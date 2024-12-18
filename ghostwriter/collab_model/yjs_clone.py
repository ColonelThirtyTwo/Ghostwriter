"""
Functions for deeply copying YJS values between documents (or in the same document).
"""

import pycrdt

def yjs_copy_text(text_from: pycrdt.Text | pycrdt.XmlText, text_to: pycrdt.Text | pycrdt.XmlText):
    """
    Copies contents from one pycrdt.Text to another, replacing the destination's contents.

    Also copies embeds and formatting attributes. The two texts may be in the same or different docs.
    """
    text_to.clear()
    for el, attrs in text_from.diff():
        text_to.insert_embed(len(text_to), el, attrs or {})

def yjs_copy_xml(xml_from: pycrdt.XmlFragment | pycrdt.XmlElement, xml_to: pycrdt.XmlFragment | pycrdt.XmlElement):
    """
    Deeply copies an XML fragment or element to another, replacing the destination's contents.

    Copies attributes (for elements) and deeply copies children. Will throw an error if passed two elements with differring tags,
    since there's no way to change the tag of an existing element in pycrdt.

    Also copies embeds and formatting attributes. The two elements or fragments may be in the same or different docs.
    """

    for i in reversed(range(len(xml_to.children))):
        del xml_to.children[i]
    if isinstance(xml_from, pycrdt.XmlElement):
        # Can't change tag so assert its the same
        if xml_from.tag != xml_to.tag:
            raise ValueError("Cannot change tag of element {} to {}".format(xml_to.tag, xml_from.tag))

        # Copy attributes
        for k,v in xml_from.attributes:
            xml_to.attributes[k] = v
        # Copy list of attributes since we edit them as we iterate over them
        for k in [k for k,_ in xml_to.attributes]:
            if k not in xml_from.attributes:
                del xml_to.attributes[k]

    for child in xml_from.children:
        if isinstance(child, pycrdt.XmlText):
            text = pycrdt.XmlText()
            xml_to.children.append(text)
            yjs_copy_text(child, text)
        elif isinstance(child, pycrdt.XmlElement):
            el = pycrdt.XmlElement(child.tag)
            xml_to.children.append(el)
            yjs_copy_xml(child, el)
        else:
            raise ValueError("Unrecognized XML child type: {}".format(type(child)))

def yjs_copy_map(map_from: pycrdt.Map, map_to: pycrdt.Map):
    """
    Deeply copies a map to another, replacing the destination's contents.
    """
    for k,v in map_from.items():
        if isinstance(v, pycrdt.Text):
            v2 = pycrdt.Text()
            map_to[k] = v2
            yjs_copy_text(v, v2)
        elif isinstance(v, pycrdt.XmlFragment):
            v2 = pycrdt.XmlFragment()
            map_to[k] = v2
            yjs_copy_xml(v, v2)
        elif isinstance(v, pycrdt.Map):
            v2 = pycrdt.Map()
            map_to[k] = v2
            yjs_copy_map(v, v2)
        elif isinstance(v, pycrdt.Array):
            v2 = pycrdt.Array()
            map_to[k] = v2
            yjs_copy_array(v, v2)
        else:
            map_to[k] = v
    for k in list(map_to.keys()):
        if k not in map_from:
            del map_to[k]

def yjs_copy_array(arr_from: pycrdt.Array, arr_to: pycrdt.Array):
    """
    Deeply copies one array to another.
    """
    arr_to.clear()
    for v in arr_from:
        if isinstance(v, pycrdt.Text):
            v2 = pycrdt.Text()
            arr_to.append(v2)
            yjs_copy_text(v, v2)
        elif isinstance(v, pycrdt.XmlFragment):
            v2 = pycrdt.XmlFragment()
            arr_to.append(v2)
            yjs_copy_xml(v, v2)
        elif isinstance(v, pycrdt.Map):
            v2 = pycrdt.Map()
            arr_to.append(v2)
            yjs_copy_map(v, v2)
        elif isinstance(v, pycrdt.Array):
            v2 = pycrdt.Array()
            arr_to.append(v2)
            yjs_copy_array(v, v2)
        else:
            arr_to.append(v)
