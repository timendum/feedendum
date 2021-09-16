from datetime import datetime as dt
from email.utils import format_datetime, parsedate_to_datetime
from typing import Optional

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
    r.raise_for_status()
    return parse_text(r.text)


def parse_rfc2822_datetime(elem: ET.Element, name: str) -> Optional[dt]:
    text = get_text(elem, name)
    if text:
        try:
            return parsedate_to_datetime(text)
        except ValueError:
            pass
    return None


def to_feed(root) -> Feed:
    if root.tag != "rss":
        raise FeedParseError("Root element is not 'rss' but " + root.tag)
    rss_version = root.get("version")
    if rss_version != "2.0":
        raise FeedParseError("RSS feed version not 2.0 but '{}'".format(rss_version))
    channel = root.find("channel")
    if channel is None:
        raise FeedParseError("Element 'channel' not found")
    feed = Feed()
    feed.title = get_text(channel, "title")
    feed.description = get_text(channel, "description")
    feed.url = get_text(channel, "link")
    feed.update = parse_rfc2822_datetime(channel, "pubDate") or parse_rfc2822_datetime(
        channel, "lastBuildDate"
    )
    for item in channel.findall("item"):
        fitem = FeedItem()
        fitem.url = get_text(item, "link")
        fitem.title = get_text(item, "title")
        fitem.id = get_text(item, "guid")
        fitem.content = get_text(item, "description")
        fitem.update = parse_rfc2822_datetime(item, "pubDate")
        for category in item.findall("category"):
            if category.text:
                fitem.categories.append(category.text)
        fitem._data = etree_to_dict(item)["item"] or {}
        feed.items.append(fitem)
        channel.remove(item)
    feed._data = etree_to_dict(channel)["channel"] or {}
    return feed


def generate(feed):
    root = ET.Element("rss", nsmap=NS)
    root.set("version", "2.0")
    channel = ET.SubElement(root, "channel")
    add_text_element(channel, "title", feed.title)
    add_text_element(channel, "description", feed.description)
    add_text_element(channel, "pubDate", feed.update, lambda x: format_datetime(x))
    add_text_element(channel, "link", feed.url)
    dict_append_etree(feed._data, channel)
    for fitem in feed.items:
        item = ET.SubElement(channel, "item")
        add_text_element(item, "title", fitem.title)
        add_text_element(item, "guid", fitem.id)
        add_text_element(item, "pubDate", fitem.update, lambda x: format_datetime(x))
        add_text_element(item, "link", fitem.url)
        add_content_element(item, "description", fitem.content)
        for fcategory in fitem.categories:
            add_text_element(item, "category", fcategory)
        dict_append_etree(fitem._data, item)
    return ET.tostring(root, encoding="UTF-8", xml_declaration=True).decode("utf-8")
