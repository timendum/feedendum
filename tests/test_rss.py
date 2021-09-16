import unittest
from datetime import datetime as dt

import feedendum.rss as rss
from feedendum.feed import Feed


class RssTest(unittest.TestCase):
    def test_parse_file(self):
        feed = rss.parse_file("tests/wikipedia-rss.xml")
        self.assertIsNotNone(feed)
        self.assertEqual(feed.title, "RSS - Revision history")
        self.assertEqual(feed.url, "https://en.wikipedia.org/w/index.php?title=RSS&action=history")
        self.assertEqual(feed.description, "Revision history for this page on the wiki")
        self.assertIsInstance(feed.update, dt)
        self.assertIsInstance(feed._data, dict)
        self.assertIsInstance(feed.items, list)
        self.assertTrue(len(feed.items) > 1)
        self.assertEqual(feed.items[0].title, "Calbow: /* Current usage */ rewording")
        self.assertIsInstance(feed.items[0].content, str)
        self.assertEqual(
            feed.items[0].url,
            "https://en.wikipedia.org/w/index.php?title=RSS&diff=924206591&oldid=prev",
        )
        self.assertEqual(
            feed.items[0].id,
            "https://en.wikipedia.org/w/index.php?title=RSS&diff=924206591&oldid=prev",
        )
        self.assertIsInstance(feed.items[0].update, dt)
        self.assertIsInstance(feed.items[0]._data, dict)
        self.assertIn('comments', feed.items[0]._data)

    def test_parse_string(self):
        feed = rss.parse_text(
            """<?xml version="1.0"?>
<rss version="2.0" xmlns:blogChannel="http://backend.userland.com/blogChannelModule">
  <channel>
    <title>Scripting News</title>
    <link>http://www.scripting.com/</link>
    <language>en-us</language>
    <blogChannel:blogRoll>http://radio.weblogs.com/0001015/userland/scriptingNewsLeftLinks.opml</blogChannel:blogRoll>
    <blogChannel:mySubscriptions>http://radio.weblogs.com/0001015/gems/mySubscriptions.opml</blogChannel:mySubscriptions>
    <blogChannel:blink>http://diveintomark.org/</blogChannel:blink>
    <copyright>Copyright 1997-2002 Dave Winer</copyright>
    <lastBuildDate>Mon, 30 Sep 2002 11:00:00 GMT</lastBuildDate>
    <docs>http://backend.userland.com/rss</docs>
    <generator>Radio UserLand v8.0.5</generator>
    <category domain="Syndic8">1765</category>
    <managingEditor>dave@userland.com</managingEditor>
    <webMaster>dave@userland.com</webMaster>
    <ttl>40</ttl>
    <item>
      <description>&quot;rssflowersalignright&quot;With any luck we should have one or two more days of namespaces stuff here on Scripting News. It feels like it's winding down. Later in the week I'm going to a &lt;a href=&quot;http://harvardbusinessonline.hbsp.harvard.edu/b02/en/conferences/conf_detail.jhtml?id=s775stg&amp;pid=144XCF&quot;&gt;conference&lt;/a&gt; put on by the Harvard Business School. So that should change the topic a bit. The following week I'm off to Colorado for the &lt;a href=&quot;http://www.digitalidworld.com/conference/2002/index.php&quot;&gt;Digital ID World&lt;/a&gt; conference. We had to go through namespaces, and it turns out that weblogs are a great way to work around mail lists that are clogged with &lt;a href=&quot;http://www.userland.com/whatIsStopEnergy&quot;&gt;stop energy&lt;/a&gt;. I think we solved the problem, have reached a consensus, and will be ready to move forward shortly.</description>
      <pubDate>Mon, 30 Sep 2002 01:56:02 GMT</pubDate>
      <guid>http://scriptingnews.userland.com/backissues/2002/09/29#When:6:56:02PM</guid>
      <category><![CDATA[link]]></category>
      </item>
    </channel>
  </rss>
"""
        )
        self.assertIsNotNone(feed)
        self.assertEqual(feed.title, "Scripting News")
        self.assertEqual(feed.url, "http://www.scripting.com/")
        self.assertEqual(feed.description, None)
        self.assertIsInstance(feed.update, dt)
        self.assertIsInstance(feed._data, dict)
        self.assertIn('language', feed._data)
        self.assertIsInstance(feed.items, list)
        self.assertTrue(len(feed.items) > 0)
        self.assertEqual(feed.items[0].title, None)
        self.assertTrue('"rssflowersalignright"With any' in feed.items[0].content)
        self.assertEqual(feed.items[0].url, None)
        self.assertEqual(
            feed.items[0].id,
            "http://scriptingnews.userland.com/backissues/2002/09/29#When:6:56:02PM",
        )
        self.assertIsInstance(feed.items[0].update, dt)
        self.assertIsInstance(feed.items[0]._data, dict)
        self.assertIsInstance(feed.items[0].categories, list)
        self.assertTrue(len(feed.items[0].categories) > 0)
        self.assertEqual(feed.items[0].categories[0], "link")

    def test_generate(self):
        feed = rss.parse_file("tests/wikipedia-rss.xml")
        self.assertIsNotNone(feed)
        xml = rss.generate(feed)
        self.assertIsInstance(xml, str)
        self.assertTrue("<?xml version=" in xml)
        self.assertTrue("encoding=" in xml)
        self.assertTrue("<rss xmlns:" in xml)
        self.assertTrue("<channel>" in xml)
        self.assertTrue(
            "<link>https://en.wikipedia.org/w/index.php?title=RSS&amp;action=history</link>" in xml
        )
        self.assertTrue(
            "<description>Revision history for this page on the wiki</description>" in xml
        )
        self.assertTrue("<generator>MediaWiki 1.35.0-wmf.14</generator>" in xml)
        self.assertTrue("<pubDate>Tue, 14 Jan 2020" in xml)
        self.assertTrue("<title>Calbow: /* Current usage */ rewording</title>" in xml)
        self.assertTrue(
            "<link>https://en.wikipedia.org/w/index.php?title=RSS&amp;diff=924206591&amp;oldid=prev</link>"
            in xml
        )
        self.assertTrue(
            "<guid>https://en.wikipedia.org/w/index.php?title=RSS&amp;diff=924206591&amp;oldid=prev</guid>"
            in xml
        )
        self.assertTrue("<dc:creator>Calbow</dc:creator>" in xml)
        self.assertTrue('<p><span dir="auto"><span class="autocomment">Current' in xml)

    def test_unprintable(self):
        feed = Feed(title="Bad\u001AChar")
        xml = rss.generate(feed)
        self.assertNotIn("\u001A", xml)

if __name__ == '__main__':
    unittest.main()