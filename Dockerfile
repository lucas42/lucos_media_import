FROM python:3.14
ARG VERSION
ENV VERSION=$VERSION
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y --no-install-recommends libchromaprint-tools ffmpeg cron libtag1-dev

# Every week, run a full scan of all files in the media library
RUN echo "45 00 * * Thu root cd `pwd` && /usr/local/bin/pipenv --quiet run python -u import.py >> /var/log/cron.log 2>&1" > /etc/cron.d/import

# Every minute, run a scan of files which have been recently added/modified
RUN echo "* * * * * root cd `pwd` && /usr/local/bin/pipenv --quiet run python -u new_files.py >> /var/log/cron.log 2>&1" >> /etc/cron.d/import
COPY startup.sh .

RUN pip install pipenv
COPY Pipfile* ./
RUN pipenv install

COPY test_tracks ./test_tracks
COPY src/* ./

CMD [ "./startup.sh"]