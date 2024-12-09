from typing import Any, Iterable
from abc import ABC

from django.db import models, transaction
from django.core import checks
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
import pycrdt._base

from ghostwriter.collab_model.yjs_dump import dump_yjs_doc


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
    db_default = b""

    def __init__(self):
        super().__init__(
            editable=False,
            serialize=False,
            verbose_name="YJS Doc"
        )

    def deconstruct(self) -> Any:
        name, path, _, _ = super().deconstruct()
        return name, path, tuple(), {}

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

    def has_default(self):
        return True

    def get_default(self):
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
                if isinstance(field, YBaseField) and field.has_default() and field.name not in kwargs:
                    kwargs[field.name] = field.get_default()

        super().__init__(**kwargs)

        self._state_vector_at_load = self.yjs_doc.get_state()

        if is_new_doc:
            # Run YFieldOnModelInit
            for field in self._meta.fields:
                if isinstance(field, YBaseField):
                    field.yjs_initialize_ydoc(self)

    def save(self, *args, author: models.Model | int | None = None, **kwargs):
        """
        Saves a YDocModel, creating a `History` entry with the specified author.

        :param author: Either a user model instance or an ID for one. Will be saved as the
          `History`'s `author`. Must be passed as a keyword argument.
        """
        for field in self._meta.fields:
            if isinstance(field, YBaseField):
                field.yjs_pre_save(self)

        if self._state_vector_at_load == self.yjs_doc.get_state():
            # No actual changes with the doc, don't save a new history entry
            return super().save(*args, **kwargs)

        update = self.yjs_doc.get_update(self._state_vector_at_load)
        with transaction.atomic():
            super().save(*args, **kwargs)

            for field in self._meta.fields:
                if isinstance(field, YBaseField):
                    field.yjs_post_save(self)

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
        top_level = dict()
        for field in self._meta.fields:
            if isinstance(field, YBaseField):
                for name, typ in field.yjs_top_level_entries():
                    top_level[name] = typ
        return dump_yjs_doc(self.yjs_doc, top_level.items())

    def user_can_edit(self, user: models.Model) -> bool:
        """
        Checks if a user has edit permission for a model.
        """
        raise NotImplementedError("YDocModel subclass must implement user_can_edit!")




class YBaseField(models.Field, ABC):
    """
    Base field for a field that forwards to the yjs doc.

    In addition to providing methods that `YDocModel` will call, `YDocModel` will emulate Django's default
    field handling by passing the fields default value to the model initializer if an existing `yjs_doc` wasn't
    provided and the field `has_default` method returns true.
    """

    def yjs_initialize_doc(self, model_instance: YDocModel):
        """
        Called when initializing a new ydoc on a YDocModel for a new instance.

        This should fill out default values or do other first-time initialization.

        This will be done in addition to the default value assignment described in the class documentation.
        """
        pass

    def yjs_pre_save(self, model_instance: YDocModel):
        """
        Called before saving the model instance.
        """
        pass

    def yjs_post_save(self, model_instance: YDocModel):
        """
        Called after saving the model instance, but before committing the transaction started in save.
        """
        pass

    def yjs_top_level_entries(self) -> Iterable[tuple[str, type[pycrdt._base.BaseType]]]:
        """
        Informs the YDocModel of top-level entries that this field uses.

        Should yield entries of arguments to `pycrdt.Doc.get(*args)`.

        Currently only used for YDocModel to know what fields to dump for debugging.
        """
        return tuple()

    def get_attname_column(self):
        # These fields forward to the yjs doc, so they don't need a real DB field.
        # This does come with some consequences though - Django will not pass the field's
        # default to the initializer of the model instance.
        attname, _column = super().get_attname_column()
        return attname, None

    def check(self, **kwargs) -> list[checks.CheckMessage]:
        return [
            *self._check_field_name(),
            *self.check_is_on_yjs_model(),
        ]

    def check_is_on_yjs_model(self) -> list[checks.CheckMessage]:
        if not issubclass(self.model, YDocModel):
            return [
                checks.Error(
                    "The YField must be on a YDocModel",
                    obj=self,
                    id="pycrdt_model.E005"
                )
            ]
        return []
