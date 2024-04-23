
from datetime import datetime
import io
from typing import Any, Iterable
import re
from venv import logger

from django.forms import ValidationError
import jinja2
from django.db.models import Model

from ghostwriter.commandcenter.models import CompanyInformation, ExtraFieldSpec
from ghostwriter.modules.reportwriter import jinja_funcs, prepare_jinja2_env


class ExportBase:
    """
    Base class for exporting things.

    Subclasses should prove a `run` method, and optionally `serialize_object`.

    Users should instantiate the object then call `run` to generate a `BytesIO` containing the exported
    file. Instances should not be re-used.

    Fields:

    * `input_object`: The object passed into `__init__`, unchanged
    * `data`: The object passed into `__init__` ran through `serialize_object`, usually a dict, for passing into a Jinja env
    * `jinja_env`: Jinja2 environment for templating
    """
    input_object: Any
    data: Any
    jinja_env: jinja2.Environment
    jinja_undefined_variables: set[str] | None
    extra_fields_spec_cache: dict[str, Iterable[ExtraFieldSpec]]

    def __init__(self, input_object: Any, *, is_raw=False, jinja_debug=False):
        if jinja_debug:
            self.jinja_env, self.jinja_undefined_variables = prepare_jinja2_env(debug=True)
        else:
            self.jinja_env = prepare_jinja2_env(debug=False)
            self.jinja_undefined_variables = None
        if is_raw:
            self.input_object = None
            self.data = input_object
        else:
            self.input_object = input_object
            self.data = self.serialize_object(input_object)
        self.extra_fields_spec_cache = {}

    def serialize_object(self, object: Any) -> Any:
        """
        Called by __init__ to serialize the input object to a format appropriate for use in a jinja environment.

        By default does nothing and returns `object` unchanged.
        """
        return object

    def extra_field_specs_for(self, model: Model) -> Iterable[ExtraFieldSpec]:
        """
        Gets (and caches) the set of extra fields for a model class.
        """
        label = model._meta.label
        if label in self.extra_fields_spec_cache:
            return self.extra_fields_spec_cache[label]
        specs = ExtraFieldSpec.objects.filter(target_model=label)
        self.extra_fields_spec_cache[label] = specs
        return specs

    def preprocess_rich_text(self, text: str, template_vars: Any):
        """
        Does jinja and `{{.item}}` substitutions on rich text, in preparation for feeding into the
        `BaseHtmlToOOXML` subclass.
        """

        if not text:
            return ""

        # Replace old `{{.item}}`` syntax with jinja templates or elements to replace
        def replace_old_tag(match: re.Match):
            contents = match.group(1).strip()
            # These will be swapped out when parsing the HTML
            if contents.startswith("ref "):
                return jinja_funcs.ref(contents[4:].strip())
            elif contents == "caption":
                return jinja_funcs.caption("")
            elif contents.startswith("caption "):
                return jinja_funcs.caption(contents[8:].strip())
            return "{{ _old_dot_vars[" + repr(contents.strip()) + "]}}"

        text_old_dot_subbed = re.sub(r"\{\{\.(.*?)\}\}", replace_old_tag, text)

        text_pagebrea_subbed = text_old_dot_subbed.replace(
            "<p><!-- pagebreak --></p>", '<br data-gw-pagebreak="true" />'
        )

        # Run template
        template = self.jinja_env.from_string(text_pagebrea_subbed)
        text_rendered = template.render(template_vars)

        # Filter out XML-incompatible characters
        text_char_filtered = "".join(c for c in text_rendered if _valid_xml_char_ordinal(c))
        return text_char_filtered

    def run(self) -> io.BytesIO:
        raise NotImplementedError()

    @classmethod
    def mime_type(cls) -> str:
        raise NotImplementedError()

    @classmethod
    def extension(cls) -> str:
        raise NotImplementedError()

    @classmethod
    def generate_lint_data(cls):
        raise NotImplementedError()

    @classmethod
    def check_filename_template(cls, filename_template: str):
        exporter = cls(
            cls.generate_lint_data(),
            is_raw=True,
            jinja_debug=True,
        )
        try:
            exporter.render_filename(filename_template, ext="test")
        except jinja2.TemplateError as e:
            raise ValidationError(str(e)) from e
        except TypeError as e:
            logger.exception("TypeError while validating report filename. May be a syntax error or an actual error.")
            raise ValidationError(str(e)) from e

    def render_filename(self, filename_template, ext=None):
        """
        Generate a filename for an export, rendering the `filename_template` with
        the jinja data and appending the extension.
        """

        template = self.jinja_env.from_string(filename_template)
        data = self.data.copy()
        data["company_name"] = CompanyInformation.get_solo().company_name
        data["now"] = datetime.now()

        report_name = template.render(data)
        report_name = _replace_filename_chars(report_name)
        if ext is None:
            ext = self.extension()
        return report_name.strip() + "." + ext


def _valid_xml_char_ordinal(c):
    """
    Clean string to make all characters XML compatible for Word documents.

    Source:
        https://stackoverflow.com/questions/8733233/filtering-out-certain-bytes-in-python

    **Parameters**

    ``c`` : string
        String of characters to validate
    """
    codepoint = ord(c)
    # Conditions ordered by presumed frequency
    return (
        0x20 <= codepoint <= 0xD7FF
        or codepoint in (0x9, 0xA, 0xD)
        or 0xE000 <= codepoint <= 0xFFFD
        or 0x10000 <= codepoint <= 0x10FFFF
    )


def _replace_filename_chars(name):
    """Remove illegal characters from the report name."""
    name = name.replace("–", "-")
    return re.sub(r"[<>:;\"'/\\|?*.,{}\[\]]", "", name)
