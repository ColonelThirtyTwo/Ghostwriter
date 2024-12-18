"""This contains all the WebSocket routes used by the Reporting application."""

# Django Imports
from django.urls import re_path

# Ghostwriter Libraries
from ghostwriter.collab_model.consumers import YjsUpdateConsumer
from ghostwriter.reporting import consumers, models

websocket_urlpatterns = [
    re_path(r"ws/reports/(?P<report_id>\w+)/$", consumers.ReportConsumer.as_asgi()),
    re_path(r"ws/reports/findings/(?P<finding_id>\w+)/$", consumers.ReportFindingConsumer.as_asgi()),
    re_path(r"ws/collab/observation/(?P<id>[0-9]+)/$", YjsUpdateConsumer.as_asgi(
        model=models.Observation,
        getter=lambda url_route: models.Observation.objects.get(id=url_route["kwargs"]["id"]),
    )),
    re_path(r"ws/collab/reportobservationlink/(?P<id>[0-9]+)/$", YjsUpdateConsumer.as_asgi(
        model=models.ReportObservationLink,
        getter=lambda url_route: models.ReportObservationLink.objects.get(id=url_route["kwargs"]["id"]),
    )),
]
