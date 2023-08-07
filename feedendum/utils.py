import itertools
from collections import defaultdict

from lxml.etree import CDATA, Element, SubElement

NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "atom03": "http://purl.org/atom/ns#",
    "content": "http://purl.org/rss/1.0/modules/content/",
    "dc": "http://purl.org/dc/elements/1.1/",
    "itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd",
    "media": "http://search.yahoo.com/mrss/",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfns": "http://purl.org/rss/1.0/",
    "slash": "http://purl.org/rss/1.0/modules/slash/",
    "thread": "http://purl.org/syndication/thread/1.0",
}

# from https://www.w3.org/TR/xml/#NT-Char
# Allowed: #x9 | #xA | #xD | [#x20-...
_NON_PRINTABLE_C0 = itertools.chain(range(0x00, 0x09), range(0x0B, 0x0D), range(0x0E, 0x20))
_TRANSLATE_MAP = {c: None for c in _NON_PRINTABLE_C0}


def get_text(element: Element, name: str) -> str | None:
    child = element.find(name, namespaces=NS)
    if child is None:
        return None
    if child.text is None:
        return None
    child.getparent().remove(child)
    return child.text.strip()


def get_attribute(element: Element, name: str, attribute: str) -> str | None:
    child = element.find(name, namespaces=NS)
    if child is None:
        return None
    if attribute not in child.attrib:
        return None
    return child.attrib[attribute].strip()


def add_text_element(
    root: Element, name: str, text: str | None, formatter=None
) -> "Element | None":
    if text and formatter:
        text = formatter(text)
    if text:
        elem = SubElement(root, name)
        text = text.translate(_TRANSLATE_MAP)
        elem.text = text
        return elem
    return None


def add_content_element(root: Element, name: str, text: str | None) -> "Element | None":
    if text:
        text = text.translate(_TRANSLATE_MAP)
        elem = SubElement(root, name)
        if ">" in text or "<" in text:
            # avoid escaping
            elem.text = CDATA(text)
        else:
            elem.text = text
        return elem
    return None


def set_attribute(element: Element, attribute: str, value: str | None) -> None:
    if element is not None and attribute and value:
        element.attrib[attribute] = value


def etree_to_dict(t: Element):
    # From https://stackoverflow.com/a/10076823
    d = {t.tag: {} if t.attrib else None}  # type: dict[str, Any]
    children = list(t)
    if children:
        dd = defaultdict(list)
        for dc in map(etree_to_dict, children):
            for k, v in dc.items():
                dd[k].append(v)
        d = {t.tag: {k: v[0] if len(v) == 1 else v for k, v in dd.items()}}
    if t.attrib:
        d[t.tag].update(("@" + k, v) for k, v in t.attrib.items())
    if t.text:
        text = t.text.strip()
        if children or t.attrib:
            if text:
                d[t.tag]["#text"] = text
        else:
            d[t.tag] = text
    return d


def dict_append_etree(d, root):
    if not d:
        pass
    elif isinstance(d, str):
        root.text = d
    elif isinstance(d, dict):
        for k, v in d.items():
            if k.startswith("#"):
                root.text = v
            elif k.startswith("@"):
                root.set(k[1:], v)
            elif isinstance(v, list):
                for e in v:
                    dict_append_etree(e, SubElement(root, k))
            else:
                dict_append_etree(v, SubElement(root, k))
