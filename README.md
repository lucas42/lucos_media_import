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

## Running script without cron

To test the script logic with worrying about cronjobs.

Set `entrypoint: pipenv run python -u import.py` in the docker-compose file (or equivalent)

## Running locally

Run `pipenv install` to setup

`pipenv run python import.py`

## Testing

Doesn't use a proper testing framework.  However, run
`docker compose up test --build --exit-code-from test`
which will check various calls to the scan_file() function, relying on files in the `test_tracks` directory

## Environment Variables
For local development, these should be stored in a .env file

* _**MEDIA_DIRECTORY**_ The directory in which to look for audio files to import
* _**MEDIA_PREFIX**_ Added to the start of each track's local path to form the url for that track
* _**MEDIA_API**_ URL of an instance of [lucos_media_metadata_api](https://github.com/lucas42/lucos_media_metadata_api)

## File structure

* `Dockerfile`, `Pipfile`, `Pipfile.lock` and the `.cirleci` directory are used at build time
* `src` directory holds the python source code
  - `logic.py` holds the logic for evaluating an audio track on the filesystem and adding an appropriate entry in the metadata API.
  - `import.py` is script which iterates through all files in the _MEDIA_DIRECTORY_ and imports them to the API.
  - `test.py` does some simple checks on the logic in `src/logic.py`.
* `startup.sh` ensures the cron daemon is running with the right environment set up and sharing its logs in a way that get surfaced to Docker
* `test_tracks` a collection of audio tracks used for testing.  Not included in the final docker image