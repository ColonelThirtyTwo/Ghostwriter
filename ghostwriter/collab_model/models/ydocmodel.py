from typing import Any, Callable, Generic, TypeVar

from django.db import models, transaction
from django.db.models.fields import NOT_PROVIDED
from django.core.exceptions import FieldDoesNotExist
from django.core import checks
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from ghostwriter.collab_model.yjs_dump import dump_yjs_doc
import pycrdt._base


T = TypeVar("T")
V = TypeVar("V", bound=T)


class History(models.Model):
    """
    Change of a `YDocModel`.

    `YDocModel.save` will create an instance of this every time it saves with changes. It contains the YJS update
    containing the delta between the previous History instance (or an empty document for the first instance) to
    the current inststance, as well as the user who submitted it and the time it was submitted.
    """

    # IDs must be monotonically increasing, and is used to order history on an individual model.
    id = models.BigAutoField(primary_key=True)
    target_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    target_id = models.PositiveIntegerField()
    target = GenericForeignKey("target_type", "target_id")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="+")
    time = models.DateTimeField(auto_now_add=True)
    update = models.BinaryField()

    class Meta:
        indexes = [
            models.Index(fields=["target_type", "target_id", "id"]),
        ]

    @classmethod
    def for_object(cls, obj: "YDocModel", recent_first: bool = False):
        """
        Gets a `QuerySet` of history entries for an object.

        The history is ordered from first to last, unless `recent_first` is set which will
        reverse the order.

        It's recommended to bound time based on the `id` field since its monotonically increasing and
        has no conflicts.
        """
        return cls.objects.filter(
            target_type=ContentType.objects.get_for_model(obj),
            target_id=obj.pk,
        ).order_by("-id" if recent_first else "id")

    @classmethod
    def replay(
        cls, obj: "YDocModel", until_id: int, until_id_inclusive: bool = True
    ) -> pycrdt.Doc:
        """
        Gets a `pycrdt.Doc` with the state at the time of the last update at or until `until_id`.

        If `until_id_inclusive` is True, the update at `until_id` is included, otherwise it is excluded.
        """
        doc = pycrdt.Doc()
        with doc.transaction():
            qs = cls.for_object(obj)
            if until_id_inclusive:
                qs = qs.filter(id__lte=until_id)
            else:
                qs = qs.filter(id__lt=until_id)
            for history_entry in qs:
                doc.apply_update(history_entry.update)
        return doc

    @classmethod
    def replay_until(
        cls, obj: "YDocModel", history_id: int
    ) -> tuple[pycrdt.Doc, "History"] | None:
        """
        Gets the history entry with the specified ID and also the doc as it appeared up to that point, excluding the specified update.

        That is, the returned doc will be the state of the doc before the `history_id` update.

        You can add observers to the returned document then apply the returned `History.update`, and the observers will be called
        with the changes introduced in this history instance.

        If there is no `History` with the passed in `history_id`, returns None.
        """
        doc = pycrdt.Doc()
        last_entry = None
        with doc.transaction():
            for history_entry in cls.for_object(obj).filter(id__lte=history_id):
                if last_entry is not None:
                    doc.apply_update(last_entry.update)
                last_entry = history_entry
        if last_entry is None or last_entry.id != history_id:
            return None
        return (doc, last_entry)



# models.Field[pycrdt.Doc, pycrdt.Doc]
class YDocField(models.Field):
    """
    Django field for a yjs document.

    When retreived from this field, the document's client ID will be set to zero.
    """
    # Based off of Django's BinaryField

    description = "YJS Document"
    empty_values = [None]

    def __init__(self, *args, **kwargs):
        kwargs["editable"] = False
        kwargs["serialize"] = False
        super().__init__(*args, **kwargs)

    def deconstruct(self) -> Any:
        name, path, args, kwargs = super().deconstruct()
        kwargs.pop("editable")
        kwargs.pop("serialize")
        return name, path, args, kwargs

    def get_internal_type(self) -> str:
        return "BinaryField"

    def from_db_value(
        self, value, _expression, _connection
    ):
        if value is None:
            return None
        doc = pycrdt.Doc(client_id=0)
        if value != b"":
            doc.apply_update(bytes(value))
        return doc

    def get_prep_value(self, value):
        if value is None:
            return None
        return value.get_update()

    def get_db_prep_value(self, value, connection, prepared=False):
        value = super().get_db_prep_value(value, connection, prepared)
        if value is not None:
            return connection.Database.Binary(value)
        return value

    def get_default(self):
        if self.has_default():
            if callable(self.default):
                return self.default()
            return self.default
        return pycrdt.Doc(client_id=0)



