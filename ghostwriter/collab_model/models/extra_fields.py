
from typing import Any
import json

import pycrdt
from django.db import models

from ghostwriter.collab_model.models.ydocmodel import YDocModel, YBaseField
from ghostwriter.commandcenter.models import ExtraFieldSpec

class YExtraFields(YBaseField):
    """
    Django field for a YDocModel that provides more convenient access to user-defined extra fields.

    All extra fields are stored on the "extra_fields" map in the doc.
    """

    def __init__(self, extra_fields_model: type[models.Model] | None = None):
        """
        :param extra_fields_model: If set, use the extra fields for the specified model instead of the
          model that this field is on.
        """
        super().__init__(
            editable=False,
            verbose_name="Extra Fields",
        )
        self.extra_fields_model = extra_fields_model

    def contribute_to_class(self, cls, name, **kwargs) -> None:
        super().contribute_to_class(cls, name, **kwargs)
        setattr(cls, self.attname, YExtraFieldsDescriptor(self))

    def deconstruct(self) -> Any:
        name, path, _, _ = super().deconstruct()
        kwargs = {}
        if self.extra_fields_model is not None:
            kwargs["extra_fields_model"] = self.extra_fields_model
        return name, path, tuple(), kwargs

    def _extra_field_specs(self, instance: YDocModel):
        if self.extra_fields_model is not None:
            return ExtraFieldSpec.for_model(self.extra_fields_model)
        else:
            return ExtraFieldSpec.for_instance(instance)

    def _extra_fields_map(self, instance: YDocModel) -> pycrdt.Map:
        return instance.yjs_doc.get("extra_fields", type=pycrdt.Map)

    def yjs_initialize_doc(self, model_instance: YDocModel):
        """
        Sets the extra field defaults
        """
        yjs_map = self._extra_fields_map(model_instance)
        for spec in self._extra_field_specs(model_instance):
            if spec.type == "rich_text":
                # TODO: this is TinyMCE html, need to either change ExtraFieldSpec or convert the output
                xml = pycrdt.XmlFragment()
                yjs_map[spec.internal_name] = xml
                xml.children.append(spec.initial_value())
            elif spec.type == "json":
                encoded = json.dumps(spec.initial_value())
                yjs_map[spec.internal_name] = encoded
            else:
                yjs_map[spec.internal_name] = spec.initial_value()

    def yjs_top_level_entries(self):
        return (("extra_fields", pycrdt.Map),)



class YExtraFieldsDescriptor:
    def __init__(self, field: YExtraFields):
        self.field = field

    def __get__(self, instance: YDocModel | None, cls: Any = None) -> "YExtraFieldsAccessor":
        if instance is None:
            return self
        return YExtraFieldsAccessor(self.field, instance)

    def __set__(self, instance: YDocModel | None, value: Any) -> Any:
        raise RuntimeError("Cannot set YExtraFields")


class YExtraFieldsAccessor:
    """
    Accessor retreived from a `YExtraFields` field.

    Can be iterated over, which will yield `(ExtraFieldSpec, current_value)` tuples, or indexed by the field's `internal_name`.
    """
    def __init__(self, field: YExtraFields, instance: YDocModel):
        self.yjs_map = field._extra_fields_map(instance)
        self.specs = field._extra_field_specs(instance)

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
        return self.yjs_map.get(key.internal_name)

    def __setitem__(self, key: str | ExtraFieldSpec, value: Any):
        if isinstance(key, str):
            key = self.spec_for(key)
            if key is None:
                raise KeyError(key)
        self.yjs_map.set(key, value)

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
