import lxml.etree as ET


def _sort_elem(e: ET.Element) -> tuple:
    # Try sorting element, best effort
    # Use:
    # - tag name
    # - number of attributes
    return (e.tag, *list(e.attrib.keys()))


def etree_equal(e1: ET.Element, e2: ET.Element) -> bool:
    # print(e1, e2)
    if e1.tag != e2.tag:
        raise ValueError(f"Tag: {e1.tag} != {e2.tag}")
    if e1.text and e2.text and e1.text.strip() != e2.text.strip():
        if _iso_formatting_workaround(e1, e2):
            pass
        else:
            raise ValueError(f"Text: {e1.text} != {e2.text}")
    if e1.tail and e2.tail and e1.tail != e2.tail:
        raise ValueError(f"Tail: {e1.tail} != {e2.tail}")
    if e1.attrib != e2.attrib:
        if _rss_guid_workaround(e1, e2):
            pass
        else:
            raise ValueError(f"Attrib: {e1.attrib} != {e2.attrib}")
    if len(e1) != len(e2):
        print(ET.tostring(e1).decode("utf-8"), ET.tostring(e2).decode("utf-8"))
        raise ValueError(f"Len: {len(e1)} != {len(e2)}")
    _rss_lastbuilddate_workaround(e1, e2)
    for c1, c2 in zip(sorted(e1, key=_sort_elem), sorted(e2, key=_sort_elem), strict=True):
        etree_equal(c1, c2)
    return True


def xml_equals(infile, instring):
    tree1 = ET.parse(infile)
    tree2 = ET.fromstring(instring.encode("utf-8"))
    return etree_equal(tree1.getroot(), tree2)


def _rss_lastbuilddate_workaround(e1: ET.Element, e2: ET.Element) -> None:
    if e1.find("lastBuildDate") is not None and e2.find("pubDate") is not None:
        # workaround for RSS: convert lastBuildDate to pubDate
        c1 = e1.find("lastBuildDate")
        c2 = e2.find("pubDate")
        c1.tag = c2.tag
        etree_equal(c1, c2)
        c1.getparent().remove(c1)
        c2.getparent().remove(c2)


def _iso_formatting_workaround(e1: ET.Element, e2: ET.Element) -> bool:
    return e1.tag == "pubDate" and (
        e1.text.strip().replace(" GMT", "").replace(" +0000", "")
        == e2.text.strip().replace(" GMT", "").replace(" +0000", "")
    )


def _rss_guid_workaround(e1: ET.Element, e2: ET.Element) -> bool:
    # We don't write guid.isPermalink in RSS
    return e1.tag == "guid" and len(e1.attrib) == 1 and "isPermaLink" in e1.attrib
