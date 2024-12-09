"""
Utilities for migrations that convert from old models to YDocModels.
"""

from typing import Any, Iterable
import json

import pycrdt

def migrate_rich_text(old_src: str, xmlfrag: pycrdt.XmlFragment):
    """
    Migrates TinyMCE HTML rich text to Tiptap YJS rich text
    """
    # TODO: do this for real
    xmlfrag.children.append(old_src)

def migrate_extra_fields(obj: Any, specs: Iterable[Any]):
    """
    Migrates extra fields from a JSONField named `extra_fields` to the `yjs_doc`'s `extra_fields` map.
    """
    yjs_extra_fields = obj.yjs_doc.get("extra_fields", type=pycrdt.Map)
    for spec in specs:
        value = obj.extra_fields.get(spec.internal_name, None)
        if spec.type == "rich_text":
            frag = pycrdt.XmlFragment()
            yjs_extra_fields[spec.internal_name] = frag
            migrate_rich_text(value, frag)
            continue
        elif spec.type == "json":
            value = json.dumps(value)

        yjs_extra_fields[spec.internal_name] = value

class TagMigrator:
    """
    Helper to copy tags from a Taggit relationship to the `tags` map of a `yjs_doc`.
    """
    def __init__(self, apps, app_label: str, model: str):
        """
        Loads data needed to perform the migration. Should be done outside of the update loop.
        """
        ContentType = apps.get_model("contenttypes", "ContentType")
        self.TaggedItem = apps.get_model("taggit", "TaggedItem")
        model = apps.get_model("reporting", "Observation")
        try:
            # ContentType methods aren't available so get it manually.
            # May not exist for a new database
            self.content_type_id = ContentType.objects.get(app_label=app_label, model=model).id
        except ContentType.DoesNotExist:
            self.content_type_id = None

    def migrate(self, obj: Any):
        """
        Migrates the tags of one object.
        """
        if self.content_type_id is None:
            return

        tags_map = obj.tags
        for ti in self.TaggedItem.objects.filter(
            object_id=obj.id,
            content_type=self.content_type_id,
        ).select_related("tag"):
            tags_map[ti.tag.name] = True
