import datetime
from collections import OrderedDict
from typing import Dict, List, Optional


class Feed:
    """A single feed similar to an atom feed or a rss channel"""

    def __init__(self, **kwargs):
        self.description = None  # type: Optional[str]
        self.title = None  # type: Optional[str]
        self.url = None  # type: Optional[str]
        self.update = None  # type: Optional[datetime.datetime]
        self.items = []  # type: List[FeedItem]
        self._data = {}  # type: Dict
        allowed_keys = vars(self).keys()
        for key, value in kwargs.items():
            if key in allowed_keys:
                setattr(self, key, value)

    def __getattr__(self, name):
        return self._data[name]

    def unique_items_by_url(self):
        """Remove from items duplicated url. Order is preserved.

        If two items have the same url, the latter will survive."""
        items = OrderedDict([item.url, item] for item in reversed(self.items))
        self.items = list(reversed(items.values()))

    def sort_items(self):
        """Order items by `update`, if every item has an `update` value."""
        for item in self.items:
            if not item.update:
                return
        self.items = sorted(self.items, key=lambda i: i.update)

    def __repr__(self):
        return "Feed({})".format(", ".join([f"{k}={v!r}" for k, v in vars(self).items() if v]))


class FeedItem:
    """A feed entry, similar to an atom entry or a rss item"""

    def __init__(self, **kwargs):
        self.content = None  # type: Optional[str]
        self.content_type = None  # type: Optional[str]
        self.title = None  # type: Optional[str]
        self.url = None  # type: Optional[str]
        self.id = None  # type: Optional[str]
        self.update = None  # type: Optional[datetime.datetime]
        self.categories = []  # type: List[str]
        self._data = {}  # type: Dict
        allowed_keys = vars(self).keys()
        for key, value in kwargs.items():
            if key in allowed_keys:
                setattr(self, key, value)

    def __getattr__(self, name):
        return self._data[name]

    def __repr__(self):
        return "FeedItem({})".format(", ".join([f"{k}={v!r}" for k, v in vars(self).items() if v]))
