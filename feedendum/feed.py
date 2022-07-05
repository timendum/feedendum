import dataclasses
import datetime
from collections import OrderedDict
from typing import Optional


@dataclasses.dataclass(kw_only=True)
class Feed:
    """A single feed similar to an atom feed or a rss channel"""

    description: Optional[str] = None
    title: Optional[str] = None
    url: Optional[str] = None
    update: Optional[datetime.datetime] = None
    items: list["FeedItem"] = dataclasses.field(default_factory=list)
    _data: dict = dataclasses.field(default_factory=dict)

    def __getattr__(self, name):
        return self._data[name]

    def unique_items_by_url(self):
        """Remove from items duplicated url. Order is preserved.

        If two items have the same url, the latter will survive."""
        items = OrderedDict([item.url, item] for item in reversed(self.items))
        self.items = list(reversed(items.values()))

    def sort_items(self, key=None) -> None:
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

    content: Optional[str] = None
    content_type: Optional[str] = None
    title: Optional[str] = None
    url: Optional[str] = None
    id: Optional[str] = None
    update: Optional[datetime.datetime] = None
    categories: list[str] = dataclasses.field(default_factory=list)
    _data: dict = dataclasses.field(default_factory=dict)

    def __getattr__(self, name):
        return self._data[name]

    def __repr__(self):
        return "FeedItem({})".format(", ".join([f"{k}={v!r}" for k, v in vars(self).items() if v]))
