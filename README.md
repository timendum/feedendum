# feedendum
A python library to parse and generate RSS or atom feeds.

## Features

This module can:

* parse and generate RSS feeds
* parse and generate RDF (RSS v1.0) feeds (thanks to @inigoserna)
* parse and generate Atom feeds
* access standard fields via `feed` class and `feed.item` list
* preserve all data parsed, even in custom fields, when generating a RSS/Atom/RDF text
* read an url if `requests` is installed
* access non-standard fields via `_data` dict
* create arbitrary feed
* modify an existing feed

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


## Development

This package is developed with `uv`.

### Setup

Just run:
    
    uv sync

### Tests

Done via unittest

    uv run python -m unittest discover -s tests

### Build

With build and hatchling

    uvx --from build  pyproject-build --installer uv

### Publish

To publish to PyPi

    uvx twine upload dist/*