import unittest
from datetime import datetime as dt

from feedendum.feed import Feed, FeedItem


class FeedTest(unittest.TestCase):
    def test_base(self):
        feed = Feed()
        feed.title = "Title"
        self.assertIsInstance(feed, Feed)

    def test_init(self):
        feed = Feed(title="Title")
        self.assertEqual(feed.title, "Title")

    def test_init_catch(self):
        with self.assertRaises(TypeError):
            Feed(title="Title", dummy="Test")

    def test_repr(self):
        feed = Feed(title="Title")
        self.assertEqual(repr(feed), "Feed(title='Title')")

    def test_unique_items_by_url(self):
        feed = Feed()
        feed.items.append(FeedItem(url="1", title="1"))
        feed.items.append(FeedItem(url="2", title="2"))
        feed.items.append(FeedItem(url="3", title="3"))
        feed.items.append(FeedItem(url="1", title="4"))
        feed.unique_items_by_url()
        self.assertEqual(len(feed.items), 3)
        self.assertEqual(feed.items[0].url, "2")
        self.assertEqual(feed.items[1].url, "3")
        self.assertEqual(feed.items[2].url, "1")

    def test_sort_items_date(self):
        feed = Feed()
        feed.items.append(FeedItem(url="b", update=dt(2001, 1, 1, 2, 0)))  # 3
        feed.items.append(FeedItem(url="a", update=dt(2001, 1, 2, 1, 0)))  # 4
        feed.items.append(FeedItem(url="4", update=dt(2001, 1, 1, 1, 0)))  # 1
        feed.items.append(FeedItem(url="3", update=dt(2001, 1, 1, 1, 2)))  # 2
        feed.sort_items()
        self.assertEqual(len(feed.items), 4)
        self.assertEqual(feed.items[0].url, "4")
        self.assertEqual(feed.items[1].url, "3")
        self.assertEqual(feed.items[2].url, "b")
        self.assertEqual(feed.items[3].url, "a")

    def test_sort_items_no_date(self):
        feed = Feed()
        feed.items.append(FeedItem(url="b"))  # 3
        feed.items.append(FeedItem(url="a", update=dt(2001, 1, 2, 1, 0)))  # 4
        feed.items.append(FeedItem(url="4", update=dt(2001, 1, 1, 1, 0)))  # 1
        feed.items.append(FeedItem(url="3", update=dt(2001, 1, 1, 1, 2)))  # 2
        feed.sort_items()
        self.assertEqual(len(feed.items), 4)
        self.assertEqual(feed.items[0].url, "b")
        self.assertEqual(feed.items[1].url, "a")
        self.assertEqual(feed.items[2].url, "4")
        self.assertEqual(feed.items[3].url, "3")


class FeedItemTest(unittest.TestCase):
    def test_base(self):
        feeditem = FeedItem()
        feeditem.title = "Title"
        self.assertIsInstance(feeditem, FeedItem)

    def test_init(self):
        feeditem = FeedItem(title="Title")
        self.assertEqual(feeditem.title, "Title")

    def test_init_catch(self):
        with self.assertRaises(TypeError):
            FeedItem(title="Title", dummy="Test")

    def test_repr(self):
        feeditem = FeedItem(title="Title")
        self.assertEqual(repr(feeditem), "FeedItem(title='Title')")
