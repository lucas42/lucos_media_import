# lucos_media_import
Scans the filesystem for audio files and writes metadata about them to an API.

## Dependencies

* docker
* docker-compose

## Remote Dependencies

* [lucos_media_metadata_api](https://github.com/lucas42/lucos_media_metadata_api)

## Build-time Dependencies (Installed by Dockerfile)

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

## File structure

* `Dockerfile`, `Pipfile`, `Pipfile.lock` and the `.cirleci` directory are used at build time
* `cron.sh` ensures the cron daemon is running with the right environment set up and sharing its logs in a way that get surfaced to Docker
* `import.py` holds the logic for the import itself.