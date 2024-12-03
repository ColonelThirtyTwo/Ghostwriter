
from typing import Any
import json

from django import template
import pycrdt

from ghostwriter.collab_model.tiptap_converters.html import TiptapToHtml

register = template.Library()

@register.filter
def yjs_xml_to_html(value: Any):
    """
    Converts a yjs XmlFragment to HTML.
    """
    if isinstance(value, pycrdt.XmlFragment):
        return str(TiptapToHtml(value))
    return str(value)

@register.filter
def yjs_type(value: Any):
    """
    Gets the name of the type of the value
    """
    return type(value).__name__

@register.filter
def yjs_try_parse_json(value: Any):
    """
    Tries to parse JSON. Returns `None` if `value` is an inappropriate type or could not be parsed
    """
    if not isinstance(value, str):
        return None
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return None
