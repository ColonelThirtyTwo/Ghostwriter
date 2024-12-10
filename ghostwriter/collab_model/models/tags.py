
from typing import Any

import pycrdt
from django.db import models
from django.core import checks
from django.core.exceptions import FieldDoesNotExist

from taggit.managers import TaggableManager

from ghostwriter.collab_model.models.ydocmodel import YDocModel, YBaseField
from ghostwriter.commandcenter.models import ExtraFieldSpec


class YTagsField(YBaseField):
    """
    Django view that provides a view into a `tags` map and copies those tags to Taggit.

    Stores tags in the ydoc in the `tags` top-level map, where the keys are string tag names and the
    only value is `True`. Copies the tags to a `TaggableManager` on save.
    """

    def __init__(self, stored_tags_field: str):
        """
        :param stored_tags_field: Name of the `TaggableManager` field to copy tags to.
        """
        super().__init__(
            editable=False,
            verbose_name="Tags",
        )
        self.stored_tags_field = stored_tags_field

    def check(self, **kwargs):
        checks = super().check(**kwargs)
        checks.extend(self._check_taggit_manager())
        return checks

    def _check_taggit_manager(self):
        try:
            field = self.model._meta.get_field(self.stored_tags_field)
        except FieldDoesNotExist:
            return [
                checks.Error(
                    "The YTagsField stored_tags_field references the nonexistent field '%s'." % self.stored_tags_field,
                    obj=self,
                )
            ]
        if not isinstance(field, TaggableManager):
            return [
                checks.Error(
                    "The YTagsField stored_tags_field references the field '%s' which is not a TaggableManager." % self.stored_tags_field,
                    obj=self,
                )
            ]
        return []

    def contribute_to_class(self, cls, name, **kwargs) -> None:
        super().contribute_to_class(cls, name, **kwargs)
        setattr(cls, self.attname, YTagsDescriptor(self))

    def deconstruct(self) -> Any:
        name, path, _, _ = super().deconstruct()
        args = tuple()
        if self.stored_tags_field is not None:
            args += (self.stored_tags_field,)
        return name, path, args, {}

    def _get_map(self, model_instance: YDocModel) -> pycrdt.Map:
        return model_instance.yjs_doc.get("tags", type=pycrdt.Map)

    def yjs_post_save(self, model_instance: YDocModel):
        stored_field: TaggableManager = getattr(model_instance, self.stored_tags_field)
        stored_field.set(self._get_map(model_instance).keys(), clear=True)

    def yjs_top_level_entries(self):
        return (("tags", pycrdt.Map),)



class YTagsDescriptor:
    def __init__(self, field: YTagsField):
        self.field = field

    def __get__(self, instance: YDocModel | None, cls: Any = None) -> "YTagsAccessor":
        if instance is None:
            return self
        return YTagsAccessor(self.field, instance)

    def __set__(self, instance: YDocModel | None, value: Any) -> Any:
        raise RuntimeError("Cannot set YTagsField")



class YTagsAccessor:
    def __init__(self, field: YTagsField, instance: YDocModel):
        self.yjs_map = field._get_map(instance)

    def insert(self, tag: str):
        self.yjs_map[tag] = True

    def remove(self, tag: str):
        del self.yjs_map[tag]

    def __iter__(self):
        return self.yjs_map.keys()

    def __contains__(self, tag: str) -> bool:
        return tag in self.yjs_map
