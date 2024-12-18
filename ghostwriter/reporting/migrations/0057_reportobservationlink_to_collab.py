
from django.db import migrations, models
import pycrdt._xml

from ghostwriter.reporting.models import Observation
import ghostwriter.collab_model.models.extra_fields
import ghostwriter.collab_model.models.tags
import ghostwriter.collab_model.models.ydocmodel
import ghostwriter.collab_model.models.yfield
from ghostwriter.modules.collab_migration_util import TagMigrator, migrate_extra_fields, migrate_rich_text


def migrate_into_ydoc(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    ReportObservationLink = apps.get_model("reporting", "ReportObservationLink")
    ExtraFieldSpec = apps.get_model("commandcenter", "ExtraFieldSpec")
    extra_field_specs = ExtraFieldSpec.objects.using(db_alias).filter(target_model=ReportObservationLink._meta.label)
    tag_migrator = TagMigrator(apps, db_alias, "reporting", "ReportObservationLink")

    for obs in ReportObservationLink.objects.using(db_alias).all().select_for_update(of=("self",)):
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
        ("reporting", "0056_observation_to_collab"),
    ]

    operations = [
        # Rename and alter old fields
        migrations.RenameField(
            model_name="reportobservationlink",
            old_name="title",
            new_name="stored_title",
        ),
        migrations.AlterField(
            model_name="reportobservationlink",
            name="stored_title",
            field=models.TextField(blank=True, editable=False, verbose_name="Title"),
        ),
        migrations.RenameField(
            model_name="reportobservationlink",
            old_name="tags",
            new_name="stored_tags",
        ),

        # Add new fields
        migrations.AddField(
            model_name="reportobservationlink",
            name="yjs_doc",
            field=ghostwriter.collab_model.models.YDocField(),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="reportobservationlink",
            name="title_new",
            field=ghostwriter.collab_model.models.YField(
                "title", str, copy_to_field="stored_title", verbose_name="Title", default="Unnamed Observation"
            ),
        ),
        migrations.AddField(
            model_name="reportobservationlink",
            name="description_new",
            field=ghostwriter.collab_model.models.YField(
                "description", pycrdt._xml.XmlFragment, verbose_name="Description"
            ),
        ),
        migrations.AddField(
            model_name="reportobservationlink",
            name="tags_new",
            field=ghostwriter.collab_model.models.YTagsField(
                "stored_tags",
            ),
        ),

        # Migrate data
        migrations.RunPython(migrate_into_ydoc),

        # Remove old fields
        migrations.RemoveField(
            model_name="reportobservationlink",
            name="description",
        ),
        migrations.RemoveField(
            model_name="reportobservationlink",
            name="extra_fields",
        ),

        # Add new extra fields accessor
        migrations.AddField(
            model_name="reportobservationlink",
            name="extra_fields",
            field=ghostwriter.collab_model.models.YExtraFields(extra_fields_model=Observation),
        ),

        # Rename new fields to correct name.
        # These are virtual fields that don't correspond to a column, so only do it in Django's state
        migrations.SeparateDatabaseAndState(database_operations=[], state_operations=[
            migrations.RenameField(
                model_name="reportobservationlink",
                old_name="title_new",
                new_name="title",
            ),
            migrations.RenameField(
                model_name="reportobservationlink",
                old_name="description_new",
                new_name="description",
            ),
            migrations.RenameField(
                model_name="reportobservationlink",
                old_name="tags_new",
                new_name="tags",
            ),
        ]),
    ]