class YDocModel(models.Model):
    """
    Base class for models that contains a YDoc.

    Adds `yjs_doc` field, and copies `YField`s to their configured `copy_to_field` when saving.

    Ghostwriter conventions:

    * Rich text hardcoded fields are stored directly on the ydoc.
    * Non-rich-text hardcoded fields are stored in the `plain_fields` map.
    * User-defined extra fields are stored in the `extra_fields` map.
    """

    class Meta:
        abstract = True

    yjs_doc: pycrdt.Doc = YDocField()

    _state_vector_at_load: bytes | None

    def __init__(self, *args, **kwargs):
        # We have to do a bunch of initialization here since Django's data model does not work well with YJS.
        # Django does not pass defaults for YFields, as they don't have a backing column, and defaults for things
        # like extra fields are a bit more complicated since they involve nested values.

        # Convert args tuple into kwargs slots since it's much easier to keep track of
        for i, val in enumerate(args):
            try:
                field = self._meta.concrete_fields[i]
            except IndexError as e:
                raise ValueError("Too many arguments to YDocModel init") from e
            kwargs[field.name] = val

        # If a yjs_doc isn't provided, this is a new model, so initialize the defaults
        is_new_doc = "yjs_doc" not in kwargs

        if is_new_doc:
            # Initialize YField defaults, since Django won't do it for us
            for field in self._meta.fields:
                if isinstance(field, YField) and field.has_default() and field.name not in kwargs:
                    kwargs[field.name] = field.get_default()

        super().__init__(**kwargs)

        self._state_vector_at_load = self.yjs_doc.get_state()

        if is_new_doc:
            # Run YFieldOnModelInit
            for field in self._meta.fields:
                if isinstance(field, YFieldOnModelInit):
                    field.initialize_ydoc(self)

    def _copy_y_fields(self, is_after_save: bool):
        """
        Copies fields from the ydoc to the Django field, as configured by its `YField`s.

        `save` does this before saving, so you shouldn't need to do this manually.
        """
        for field in self._meta.fields:
            if isinstance(field, YField):
                field._do_copy_to_field(self, is_after_save)

    def save(self, *args, author: models.Model | int | None = None, **kwargs):
        self._copy_y_fields(False)

        if self._state_vector_at_load == self.yjs_doc.get_state():
            # No actual changes with the doc, don't save a new history entry
            return super().save(*args, **kwargs)

        update = self.yjs_doc.get_update(self._state_vector_at_load)
        with transaction.atomic():
            super().save(*args, **kwargs)
            self._copy_y_fields(True)

            history = History(target=self, update=update)
            if isinstance(author, int):
                history.author_id = author
            else:
                history.author = author
            history.save()
        return super().save(*args, **kwargs)

    def dump(self) -> str:
        """
        Returns a human-readable representation of the ydoc, for debugging
        """
        top_level_keys = dict((field.top_level_key(), field.top_level_type()) for field in self._meta.fields if isinstance(field, YField))
        top_level_keys.setdefault("extra_fields", pycrdt.Map)
        return dump_yjs_doc(self.yjs_doc, top_level_keys.items())

    def user_can_edit(self, user: models.Model) -> bool:
        """
        Checks if a user has edit permission for a model.
        """
        raise NotImplementedError("YDocModel subclass must implement user_can_edit!")



