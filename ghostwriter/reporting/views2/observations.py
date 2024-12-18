
import logging

from django.contrib import messages
from django.db.models import Q
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import DeleteView
from django.views.generic.list import ListView

from ghostwriter.api.utils import ForbiddenJsonResponse, RoleBasedAccessControlMixin, verify_access
from ghostwriter.collab_model.views import CollabModelUpdate
from ghostwriter.reporting.filters import ObservationFilter
from ghostwriter.reporting.models import Observation, Report

logger = logging.getLogger(__name__)


class ObservationList(RoleBasedAccessControlMixin, ListView):
    """
    Display a list of all :model:`reporting.Observation`.
    """

    model = Observation
    template_name = "reporting/observation_list.html"

    def __init__(self):
        super().__init__()
        self.autocomplete = []

    def get_queryset(self):
        search_term = ""
        observations = Observation.objects.all().order_by("stored_title")

        # Build autocomplete list
        for observation in observations:
            self.autocomplete.append(observation.title)

        search_term = self.request.GET.get("observation", "").strip()
        if search_term:
            messages.success(
                self.request,
                "Displaying search results for: {}".format(search_term),
                extra_tags="alert-success",
            )
            return observations.filter(
                Q(title__icontains=search_term) | Q(description__icontains=search_term)
            ).order_by("title")
        return observations

    def get(self, request: HttpRequest, *args, **kwarg) -> HttpResponse:
        observation_filter = ObservationFilter(request.GET, queryset=self.get_queryset())
        return render(
            request,
            "reporting/observation_list.html",
            {"filter": observation_filter, "autocomplete": self.autocomplete},
        )


class ObservationDetail(RoleBasedAccessControlMixin, DetailView):
    """
    Display an individual :model:`reporting.Observation`.

    **Template**

    :template:`reporting/observation_detail.html`
    """

    model = Observation

    def handle_no_permission(self):
        messages.error(self.request, "You do not have the necessary permission to view observations.")
        return redirect("reporting:observations")


class ObservationCreate(RoleBasedAccessControlMixin, View):
    def test_func(self):
        return Observation.user_can_create(self.request.user)

    def handle_no_permission(self):
        messages.error(self.request, "You do not have the necessary permission to create new observations.")
        return redirect("reporting:observations")

    def post(self, request: HttpRequest) -> HttpResponse:
        obj = Observation()
        obj.save(author=request.user)
        return redirect("reporting:observation_update", pk=obj.id)


class ObservationUpdate(CollabModelUpdate):
    """
    Display an individual :model:`reporting.Observation` for editing.
    """
    model = Observation
    template_name = "reporting/observation_update.html"
    unauthorized_redirect = "reporting:observations"


class ObservationDelete(RoleBasedAccessControlMixin, DeleteView):
    """
    Delete an individual instance of :model:`reporting.Observation`.

    **Context**

    ``object_type``
        String describing what is to be deleted
    ``object_to_be_deleted``
        To-be-deleted instance of :model:`reporting.Observation`
    ``cancel_link``
        Link for the form's Cancel button to return to observation list page

    **Template**

    :template:`confirm_delete.html`
    """
    model = Observation
    template_name = "confirm_delete.html"

    def test_func(self):
        return self.get_object().user_can_delete(self.request.user)

    def handle_no_permission(self):
        messages.error(self.request, "You do not have the necessary permission to delete observations.")
        return redirect(self.get_object().get_absolute_url())

    def get_success_url(self):
        messages.warning(
            self.request,
            "Observation {} was successfully deleted".format(self.get_object().title),
            extra_tags="alert-warning",
        )
        return reverse_lazy("reporting:observations")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        queryset = kwargs["object"]
        ctx["object_type"] = "observation"
        ctx["object_to_be_deleted"] = queryset.title
        ctx["cancel_link"] = reverse("reporting:observations")
        return ctx



class ObservationToReportObservationLink(View):
    """
    JSON endpoint that creates a `ReportObservationLink` from an `Observation` and binds it to a `Report`.
    """

    def post(self, *args, **kwargs):
        if not self.request.user.is_active:
            return ForbiddenJsonResponse()
        observation = get_object_or_404(Observation, id=self.kwargs["observation_pk"])

        if "report" in self.request.POST:
            try:
                report_id = int(self.request.POST["report"])
            except ValueError:
                report_id = None
        else:
            report_id = self.request.session.get("active_report", None)
        if report_id is None:
            return JsonResponse({
                "result": "error",
                "message": "Please select a report to edit in the sidebar or go to a report's dashboard to assign an observation."
            })

        report = get_object_or_404(Report, id=report_id)
        if not verify_access(self.request.user, report.project):
            return ForbiddenJsonResponse()

        report_link = observation.create_link(report)
        report_link.assigned_to = self.request.user
        report_link.save()

        logger.info(
            "Copied %s %s to %s %s (%s %s) by request of %s",
            observation.__class__.__name__,
            observation.id,
            report.__class__.__name__,
            report.id,
            report_link.__class__.__name__,
            report_link.id,
            self.request.user,
        )

        return JsonResponse({
            "result": "success",
            "message": "{} successfully added to your active report.".format(observation),
            "table_html": render_to_string(
                "snippets/report_observations_table.html",
                {"report": report},
                request=self.request
            )
        })
