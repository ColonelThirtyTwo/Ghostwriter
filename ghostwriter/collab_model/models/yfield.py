from typing import Any, Generic, TypeVar

from django.db.models.fields import NOT_PROVIDED
from django.core.exceptions import FieldDoesNotExist
from django.core import checks
from django.template.loader import render_to_string
from django.utils.safestring import SafeString
import pycrdt._base

from ghostwriter.collab_model.tiptap_converters.html import TiptapToHtml
from ghostwriter.collab_model.models.ydocmodel import BaseHistoryObserver, YBaseField, YDocModel

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
        yjs_name: str,
        yjs_type: type[T],
        *,
        copy_to_field: str | None = None,
        verbose_name: str | None = None,
        name: str | None = None,
        default = NOT_PROVIDED,
    ):
        """
        :param yjs_name: Name in the ydoc to access. If `yjs_type` is a pycrdt type, the field will access this from the ydoc top level.
          Otherwise, the field will access from the "plain_fields" map.
        :param yjs_type: Type of the field.
        :param copy_to_field: If set, assigns another field with a copy of the value in the doc when assigning this field or saving.
        """
        super().__init__(
            editable=False,
            null=True,
            blank=True,
            verbose_name=verbose_name,
            name=name,
            default=default,
        )
        self.yjs_name = yjs_name
        self.yjs_type = yjs_type
        self.copy_to_field = copy_to_field

    def check(self, **kwargs) -> list[checks.CheckMessage]:
        checks = super().check(**kwargs)
        checks.extend(self._check_copy_to_field_field())
        return checks

    def _check_copy_to_field_field(self) -> list[checks.CheckMessage]:
        if self.copy_to_field is None:
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
        if issubclass(self.yjs_type, pycrdt._base.BaseType):
            return instance.yjs_doc.get(self.yjs_name, type=self.yjs_type)
        return instance.yjs_doc.get("plain_fields", type=pycrdt.Map).get(self.yjs_name)

    def _set_on_model(self, instance: YDocModel, value: T):
        if issubclass(self.yjs_type, pycrdt._base.BaseType):
            raise RuntimeError("Cannot set {} directly".format(self.yjs_type))
        instance.yjs_doc.get("plain_fields", type=pycrdt.Map)[self.yjs_name] = value

    def yjs_pre_save(self, model_instance: YDocModel):
        if self.copy_to_field is None:
            return
        value = self._get_from_model(model_instance)
        setattr(model_instance, self.copy_to_field, value)

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
        args = (self.yjs_name, self.yjs_type)
        return name, path, args, kwargs

    def yjs_top_level_entries(self):
        if issubclass(self.yjs_type, pycrdt._base.BaseType):
            return ((self.yjs_name, self.yjs_type),)
        return (("plain_fields", pycrdt.Map),)

    def yjs_observe_for_history(self, document: pycrdt.Doc) -> BaseHistoryObserver | None:
        if issubclass(self.yjs_type, pycrdt.XmlFragment):
            return XmlFragmentHistoryObserver(
                self.verbose_name,
                document.get(self.yjs_name, type=pycrdt.XmlFragment),
            )
        elif issubclass(self.yjs_type, pycrdt._base.BaseType):
            return None
        else:
            return SimpleHistoryObserver(
                self.verbose_name,
                document.get("plain_fields", type=pycrdt.Map),
                self.yjs_name,
            )


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
        self.field._set_on_model(instance, value)
        return value


class SimpleHistoryObserver(BaseHistoryObserver):
    def __init__(self, verbose_name: str, map: pycrdt.Map, field: str):
        self.verbose_name = verbose_name
        self.field = field
        self.map = map
        self.changed = False
        self.old_value = self.map.get(field)
        self.new_value = None

        def callback(ev: pycrdt.MapEvent):
            nonlocal self
            if self.field in ev.keys:
                delta = ev.keys[self.field]
                self.changed = True
                self.new_value = delta.get("newValue")

        self.subscription = self.map.observe(callback)

    def render_and_reset(self) -> str | None:
        if not self.changed:
            return None
        if not self.old_value and not self.new_value:
            # Change won't be visible so don't bother.
            # For example, changing from None to the empty string in defaults.
            return None

        rendered = render_to_string("collab_model/history_delta/simple.html", {
            "verbose_name": self.verbose_name,
            "old_value": self.old_value,
            "new_value": self.new_value,
        })

        self.changed = False
        self.old_value = self.new_value
        self.new_value = None

        return rendered

    def unobserve(self):
        self.map.unobserve(self.subscription)

class XmlFragmentHistoryObserver(BaseHistoryObserver):
    def __init__(self, verbose_name: str, fragment: pycrdt.XmlFragment):
        self.verbose_name = verbose_name
        self.fragment = fragment
        self.converter = TiptapToHtml(self.fragment)
        self.changed = False

        def callback(evs: list[pycrdt.XmlEvent]):
            nonlocal self
            for ev in evs:
                self.changed = True
                if isinstance(ev.target, pycrdt.XmlText):
                    self.converter.apply_text_event(ev.path, ev.delta)
                else:
                    self.converter.apply_element_event(ev.path, ev.delta, ev.keys)

        self.subscription = self.fragment.observe_deep(callback)

    def render_and_reset(self) -> SafeString | None:
        if not self.changed:
            return None

        rendered = render_to_string("collab_model/history_delta/rich_text.html", {
            "verbose_name": self.verbose_name,
            "converter": self.converter,
        })

        self.converter = TiptapToHtml(self.fragment)
        self.changed = False

        return rendered

    def unobserve(self):
        self.fragment.unobserve(self.subscription)
