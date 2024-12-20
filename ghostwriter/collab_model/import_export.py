
from ghostwriter.collab_model.models.ydocmodel import YBaseField
from import_export.resources import ModelResource

class YModelResource(ModelResource):
    """
    django-import-export ModelResource that provides fields and widgets for YDocModel fields
    """

    @classmethod
    def field_from_django_field(cls, field_name, django_field, readonly):
        if isinstance(django_field, YBaseField):
            field = django_field.yjs_import_export_field(field_name, readonly)
            if field is not None:
                return field
        return super().field_from_django_field(field_name, django_field, readonly)