def _resolve_path(doc: pycrdt.Doc, doc_value_path: str | list[str | int], typ: type[T], default: T | None = None) -> T | None:
    """
    Gets a possibly nested value from a YDoc via a path.

    If `doc_value_path` is a string, returns `doc.get(doc_value_path, type=typ)`.
    Otherwise `doc_value_path` must be a list whose first item is a string and remaining items strings or
    integers. This will traverse the document, indexing each element in the list order.
    """
    if isinstance(doc_value_path, str):
        return doc.get(doc_value_path, type=typ)

    if not doc_value_path:
        raise ValueError("Empty path")

    first = doc_value_path[0]
    if not isinstance(first, str):
        raise ValueError("doc_value_path must start with a string")

    if len(doc_value_path) == 1:
        return doc.get(first, type=typ)

    value: pycrdt.Map | pycrdt.Array = doc.get(
        first,
        type=pycrdt.Map if isinstance(doc_value_path[0], str) else pycrdt.Array,
    )
    for index in doc_value_path[1:]:
        try:
            value = value[index]
        except (KeyError, IndexError):
            return default
    return value


class YFieldOnModelInit:
    """
    Interface for fields that should help initialize the ydoc on a new model.
    """

    def initialize_ydoc(self, model_instance: YDocModel):
        """
        Called on each field extending this class after initializing a new instance of a YDocModel.
        This should fill out default values or do other first-time initialization prepwork.
        """
        pass


# models.Field[Never, T | None]
class YField(models.Field, YFieldOnModelInit, Generic[T]):
    """
    Field that is a view into a YDoc value.

    Getting or setting this field will get or set the corresponding field in the ydoc.
    """

    def __init__(
        self,
        y_value_path: str | list[str | int],
        yjs_type: type[T],
        *,
        copy_to_field: str | Callable[[models.Model, T], None] | None = None,
        copy_to_field_after_save: bool = False,
        to_field_value: Callable[[T], Any] | None = None,
        verbose_name: str | None = None,
        name: str | None = None,
        default = NOT_PROVIDED,
    ):
        """
        :param y_value_path: Path to the item in the ydoc to get. If a string or one-element list, gets a top level element of the
          doc with type `yjs_type`. Otherwise, gets a value nested in a map or array by indexing with each list item in order.
        :param yjs_type: Type of the field, used to get the item from the top level of the doc.
        :param copy_to_field: If a string fieldname, assigns another field with a copy of the value in the doc when assigning this field or saving.
          If a function, calls it instead with the YField, model instance, and value instead, to perform assignment.
        :param copy_to_field_after_save: Perform the `copy_to_field` action after saving rather than just before. Needed for foreign key fields that require
          the model to have a PK first.
        :param to_field_value: If `copy_to_field` is a string, called to transform the value before `copy_to_field` assignment. Otherwise ignored.
        """
        super().__init__(
            editable=False,
            null=True,
            blank=True,
            verbose_name=verbose_name,
            name=name,
            default=default,
        )
        self.y_value_path = y_value_path
        self.yjs_type = yjs_type
        self.copy_to_field = copy_to_field
        self.copy_to_field_after_save = copy_to_field_after_save
        self.to_field_value = to_field_value

    def check(self, **kwargs) -> list[checks.CheckMessage]:
        return [
            *self._check_field_name(),
            *self._check_is_on_yjs_model(),
            *self._check_path(),
            *self._check_copy_to_field_field(),
        ]

    def _check_is_on_yjs_model(self) -> list[checks.CheckMessage]:
        if not issubclass(self.model, YDocModel):
            return [
                checks.Error(
                    "The YField must be on a YDocModel",
                    obj=self,
                    id="pycrdt_model.E005"
                )
            ]
        return []

    def _check_path(self) -> list[checks.CheckMessage]:
        if isinstance(self.y_value_path, str):
            return []
        if len(self.y_value_path) <= 0:
            return [
                checks.Error(
                    "The YField path is empty",
                    obj=self,
                    id="pycrdt_model.E002"
                )
            ]
        if not isinstance(self.y_value_path[0], str):
            return [
                checks.Error(
                    "The first element of the YField path must be a string",
                    obj=self,
                    id="pycrdt_model.E003"
                )
            ]
        return []

    def _check_copy_to_field_field(self) -> list[checks.CheckMessage]:
        if self.copy_to_field is None or not isinstance(self.copy_to_field, str):
            return []
        try:
            self.model._meta.get_field(self.copy_to_field)
        except FieldDoesNotExist:
            return [
                checks.Error(
                    "The YField copy_to_field reference the nonexistent field '%s'." % self.copy_to_field,
                    obj=self,
                    id="pycrdt_model.E004",
                )
            ]
        return []

    def _get_from_model(self, instance: YDocModel) -> T | None:
        """
        Gets the field value from a model instance's ydoc.
        """
        return _resolve_path(instance.yjs_doc, self.y_value_path, self.yjs_type)

    def _do_copy_to_field(self, instance: YDocModel, is_after_save: bool):
        if self.copy_to_field is None:
            return
        if self.copy_to_field_after_save is not is_after_save:
            return

        value = self._get_from_model(instance)

        if isinstance(self.copy_to_field, str):
            if self.to_field_value is not None:
                value = self.to_field_value(value)
            else:
                value = _yjs_to_db(value)
            setattr(instance, self.copy_to_field, value)
        else:
            self.copy_to_field(self, instance, value)

    def get_attname_column(self):
        attname, _column = super().get_attname_column()
        return attname, None

    def contribute_to_class(self, cls, name, **kwargs) -> None:
        super().contribute_to_class(cls, name, **kwargs)
        setattr(cls, self.attname, YFieldDescriptor(self))

    def deconstruct(self):
        name, path, _, kwargs = super().deconstruct()
        kwargs.pop("editable")
        kwargs.pop("null")
        kwargs.pop("blank")
        if self.copy_to_field is not None:
            kwargs["copy_to_field"] = self.copy_to_field
            if self.copy_to_field_after_save:
                kwargs["copy_to_field_after_save"] = self.copy_to_field_after_save
        args = (self.y_value_path,self.yjs_type)
        return name, path, args, kwargs

    def top_level_type(self):
        if isinstance(self.y_value_path, str) or len(self.y_value_path) == 1:
            return self.yjs_type
        if isinstance(self.y_value_path[0], str):
            return pycrdt.Map
        return pycrdt.Array

    def top_level_key(self):
        if isinstance(self.y_value_path, str):
            return self.y_value_path
        return self.y_value_path[0]


