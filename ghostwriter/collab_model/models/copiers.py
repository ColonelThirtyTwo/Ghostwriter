
from ghostwriter.collab_model.models.ydocmodel import YDocModel, YField
import pycrdt


def copy_tags(_field: YField, instance: YDocModel, value: pycrdt.Map):
    """
    Copies tags from a `YMap` to the `stored_tags` field of the instance, which should be a `TaggableManager`.

    For use as an argument to `copy_field` in `YField`.
    """
    instance.stored_tags.set(
        (key for key in value.keys()),
        clear=True,
    )

