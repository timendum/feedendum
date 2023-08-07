import unittest
from datetime import datetime as dt

import feedendum.atom as atom
from feedendum.exceptions import FeedParseError, FeedXMLError
from feedendum.feed import Feed


class AtomTest(unittest.TestCase):
    def test_parse_file(self):
        feed = atom.parse_file("tests/martinfowler.atom")
        self.assertIsNotNone(feed)
        self.assertEqual(feed.title, "Martin Fowler")
        self.assertEqual(feed.url, "https://martinfowler.com")
        self.assertEqual(feed.description, "Master feed of news and updates from martinfowler.com")
        self.assertIsInstance(feed.update, dt)
        self.assertIsInstance(feed._data, dict)
        self.assertIn('{http://www.w3.org/2005/Atom}author', feed._data)
        self.assertIsInstance(feed.items, list)
        self.assertTrue(len(feed.items) > 1)
        self.assertEqual(feed.items[0].title, "Bliki: ExploratoryTesting")
        self.assertIsInstance(feed.items[0].content, str)
        self.assertEqual(
            feed.items[0].url, "https://martinfowler.com/bliki/ExploratoryTesting.html"
        )
        self.assertEqual(feed.items[0].id, "https://martinfowler.com/bliki/ExploratoryTesting.html")
        self.assertIsInstance(feed.items[0].update, dt)
        self.assertIsInstance(feed.items[0]._data, dict)
        self.assertIsInstance(feed.items[0].categories, list)
        self.assertNotEqual(feed.items[0].content, None)
        self.assertNotEqual(feed.items[0].content_type, None)
        self.assertTrue(len(feed.items[0].categories) > 0)
        self.assertEqual(feed.items[0].categories[0], "bliki")

    def test_parse_string(self):
        feed = atom.parse_text(
            """<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">

  <title>Example Feed</title>
  <link href="http://example.org/"/>
  <updated>2003-12-13T18:30:02Z</updated>

  <entry>
    <title>Atom-Powered Robots Run Amok</title>
    <link href="http://example.org/2003/12/13/atom03"/>
    <id>urn:uuid:1225c695-cfb8-4ebb-aaaa-80da344efa6a</id>
    <updated>2003-12-13T18:30:02Z</updated>
    <summary>Some text.</summary>
    <extra>An extra</extra>
  </entry>

</feed>"""
        )
        self.assertIsNotNone(feed)
        self.assertEqual(feed.title, "Example Feed")
        self.assertEqual(feed.url, "http://example.org/")
        self.assertEqual(feed.description, None)
        self.assertIsInstance(feed.update, dt)
        self.assertIsInstance(feed._data, dict)
        self.assertIsInstance(feed.items, list)
        self.assertTrue(len(feed.items) > 0)
        self.assertEqual(feed.items[0].title, "Atom-Powered Robots Run Amok")
        self.assertEqual(feed.items[0].content, None)
        self.assertEqual(feed.items[0].url, "http://example.org/2003/12/13/atom03")
        self.assertEqual(feed.items[0].id, "urn:uuid:1225c695-cfb8-4ebb-aaaa-80da344efa6a")
        self.assertIsInstance(feed.items[0].update, dt)
        self.assertIsInstance(feed.items[0]._data, dict)
        self.assertIn('{http://www.w3.org/2005/Atom}extra', feed.items[0]._data)

    def test_generate(self):
        feed = atom.parse_file("tests/martinfowler.atom")
        self.assertIsNotNone(feed)
        xml = atom.generate(feed)
        self.assertIsInstance(xml, str)
        # xml_declaration
        self.assertTrue("<?xml version=" in xml)
        # encoding
        self.assertTrue("encoding=" in xml)
        # root
        self.assertTrue('<feed xmlns="http://www.w3.org/2005/Atom">' in xml)
        # feed.url
        self.assertTrue('<link href="https://martinfowler.com"/>' in xml)
        # feed.description
        self.assertTrue("<subtitle>Master feed of" in xml)
        # feed._data element
        self.assertTrue("<id>https://martinfowler.com/feed.atom</id>" in xml)
        # feed._data sub elements
        self.assertTrue("<author>" in xml)
        self.assertTrue("<email>fowler@acm.org</email>" in xml)
        # feed.update
        self.assertTrue("<updated>2019-11-18T" in xml)
        self.assertTrue("<title>Bliki: ExploratoryTesting</title>" in xml)
        self.assertTrue(
            '<link href="https://martinfowler.com/bliki/ExploratoryTesting.html"' in xml
        )
        self.assertTrue("<id>https://martinfowler.com/bliki/ExploratoryTesting.html</id>" in xml)
        self.assertTrue('<category term="bliki"/>' in xml)
        self.assertTrue("Exploratory testing is a style of testing" in xml)

    def test_unprintable(self):
        feed = Feed(title="Bad\u0008Char")
        xml = atom.generate(feed)
        self.assertNotIn("\u0008", xml)

    def test_unparsable(self):
        with self.assertRaises(FeedXMLError):
            atom.parse_text('A')
        with self.assertRaises(FeedParseError):
            atom.parse_file('tests/wikipedia-rss.xml')
        with self.assertRaises(FeedParseError):
            atom.parse_file('tests/lwn.rdf')

if __name__ == '__main__':
    unittest.main()