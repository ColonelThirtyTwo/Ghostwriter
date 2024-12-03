
from typing import Any

from django.views.generic.detail import DetailView
from django.contrib import messages
from django.shortcuts import redirect

from ghostwriter.api.utils import RoleBasedAccessControlMixin
from ghostwriter.collab_model.models.ydocmodel import YDocModel
from ghostwriter.commandcenter.models import ExtraFieldSpec
from ghostwriter.modules.custom_serializers import ExtraFieldsSpecSerializer

class CollabModelUpdate(RoleBasedAccessControlMixin, DetailView):
    """
    Base view for collaborative forms.

    The actual form is a React component implemented in `/frontend/src/collab_forms/forms/` - this view
    provides the data that the components use.

    Subclasses should also extend the `collab_model/update.html` template to add things like breadcrumbs.
    """

    # Narrow the model type
    model: type[YDocModel]

    # Default template. Subclasses will likely want to extend this template.
    template_name = "collab_model/update.html"

    # Route to redirect to when authorization fails
    unauthorized_redirect = "home:dashboard"

    # If set, also adds the extra fields for the model
    has_extra_fields = True

    def test_func(self):
        return self.get_object().user_can_edit(self.request.user)

    def handle_no_permission(self):
        messages.error(self.request, "You do not have the necessary permission to edit " + self.model._meta.verbose_name_plural + ".")
        return redirect(self.unauthorized_redirect)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["model_name"] = self.model._meta.model_name
        if self.has_extra_fields:
            context["extra_fields_spec_ser"] = ExtraFieldsSpecSerializer(
                ExtraFieldSpec.for_model(self.model), many=True
            ).data
        return context
