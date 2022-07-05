from datetime import datetime as dt
from typing import Optional

from requests import HTTPError

import lxml.etree as ET

from .exceptions import FeedParseError, FeedXMLError, RemoteFeedError
from .feed import Feed, FeedItem
from .utils import (
    NS,
    add_content_element,
    add_text_element,
    dict_append_etree,
    etree_to_dict,
    get_attribute,
    get_text,
    set_attribute,
)

try:
    import requests
except ModuleNotFoundError:
    requests = None  # type: ignore


def parse_text(text: str) -> Feed:
    try:
        tree = ET.fromstring(text.encode("utf-8"))
    except ET.ParseError:
        raise FeedXMLError("Not a valid XML document")
    return to_feed(tree)


def parse_file(file) -> Feed:
    try:
        tree = ET.parse(file)
    except ET.ParseError:
        raise FeedXMLError("Not a valid XML document")
    return to_feed(tree.getroot())


def parse_url(url, **extra) -> Feed:
    if not requests:
        raise ModuleNotFoundError(
            "No module named 'requests' found, please install it to use this feature"
        )
    r = requests.get(url)
    try:
        r.raise_for_status()
    except HTTPError as e:
        raise RemoteFeedError(e)
    return parse_text(r.text)


def parse_iso_datetime(elem: ET.Element, name: str) -> Optional[dt]:
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
    if root.tag != "{http://www.w3.org/2005/Atom}feed":
        raise FeedParseError("Root element is not 'feed'")
    feed = Feed()
    feed.title = get_text(root, "atom:title")
    feed.description = get_text(root, "atom:subtitle")
    feed.update = parse_iso_datetime(root, "atom:updated")
    for link in root.findall("atom:link", NS):
        rel = link.get("rel")
        if not rel or rel == "alternate":
            feed.url = link.get("href")
            link.getparent().remove(link)
            break
    for item in root.findall("atom:entry", NS):
        fitem = FeedItem()
        for link in item.findall("atom:link", NS):
            rel = link.get("rel")
            if not rel or rel == "alternate":
                fitem.url = link.get("href")
                link.getparent().remove(link)
                break
        fitem.title = get_text(item, "atom:title")
        fitem.id = get_text(item, "atom:id")
        fitem.content_type = get_attribute(item, "atom:content", "type")
        fitem.content = get_text(item, "atom:content")
        fitem.update = parse_iso_datetime(item, "atom:updated") or parse_iso_datetime(
            item, "atom:published"
        )
        for link in item.findall("atom:category", NS):
            term = link.get("term")
            if term:
                fitem.categories.append(term)
        fitem._data = etree_to_dict(item)["{http://www.w3.org/2005/Atom}entry"] or {}
        feed.items.append(fitem)
        root.remove(item)
    feed._data = etree_to_dict(root)["{http://www.w3.org/2005/Atom}feed"] or {}
    return feed


def generate(feed):
    nsmap = {None: NS["atom"]}
    ns = f"{{{NS['atom']}}}"
    root = ET.Element(f"{ns}feed", nsmap=nsmap)
    add_text_element(root, f"{ns}title", feed.title)
    add_text_element(root, f"{ns}subtitle", feed.description)
    add_text_element(root, f"{ns}updated", feed.update, lambda x: dt.isoformat(x))
    if feed.url:
        elink = ET.SubElement(root, f"{ns}link")
        elink.set("href", feed.url)
    dict_append_etree(feed._data, root)
    for fitem in feed.items:
        entry = ET.SubElement(root, f"{ns}entry")
        add_text_element(entry, f"{ns}title", fitem.title)
        add_text_element(entry, f"{ns}id", fitem.id)
        add_text_element(entry, f"{ns}updated", feed.update, lambda x: dt.isoformat(x))
        if fitem.url:
            elink = ET.SubElement(entry, f"{ns}link")
            elink.set("href", fitem.url)
        elem = add_content_element(entry, f"{ns}content", fitem.content)
        set_attribute(elem, "type", fitem.content_type)
        for fcategory in fitem.categories:
            elink = ET.SubElement(entry, f"{ns}category")
            elink.set("term", fcategory)
        dict_append_etree(fitem._data, entry)
    return ET.tostring(root, encoding="UTF-8", xml_declaration=True).decode("utf-8")
