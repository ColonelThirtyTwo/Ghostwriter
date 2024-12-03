
from typing import Iterable
from io import StringIO

import pycrdt
import pycrdt._base

def dump_yjs_doc(doc: pycrdt.Doc, top_level_elements: Iterable[tuple[str, pycrdt._base.BaseType]]) -> str:
    """
    Dumps the contents of a yjs doc to a human-readable string, for debugging.
    """
    out = StringIO()
    out.write("ydoc{")

    sorted_items = sorted(top_level_elements, key=lambda t: t[0])
    for k, typ in sorted_items:
        out.write(f"\t{k!r}: ")
        _dump_one(out, 1, doc.get(k, type=typ))
        out.write(f",\n")

    out.write("}")
    return out.getvalue()

def _dump_one(out: StringIO, indent: int, value: pycrdt._base.BaseType):
    if not isinstance(value, pycrdt._base.BaseType):
        out.write(repr(value))
    elif isinstance(value, pycrdt.Text):
        # TODO: dump formatting
        out.write("Text(")
        out.write(repr(str(value)))
        out.write(")")
    elif isinstance(value, pycrdt.XmlFragment):
        # TODO: dump formatting
        out.write("XmlFragment(")
        out.write(repr(str(value)))
        out.write(")")
    elif isinstance(value, pycrdt.Array):
        out.write("Array([\n")
        for subvalue in value:
            out.write("\t"*(indent+1))
            _dump_one(out, indent+1, subvalue)
            out.write(",\n")
        out.write("\t"*indent)
        out.write("])")
    elif isinstance(value, pycrdt.Map):
        out.write("Map({\n")
        sorted_items = sorted(value.items(), key=lambda t: t[0])
        for k,v in sorted_items:
            out.write("\t"*(indent+1))
            out.write(repr(k))
            out.write(": ")
            _dump_one(out, indent+1, value[k])
            out.write(",\n")
        out.write("\t"*indent)
        out.write("})")
    else:
        out.write("Unrecognized({})".format(type(value)))
