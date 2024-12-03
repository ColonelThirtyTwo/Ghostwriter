from django.test import TestCase
from collab_model.tiptap_converters.html import TiptapToHtml
import pycrdt

class TiptapToHtmlTestCase(TestCase):
    def setUp(self) -> None:
        self.doc = pycrdt.Doc(client_id=0)
        self.frag = self.doc.get("test", type=pycrdt.XmlFragment)

    def test_plain_text(self):
        with self.doc.transaction():
            p = self.frag.children.append(pycrdt.XmlElement("paragraph"))
            p.children.append("Hello, world!")

            s = str(TiptapToHtml(self.frag))
            self.assertEqual(s, "<p><span>Hello, world!</span></p>")
