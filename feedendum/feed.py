import dataclasses
import datetime
from collections import OrderedDict


@dataclasses.dataclass(kw_only=True)
class Feed:
    """A single feed similar to an atom feed or a rss channel."""

    description: str | None = None
    """Description of the feed."""
    title: str | None = None
    """Title of the feed."""
    url: str | None = None
    """URL of the feed."""
    update: datetime.datetime | None = None
    """Last update."""
    items: list["FeedItem"] = dataclasses.field(default_factory=list)
    """List of items."""
    _data: dict = dataclasses.field(default_factory=dict)
    """Other attributes not managed."""

    def __getattr__(self, name):
        return self._data[name]

    def unique_items_by_url(self):
        """Remove from items duplicated url. Order is preserved.

        If two items have the same url, the latter will survive."""
        items = OrderedDict([item.url, item] for item in reversed(self.items))
        self.items = list(reversed(items.values()))

    def sort_items(self, key=None) -> bool:
        """Order items by according to key or by `update`, if every item has an `update` value.
        Returns `True` if sorted, `False` otherwise."""
        if not key:

            def key(i):
                return i.update

        for item in self.items:
            try:
                if not key(item):
                    return False
            except Exception:
                return False
        self.items = sorted(self.items, key=key)
        return True

    def __repr__(self):
        return "Feed({})".format(", ".join([f"{k}={v!r}" for k, v in vars(self).items() if v]))


@dataclasses.dataclass(kw_only=True)
class FeedItem:
    """A feed entry, similar to an atom entry or a rss item"""

    content: str | None = None
    """The content of the item (usually a text or HTML)."""
    content_type: str | None = None
    """The type of the content."""
    title: str | None = None
    """The title of the item,"""
    url: str | None = None
    """The URL of the item,"""
    id: str | None = None
    """The id of the item,"""
    update: datetime.datetime | None = None
    """Last update."""
    categories: list[str] = dataclasses.field(default_factory=list)
    """The categories of the item."""
    _data: dict = dataclasses.field(default_factory=dict)
    """Other attributes not managed."""

    def __getattr__(self, name):
        return self._data[name]

    def __repr__(self):
        return "FeedItem({})".format(", ".join([f"{k}={v!r}" for k, v in vars(self).items() if v]))
