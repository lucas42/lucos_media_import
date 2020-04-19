# lucos_media_import
Script to import media metadata from files on disk

## Dependencies

* docker
* docker-compose

## Build-time Dependencies

* [python 3](https://www.python.org/download/releases/3.0/)
* [pipenv](https://github.com/pypa/pipenv)
* [chromaprint](https://acoustid.org/chromaprint)

## Running
`nice -19 docker-compose up -d --no-build`

## Running locally

Run `pipenv install` to setup

`pipenv run python import.py`


## Environment Variables

* _**MEDIA_DIRECTORY**_ The directory in which to look for audio files to import
* _**MEDIA_PREFIX**_ Added to the start of each track's local path to form the url for that track
* _**MEDIA_API**_ URL of an instance of [lucos_media_metadata_api](https://github.com/lucas42/lucos_media_metadata_api)