from typing import Any, Callable, Generic, TypeVar

from django.db import models
from django.db.models.fields import NOT_PROVIDED
from django.core.exceptions import FieldDoesNotExist
from django.core import checks
import pycrdt._base

from ghostwriter.collab_model.models.ydocmodel import YBaseField, YDocModel

T = TypeVar("T")
V = TypeVar("V", bound=T)

# models.Field[Never, T | None]
class YField(YBaseField, Generic[T]):
    """
    Basic view into a YDoc.

    Getting or setting this field will get or set the corresponding field in the ydoc.

    The field specified here can optionally be copied to another Django model field when saving,
    so that the value is accessible to the Django ORM.
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
        checks = super().check(**kwargs)
        checks.extend(self._check_path())
        checks.extend(self._check_copy_to_field_field())
        return checks

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
                    "The YField copy_to_field references the nonexistent field '%s'." % self.copy_to_field,
                    obj=self,
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

    def yjs_pre_save(self, model_instance: YDocModel):
        self._do_copy_to_field(model_instance, False)

    def yjs_post_save(self, model_instance: YDocModel):
        self._do_copy_to_field(model_instance, True)

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

    def yjs_top_level_entries(self):
        return ((self.top_level_key(), self.top_level_type()),)


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

