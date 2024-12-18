
import logging
import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.views import View
from django.views.generic.detail import SingleObjectMixin

from ghostwriter.api.utils import ForbiddenJsonResponse, RoleBasedAccessControlMixin, verify_access
from ghostwriter.collab_model.views import CollabModelUpdate
from ghostwriter.reporting.models import Observation, Report, ReportObservationLink

logger = logging.getLogger(__name__)



class ReportObservationLinkCreateBlank(View):
    """
    Creates a blank :model:`reporting.ReportObservationLink` attached to a report.
    """
    def post(self, *args, **kwargs):
        report = get_object_or_404(Report, id=self.kwargs["pk"])
        if not verify_access(self.request.user, report.project):
            return ForbiddenJsonResponse()

        report_link = ReportObservationLink(
            report=report,
            position=ReportObservationLink.next_position_for_report(report),
            added_as_blank=True,
        )
        report_link.save(author=self.request.user)

        logger.info(
            "Added a blank observation to %s %s by request of %s",
            report.__class__.__name__,
            report.id,
            self.request.user,
        )

        message = "Successfully added a blank observation to the report."
        table_html = render_to_string(
            "snippets/report_observations_table.html",
            {"report": report},
            request=self.request
        )
        return JsonResponse({
            "result": "success",
            "message": message,
            "table_html": table_html,
        })



class ReportObservationLinkUpdate(CollabModelUpdate):
    """
    Display an individual :model:`reporting.ReportObservationLink` for editing.
    """
    model = ReportObservationLink
    template_name = "reporting/reportobservationlink_update.html"
    unauthorized_redirect = "reporting:reports"

    form_script_name = "assets/observation_form.js"



class ReportObservationLinkDelete(RoleBasedAccessControlMixin, SingleObjectMixin, View):
    """Delete an individual :model:`reporting.ReportObservationLink`."""

    model = ReportObservationLink

    def test_func(self):
        return self.get_object().user_can_delete(self.request.user)

    def handle_no_permission(self):
        return ForbiddenJsonResponse()

    def post(self, *args, **kwargs):
        observation = self.get_object()
        logger.info(
            "Deleted %s %s by request of %s",
            observation.__class__.__name__,
            observation.id,
            self.request.user,
        )

        observation.delete()

        return JsonResponse({
            "result": "success",
            "message": "Successfully deleted {observation}.".format(observation=observation),
        })



class ConvertObservation(RoleBasedAccessControlMixin, SingleObjectMixin, View):
    """
    Create a copy of an individual :model:`reporting.ReportObservationLink` and prepare
    it to be saved as a new :model:`reporting.Observation`.

    **Template**

    :template:`reporting/observation_form.html`
    """

    model = ReportObservationLink

    def test_func(self):
        return Observation.user_can_create(self.request.user) and self.get_object().user_can_view(self.request.user)

    def handle_no_permission(self):
        messages.error(self.request, "You do not have the necessary permission to create new findings.")
        return redirect(reverse("reporting:report_detail", kwargs={"pk": self.get_object().report.pk}) + "#findings")

    def post(self, *args, **kwargs):
        rol: ReportObservationLink = self.get_object()
        observation = rol.clone_to_library()
        observation.save(author=self.request.user)
        return redirect(observation.get_absolute_url())



@login_required
def ajax_update_report_observations(request: HttpRequest) -> HttpResponse:
    """
    Update the ``position`` fields of all :model:`reporting.ReportObservationLink`
    attached to an individual :model:`reporting.Report`.
    """
    if request.method != "POST" or not request.is_ajax():
        return JsonResponse({"result": "error"})

    pos = request.POST.get("positions")
    report_id = request.POST.get("report")
    order = json.loads(pos)

    report = get_object_or_404(Report, pk=report_id)
    if not verify_access(request.user, report.project):
        logger.error(
            "AJAX request submitted by user %s without access to report %s",
            request.user,
            report_id,
        )
        return JsonResponse({"result": "error"})

    logger.info(
        "Received AJAX POST to update report %s's observations in this order: %s",
        report_id,
        ", ".join(order),
    )

    for (i, observation_id) in enumerate(order):
        observation_instance = ReportObservationLink.objects.get(report=report, id=observation_id)
        if observation_instance:
            observation_instance.position = i + 1
            observation_instance.save()
        else:
            logger.error(
                "Received an observation ID, %s, that did not match an existing observation",
                observation_id,
            )
    return JsonResponse({"result": "success"})
