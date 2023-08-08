
.. _user:

User guide
========================

Quickstart
----------

Parsing
^^^^^^^

To parse a feed, select the corresponding parser::

   feed = feedendum.rss.parse_text(file_path)
   feed = feedendum.atom.parse_text(file_path)
   feed = feedendum.rdf.parse_text(file_path)

You can also use ``parse_file`` (or ``parse_url`` if ``requests`` library is available).

Reading and editing
^^^^^^^^^^^^^^^^^^^

Feed and its fields are available as attribute in the :class:`Feed <feedendum.Feed>` class.

Feed items and their fields are available as attribute in the :class:`FeedItem <feedendum.FeedItem>` class.


Output
^^^^^^

To save a feed, use the corresponding namespace::

   xml_string = feedendum.rss.generate(feed)
   xml_string = feedendum.atom.generate(feed)
   xml_string = feedendum.rdf.generate(feed)


Examples
--------


Creating a feed
^^^^^^^^^^^^^^^

:class:`Feed <feedendum.Feed>` and :class:`FeedItem <feedendum.FeedItem>`  are a dataclasses, so::

   feed = feedendum.feed.Feed(
            title="Title",
            url="https://example.org",
            description="Example description",
            update=datetime.datetime.now(),
   )
   feed.items.append(
      feedendum.feed.FeedItem(
         url="https://example.org/1",
         title="Item 1",
         content="<p>Text</p>", categories=["Tests"]
      )
   )

Or step by step::

   feed = feedendum.feed.Feed()
   feed.title = "Title"
   feed.url = "https://example.org"
   feed.description = "Example description"
   feed.update = datetime.datetime.now()
   
   feeditem =  feedendum.feed.FeedItem()
   feeditem.url = "https://example.org/1"
   feeditem.title="Item 1"
   feeditem.content="<p>Text</p>"
   feeditem.categories=["Tests"]
   feed.items.append(feeditem)

Non standard attributes
^^^^^^^^^^^^^^^^^^^^^^^

Use ``Feed._data`` or ``FeedItem._data`` to manipulate non standard attributes,
remember to add the corresponding XML namespace, if needed::

   feed._data["{http://www.itunes.com/dtds/podcast-1.0.dtd}author"] = \
      "Podcast author"

Attributes are prefixed by `@`, text chilren mixed with other elements are prefixed by '#'
(but this) should not happen in a feed.


   >>> feedendum.rss.parse_url("https://gist.githubusercontent.com/timendum/871f455d2d4ad4b382b935a42ec8ad29/raw/0e8a4d0da6af9a982341f28f25dc92fb8c96254f/podcast.xml")

Generates::

   Feed(
      description="La guida di un'appassionata dei famosi quadrupedi a strisce.",
      title='Podcast Zebra di Dafna',
      url='https://www.example.com/podcasts/dafnas-zebras/',
      items=[
         FeedItem(
            content="Dieci convinzioni errate sulla cura, l'alimentazione e la riproduzione di questi adorabili animali a strisce.",
            title='10 miti sulle zebre come animali domestici',
            id='dzpodtop10',
            update=datetime.datetime(2017, 3, 14, 12, 0, tzinfo=datetime.timezone.utc),
            _data={
               'enclosure': {
                  '@url': 'https://www.example.com/podcasts/dafnas-zebras/audio/toptenmyths.mp3',
                  '@type': 'audio/mpeg',
                  '@length': '34216300'},
               '{http://www.itunes.com/dtds/podcast-1.0.dtd}duration': '30:00'
            }),
            FeedItem(
               content='Mantenere pulita la tua zebra è un lavoraccio, ma ne vale la pena.',
               title='Cura e manutenzione delle strisce',
               id='dzpodclean',
               update=datetime.datetime(2017, 2, 24, 12, 0, tzinfo=datetime.timezone.utc),
               _data={
                  'enclosure': {
                     '@url': 'https://www.example.com/podcasts/dafnas-zebras/audio/cleanstripes.mp3',
                     '@type': 'audio/mpeg',
                     '@length': '26004388'},
                  '{http://www.itunes.com/dtds/podcast-1.0.dtd}duration': '22:48'}
               )],
      _data={
         '{http://www.itunes.com/dtds/podcast-1.0.dtd}owner': {
            '{http://www.itunes.com/dtds/podcast-1.0.dtd}email': 'dafna@example.com'},
            '{http://www.itunes.com/dtds/podcast-1.0.dtd}author': 'Dafna',
            '{http://www.itunes.com/dtds/podcast-1.0.dtd}image': {
               '@href': 'https://www.example.com/podcasts/dafnas-zebras/img/dafna-zebra-pod-logo.jpg'},
               'language': 'it-it'
      }
   )
