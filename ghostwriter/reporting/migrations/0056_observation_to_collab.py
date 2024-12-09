
from django.db import migrations, models
import pycrdt._map
import pycrdt._xml

import ghostwriter.collab_model.models.ydocmodel
import ghostwriter.collab_model.models.copiers
import ghostwriter.collab_model.models.extra_fields
from ghostwriter.modules.collab_migration_util import TagMigrator, migrate_extra_fields, migrate_rich_text


def migrate_into_ydoc(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    Observation = apps.get_model("reporting", "Observation")
    ExtraFieldSpec = apps.get_model("commandcenter", "ExtraFieldSpec")
    extra_field_specs = ExtraFieldSpec.objects.filter(target_model=Observation._meta.label)
    tag_migrator = TagMigrator(apps, "reporting", "Observation")

    for obs in Observation.objects.using(db_alias).all().select_for_update():
        obs.title_new = obs.stored_title

        migrate_rich_text(obs.description, obs.description_new)
        migrate_extra_fields(obs, extra_field_specs)
        tag_migrator.migrate(obs)
        obs.save()

class Migration(migrations.Migration):
    dependencies = [
        (
            "taggit",
            "0006_rename_taggeditem_content_type_object_id_taggit_tagg_content_8fc721_idx",
        ),
        ("reporting", "0055_auto_20240924_2108"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="observation",
            options={
                "ordering": ["stored_title"],
                "verbose_name": "Observation",
                "verbose_name_plural": "Observations",
            },
        ),

        # Rename and alter old fields
        migrations.RenameField(
            model_name="observation",
            old_name="title",
            new_name="stored_title",
        ),
        migrations.AlterField(
            model_name="observation",
            name="stored_title",
            field=models.TextField(blank=True, editable=False, verbose_name="Title"),
        ),
        migrations.RenameField(
            model_name="observation",
            old_name="tags",
            new_name="stored_tags",
        ),

        # Add new fields
        migrations.AddField(
            model_name="observation",
            name="yjs_doc",
            field=ghostwriter.collab_model.models.ydocmodel.YDocField(default=pycrdt.Doc(client_id=0)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="observation",
            name="title_new",
            field=ghostwriter.collab_model.models.ydocmodel.YField(
                ["plain_fields", "title"], str, copy_to_field="stored_title", verbose_name="Title", default="Unnamed Observation"
            ),
        ),
        migrations.AddField(
            model_name="observation",
            name="description_new",
            field=ghostwriter.collab_model.models.ydocmodel.YField(
                "description", pycrdt._xml.XmlFragment, verbose_name="Description"
            ),
        ),
        migrations.AddField(
            model_name="observation",
            name="tags_new",
            field=ghostwriter.collab_model.models.ydocmodel.YField(
                "tags",
                pycrdt._map.Map,
                copy_to_field=ghostwriter.collab_model.models.copiers.copy_tags,
                copy_to_field_after_save=True,
                verbose_name="Tags",
            ),
        ),

        # Migrate data
        migrations.RunPython(migrate_into_ydoc),

        # Remove old fields
        migrations.RemoveField(
            model_name="observation",
            name="description",
        ),
        migrations.RemoveField(
            model_name="observation",
            name="extra_fields",
        ),

        # Add new extra fields accessor
        migrations.AddField(
            model_name="observation",
            name="extra_fields",
            field=ghostwriter.collab_model.models.extra_fields.YExtraFields(),
        ),

        # Rename new fields to correct name.
        # These are virtual fields that don't correspond to a column, so only do it in Django's state
        migrations.SeparateDatabaseAndState(database_operations=[], state_operations=[
            migrations.RenameField(
                model_name="observation",
                old_name="title_new",
                new_name="title",
            ),
            migrations.RenameField(
                model_name="observation",
                old_name="description_new",
                new_name="description",
            ),
            migrations.RenameField(
                model_name="observation",
                old_name="tags_new",
                new_name="tags",
            ),
        ]),
    ]
