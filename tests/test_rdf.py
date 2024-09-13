import unittest
from datetime import datetime as dt

import utils

import feedendum.rdf as rdf
from feedendum.exceptions import FeedParseError, FeedXMLError
from feedendum.feed import Feed


class RdfTest(unittest.TestCase):
    def test_parse_file(self):
        feed = rdf.parse_file("tests/lwn.rdf")
        self.assertIsNotNone(feed)
        self.assertEqual(feed.title, "LWN.net")
        self.assertEqual(feed.url, "https://lwn.net")
        self.assertEqual(
            feed.description,
            """LWN.net is a comprehensive source of news and opinions from
        and about the Linux community.  This is the main LWN.net feed,
        listing all articles which are posted to the site front page.""",
        )
        self.assertEqual(feed.update, None)  # No update
        self.assertIsInstance(feed._data, dict)
        self.assertIn("{http://purl.org/rss/1.0/modules/syndication/}updateFrequency", feed._data)
        self.assertIsInstance(feed.items, list)
        self.assertTrue(len(feed.items) > 1)
        self.assertEqual(feed.items[0].title, "Going Rogue (Digital Antiquarian)")
        self.assertIsInstance(feed.items[0].content, str)
        self.assertEqual(
            feed.items[0].url,
            "https://lwn.net/Articles/937631/",
        )
        self.assertEqual(
            feed.items[0].id,
            "https://lwn.net/Articles/937631/",
        )
        self.assertIsInstance(feed.items[0].update, dt)
        self.assertIsInstance(feed.items[0]._data, dict)
        self.assertNotIn("comments", feed.items[0]._data)

    def test_inout_file(self):
        feed = rdf.parse_file("tests/lwn.rdf")
        feed_out = rdf.generate(feed)
        self.assertTrue(utils.xml_equals("tests/lwn.rdf", feed_out))

    def test_parse_string(self):
        feed = rdf.parse_text(
            """<?xml version="1.0" encoding="ISO-8859-1"?>
<!-- generator="FeedCreator 1.7.2" -->
<rdf:RDF
    xmlns="http://purl.org/rss/1.0/"
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:slash="http://purl.org/rss/1.0/modules/slash/"
    xmlns:dc="http://purl.org/dc/elements/1.1/">
    <channel rdf:about="http://theoatmeal.com/feed/rss">
        <title>The Oatmeal - Comics by Matthew Inman</title>
        <description>I make comics about science, cats, social media, and sometimes goats.</description>
        <link>http://theoatmeal.com/</link>
       <dc:date>2023-07-07T20:51:51+01:00</dc:date>
        <items>
            <rdf:Seq>
                <rdf:li rdf:resource="http://theoatmeal.com/blog/wordy_online?no_popup=1"/>
                <rdf:li rdf:resource="http://theoatmeal.com/therapist?no_popup=1"/>
                <rdf:li rdf:resource="http://theoatmeal.com/comics/rise?no_popup=1"/>
                <rdf:li rdf:resource="http://theoatmeal.com/comics/venting?no_popup=1"/>
                <rdf:li rdf:resource="http://theoatmeal.com/comics/selfie_angles?no_popup=1"/>
                <rdf:li rdf:resource="http://theoatmeal.com/comics/baby_vs_intimacy?no_popup=1"/>
                <rdf:li rdf:resource="http://theoatmeal.com/comics/subtitles?no_popup=1"/>
                <rdf:li rdf:resource="http://theoatmeal.com/blog/netflix_kittens?no_popup=1"/>
                <rdf:li rdf:resource="http://theoatmeal.com/comics/discover_videos?no_popup=1"/>
            </rdf:Seq>
        </items>
    </channel>
    <item rdf:about="http://theoatmeal.com/blog/wordy_online?no_popup=1">
        <dc:format>text/html</dc:format>
        <dc:date>2023-04-17T14:46:51+01:00</dc:date>
        <dc:source>http://theoatmeal.com</dc:source>
        <dc:creator>Matthew Inman</dc:creator>
        <title>I'm thinking of a word. Try to guess what it is.</title>
        <link>http://theoatmeal.com/blog/wordy_online?no_popup=1</link>
        <description>&lt;a href=&quot;http://theoatmeal.com/blog/wordy_online?no_popup=1&quot;&gt;&lt;img width=&quot;600&quot; src=&quot;https://s3.amazonaws.com/theoatmeal-img/thumbnails/wordy_online_big.png&quot; alt=&quot;I'm thinking of a word. Try to guess what it is.&quot; class=&quot;border0&quot; /&gt;&lt;/a&gt;&lt;p&gt;I coded a daily word-guessing game.&lt;/p&gt;&lt;a href=&quot;http://theoatmeal.com/blog/wordy_online?no_popup=1&quot;&gt;View on my website&lt;/a&gt;&lt;br /&gt;&lt;br /&gt;</description>
    </item>
</rdf:RDF>
"""  # noqa: E501
        )
        self.assertIsNotNone(feed)
        self.assertEqual(feed.title, "The Oatmeal - Comics by Matthew Inman")
        self.assertEqual(feed.url, "http://theoatmeal.com/")
        self.assertEqual(
            feed.description,
            "I make comics about science, cats, social media, and sometimes goats.",
        )
        self.assertIsInstance(feed.update, dt)
        self.assertIsInstance(feed._data, dict)
        self.assertIn("{http://purl.org/rss/1.0/}items", feed._data)
        self.assertIsInstance(feed.items, list)
        self.assertTrue(len(feed.items) > 0)
        self.assertEqual(feed.items[0].title, "I'm thinking of a word. Try to guess what it is.")
        self.assertTrue("View on my website" in feed.items[0].content)
        self.assertEqual(feed.items[0].url, "http://theoatmeal.com/blog/wordy_online?no_popup=1")
        self.assertEqual(feed.items[0].id, "http://theoatmeal.com/blog/wordy_online?no_popup=1")
        self.assertEqual(feed.items[0].content_type, "text/html")
        self.assertIsInstance(feed.items[0].update, dt)
        self.assertIsInstance(feed.items[0]._data, dict)
        self.assertIsInstance(feed.items[0].categories, list)

    def test_generate(self):
        feed = rdf.parse_file("tests/lwn.rdf")
        self.assertIsNotNone(feed)
        xml = rdf.generate(feed)
        self.assertIsInstance(xml, str)
        # xml_declaration
        self.assertTrue("<?xml version=" in xml)
        # encoding
        self.assertTrue("encoding=" in xml)
        # root
        self.assertTrue("<rdf:RDF" in xml)
        # content root
        self.assertTrue("<channel" in xml)
        # feed.url
        self.assertTrue("<link>https://lwn.net</link>" in xml)
        # feed.description
        self.assertTrue(
            """LWN.net is a comprehensive source of news and opinions from
        and about the Linux community.  This is the main LWN.net feed,
        listing all articles which are posted to the site front page."""
            in xml
        )
        self.assertTrue("date>2023-07-07" in xml)
        # feed.title
        self.assertTrue("<title>LWN.net</title>" in xml)
        # feed._data element
        self.assertTrue("<dc:creator>corbet</dc:creator>" in xml)
        # feed.item.url element
        self.assertTrue("<link>https://lwn.net/Articles/937631/</link>" in xml)

    def test_unprintable(self):
        feed = Feed(title="Bad\u001aChar")
        xml = rdf.generate(feed)
        self.assertNotIn("\u001a", xml)

    def test_unparsable(self):
        with self.assertRaises(FeedXMLError):
            rdf.parse_text("A")
        with self.assertRaises(FeedParseError):
            rdf.parse_file("tests/martinfowler.atom")
        with self.assertRaises(FeedParseError):
            rdf.parse_file("tests/wikipedia-rss.xml")


if __name__ == "__main__":
    unittest.main()
