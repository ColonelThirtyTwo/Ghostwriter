
from typing import Any

import pycrdt
from django.db import models
from django.core import checks

from ghostwriter.collab_model.models.ydocmodel import YDocModel
from ghostwriter.commandcenter.models import ExtraFieldSpec

class YExtraFields(models.Field):
    """
    Django field for a YDocModel that provides more convenient access to user-defined extra fields.

    All extra fields are stored on the "extra_fields" map in the doc.
    """

    def __init__(self):
        super().__init__(
            editable=False,
            verbose_name="Extra Fields",
        )

    def check(self, **kwargs) -> list[checks.CheckMessage]:
        return [
            *self._check_field_name(),
            *self._check_is_on_yjs_model(),
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

    def get_attname_column(self):
        attname, _column = super().get_attname_column()
        return attname, None

    def contribute_to_class(self, cls, name, **kwargs) -> None:
        super().contribute_to_class(cls, name, **kwargs)
        setattr(cls, self.attname, YExtraFieldsDescriptor(self))

    def deconstruct(self) -> Any:
        name, path, _, _ = super().deconstruct()
        return name, path, tuple(), {}


class YExtraFieldsDescriptor:
    def __init__(self, field: YExtraFields):
        self.field = field
        self.cached_accessor = None

    def __get__(self, instance: YDocModel | None, cls: Any = None) -> "YExtraFieldsAccessor":
        if instance is None:
            return self
        if self.cached_accessor is None:
            self.cached_accessor = YExtraFieldsAccessor(instance)
        return self.cached_accessor

    def __set__(self, instance: YDocModel | None, value: Any) -> Any:
        raise RuntimeError("Cannot set YExtraFields")


class YExtraFieldsAccessor:
    """
    Accessor retreived from a `YExtraFields` field.

    Can be iterated over, which will yield `(ExtraFieldSpec, current_value)` tuples, or indexed by the field's `internal_name`.
    """
    def __init__(self, instance: YDocModel):
        self.model_instance = instance
        self.specs = ExtraFieldSpec.for_instance(instance)

    def spec_for(self, internal_name: str) -> ExtraFieldSpec | None:
        """
        Gets the spec for an extra field by its internal name
        """
        return next((spec for spec in self.specs if spec.internal_name == internal_name), None)

    def __getitem__(self, key: str | ExtraFieldSpec) -> Any:
        """
        Gets the extra field value. Can be indexed by the field's internal_name or the spec itself.
        """
        if isinstance(key, str):
            key = self.spec_for(key)
            if key is None:
                raise KeyError(key)
        return self.model_instance.yjs_doc.get("extra_fields", type=pycrdt.Map).get(key.internal_name)

    def __iter__(self):
        return YExtraFieldsIterator(self)

    def __bool__(self):
        return bool(self.specs)

class YExtraFieldsIterator:
    """
    Iterator yielding tuples of the extra field's spec and its current value
    """
    def __init__(self, accessor: YExtraFieldsAccessor):
        self.accessor = accessor
        self.specs_iter = iter(self.accessor.specs)

    def __iter__(self):
        return self

    def __next__(self):
        spec = next(self.specs_iter)
        return (spec, self.accessor[spec])
