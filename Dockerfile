FROM python:3.10

WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y pipenv libtag1-dev libchromaprint-tools ffmpeg cron

# Every week, run a full scan of all files in the media library
RUN echo "30 12 * * 6 root cd `pwd` && pipenv run python -u import.py >> /var/log/cron.log 2>&1" > /etc/cron.d/import

# Every minutes, run a scan of files which have been recently added/modified
RUN echo "* * * * * root cd `pwd` && pipenv run python -u new_files.py >> /var/log/cron.log 2>&1" >> /etc/cron.d/import
COPY startup.sh .

COPY Pipfile* ./
RUN pipenv install

COPY src/* ./

CMD [ "./startup.sh"]