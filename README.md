# feedendum
A python library to parse and generate RSS or atom feeds.

## Features

This module can:

* parse RSS text and file
* parse RDF (RSS v1.0) text and file
* parse Atom text and file
* read an url if `requests` is installed
* access standard fields via `feed` class and `feed.item` list
* access non-standard fields via `_data` dict
* create arbitrary feed
* modify an existing feed
* generate a RSS text
* generate a RDF (RSS v1.0) text
* generate an Atom text
* preserve all data parsed, even in custom fields, when generating a RSS/Atom text

## Usage

### Parsing a file

For RSS:

    feed = feedendum.from_rss_file(file_path)
    feed = feedendum.from_rss_text(txt)

For RDF (RSS v1.0): 

    feed = feedendum.from_rdf_file(file_path)
    feed = feedendum.from_rdf_text(txt)

For Atom:

    feed = feedendum.from_atom_file(file_path)
    feed = feedendum.from_atom_text(txt)

### Accessing to parsed data

Standard fields:

    print("Title", feed.title)
    print("First entry title", feed.items[0].title)

For other fields, not defined in `Feed` class:

    print("Extra attributes in the feed", feed._data)
    print("Extra attributes in the first entry", feed.items[0]._data)

### Writing a file

For RSS:

    feedendum.to_rss_string(feed)

For RDF (RSS v1.0):

    feedendum.to_rdf_string(feed)

For Atom:

    feedendum.to_atom_string(feed)
