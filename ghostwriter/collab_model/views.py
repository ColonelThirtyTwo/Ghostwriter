
from typing import Any
from abc import ABC

from django.views.generic.detail import DetailView
from django.contrib import messages
from django.shortcuts import redirect
from django.core.paginator import Paginator

from ghostwriter.api.utils import RoleBasedAccessControlMixin
from ghostwriter.collab_model.models.ydocmodel import History, YDocModel
from ghostwriter.commandcenter.models import ExtraFieldSpec
from ghostwriter.modules.custom_serializers import ExtraFieldsSpecSerializer

class CollabModelUpdate(RoleBasedAccessControlMixin, DetailView, ABC):
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

class HistoryListView(RoleBasedAccessControlMixin, DetailView, ABC):
    # Narrow the model type
    model: type[YDocModel]

    template_name = "collab_model/history_list.html"

    # Route to redirect to when authorization fails
    unauthorized_redirect = "home:dashboard"

    def __init__(self, model: type[YDocModel] | None = None, template_name: str | None = None, unauthorized_redirect: str | None = None):
        if model is not None:
            self.model = model
        if template_name is not None:
            self.template_name = template_name
        if unauthorized_redirect is not None:
            self.unauthorized_redirect = unauthorized_redirect

    def handle_no_permission(self):
        messages.error(self.request, "You do not have the necessary permission to view " + self.model._meta.verbose_name_plural + ".")
        return redirect(self.unauthorized_redirect)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        object = self.get_object()

        history_qs = History.for_object(object, recent_first=True)
        history_paginator = Paginator(history_qs, 20, allow_empty_first_page=True)
        history_page = history_paginator.get_page(self.request.GET.get("page"))
        context["pagination_range"] = history_paginator.get_elided_page_range(history_page.number)
        context["page"] = history_page

        if not history_page:
            context["history_deltas"] = []
            return context

        doc = History.replay(object, history_page[-1].id, until_id_inclusive=False)
        history_deltas = []
        observers = [field.yjs_observe_for_history(doc) for field in self.model.yfields()]
        try:
            history_instance: History
            for history_instance in reversed(history_page):
                doc.apply_update(bytes(history_instance.update))
                differences = list(filter(
                    lambda v: v is not None,
                    (observer.render_and_reset() for observer in observers)
                ))
                history_deltas.append((history_instance, differences))
        finally:
            for obs in observers:
                obs.unobserve()

        history_deltas.reverse()
        context["history_deltas"] = history_deltas
        return context
