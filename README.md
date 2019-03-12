# lucos_media_import
Script to import media metadata from files on disk

## Requirements

* [python 3](https://www.python.org/download/releases/3.0/)
* [pipenv](https://github.com/pypa/pipenv)
* [chromaprint](https://acoustid.org/chromaprint)

## Setup

Run `pipenv install`

## Running

`pipenv run python import.py [media directory path] [track url prefix] [media API url]`

* `media directory path` is the directory in which to look for audio files to import
* `track url prefix` is added to the start of each track's local path to form the url for that track
* `media API url` is the url of an instance of [lucos_media_metadata_api](https://github.com/lucas42/lucos_media_metadata_api)