class YFieldDescriptor(Generic[T]):
    """
    Descriptor used with YField, getting the corresponding field in the YDoc.
    """
    def __init__(self, field: YField[T]):
        self.field = field

    def __get__(self, instance: YDocModel | None, cls: Any = None) -> T | None:
        if instance is None:
            return self
        return self.field._get_from_model(instance)

    def __set__(self, instance: YDocModel | None, value: V) -> V:
        if value is YFIELD_DEFAULT:
            return value
        if isinstance(value, pycrdt._base.BaseType):
            raise RuntimeError("Cannot set a Pycrdt type directly, go through the doc instead")

        doc = instance.yjs_doc
        if isinstance(self.field.y_value_path, str):
            doc[self.field.y_value_path] = value
        elif len(self.field.y_value_path) == 1:
            doc[self.field.y_value_path[0]] = value
        else:
            base = _resolve_path(
                doc,
                self.field.y_value_path[:-1],
                pycrdt.Map if isinstance(self.field.y_value_path[-1], str) else pycrdt.Array,
                None
            )
            base[self.field.y_value_path[-1]] = value

        self.field._do_copy_to_field(instance, False)

        return value


def _yjs_to_db(value: Any) -> Any:
    """
    Helper: converts a value from a YDoc to a value for a Django field.
    """
    if isinstance(value, pycrdt.XmlFragment) or isinstance(value, pycrdt.Text):
        return str(value)
    return value

class YFIELD_DEFAULT:
    pass
