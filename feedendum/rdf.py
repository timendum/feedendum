"""Module to handle RDF (RSS 1.0) feeds."""
from datetime import datetime as dt

import lxml.etree as ET

from .exceptions import FeedParseError, FeedXMLError, RemoteFeedError
from .feed import Feed, FeedItem
from .utils import (
    NS,
    add_content_element,
    add_text_element,
    dict_append_etree,
    etree_to_dict,
    get_text,
)

try:
    import requests
except ModuleNotFoundError:
    requests = None  # type: ignore


def parse_text(text: str) -> Feed:
    """Generate a :class:`.feed.Feed` from a RDF string.v
    
    :raises FeedXMLError: If string is not a valid xml.
    :raises FeedParseError: If the xml is not an RSS feed."""
    try:
        tree = ET.fromstring(text.encode("utf-8"))
    except ET.ParseError as e:
        raise FeedXMLError("Not a valid XML document") from e
    return to_feed(tree)


def parse_file(file) -> Feed:
    """Generate a :class:`.feed.Feed` from a RDF file.
    
    :raises FeedXMLError: If string is not a valid xml.
    :raises FeedParseError: If the xml is not an RSS feed."""
    try:
        tree = ET.parse(file)
    except ET.ParseError as e:
        raise FeedXMLError("Not a valid XML document") from e
    return to_feed(tree.getroot())


def parse_url(url, **extra) -> Feed:
    """Utility method to generate a :class:`.feed.Feed` from a RDF URL.

    :raises ModuleNotFoundError: If `requests` is not available.
    :raises FeedXMLError: If string is not a valid xml.
    :raises FeedParseError: If the xml is not an RSS feed."""
    if not requests:
        raise ModuleNotFoundError(
            "No module named 'requests' found, please install it to use this feature"
        )
    r = requests.get(url)
    try:
        r.raise_for_status()
    except requests.HTTPError as e:
        raise RemoteFeedError() from e
    return parse_text(r.text)


def __parse_iso_datetime(elem: ET.Element, name: str) -> dt | None:
    text = get_text(elem, name)
    if text:
        try:
            if text.endswith("Z"):
                text = text[:-1] + "+00:00"
            return dt.fromisoformat(text)
        except ValueError:
            pass
    return None


def to_feed(root) -> Feed:
    """Generate a :class:`.feed.Feed` from a root XML element of an RDF document.
    
    :raises FeedXMLError: If string is not a valid xml.
    :raises FeedParseError: If the xml is not an RSS feed.
    
    :meta private:"""
    if root.tag != "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}RDF":
        raise FeedParseError("Root element is not 'rdf'")

    channel = root.find("rdfns:channel", namespaces=NS)
    if channel is None:
        raise FeedParseError("Element 'channel' not found")
    feed = Feed()
    feed.title = get_text(channel, "rdfns:title")
    feed.description = get_text(channel, "rdfns:description")
    feed.url = get_text(channel, "rdfns:link")
    feed.update = __parse_iso_datetime(channel, "dc:date")

    for item in root.findall("rdfns:item", NS):
        fitem = FeedItem()
        fitem.title = get_text(item, "rdfns:title")
        fitem.url = get_text(item, "rdfns:link")
        fitem.id = fitem.url
        fitem.content = get_text(item, "rdfns:description")
        fitem.update = __parse_iso_datetime(item, "dc:date")
        fitem.content_type = get_text(item, "dc:format")
        term = get_text(item, "dc:subject")
        if term:
            fitem.categories.append(term)
        fitem._data = etree_to_dict(item)["{http://purl.org/rss/1.0/}item"] or {}
        feed.items.append(fitem)
        root.remove(item)
    feed._data = etree_to_dict(channel)['{http://purl.org/rss/1.0/}channel'] or {}
    return feed


def generate(feed):
    """Returns a string RDF rappresentation of a feed."""
    nsmap = {None: "http://purl.org/rss/1.0/", "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
             "dc": "http://purl.org/dc/elements/1.1/",
             "syn": "http://purl.org/rss/1.0/modules/syndication/"}
    rdf = f"{{{NS['rdf']}}}"
    ns = f"{{{NS['rdfns']}}}"
    dc = f"{{{NS['dc']}}}"
    root = ET.Element(f"{rdf}RDF", nsmap=nsmap)
    channel = ET.SubElement(root, f"{ns}channel")
    add_text_element(channel, "title", feed.title)
    add_text_element(channel, "link", feed.url)
    add_text_element(channel, "description", feed.description)
    if feed.update is not None:
        add_text_element(channel, f"{dc}date", dt.isoformat(feed.update))
    dict_append_etree(feed._data, root)
    for fitem in feed.items:
        entry = ET.SubElement(root, f"{ns}item")
        add_text_element(entry, f"{ns}title", fitem.title)
        add_text_element(entry, f"{ns}link", fitem.url)
        add_text_element(entry, f"{ns}id", fitem.id)
        add_content_element(entry, f"{ns}description", fitem.content)
        add_text_element(entry, f"{dc}date", dt.isoformat(fitem.update))
        add_text_element(entry, f"{dc}format", fitem.content_type)
        for fcategory in fitem.categories:
            add_text_element(entry, f"{dc}subject", fcategory)
        dict_append_etree(fitem._data, entry)
    ET.cleanup_namespaces(root)
    return ET.tostring(root, encoding="UTF-8", xml_declaration=True).decode("utf-8")
