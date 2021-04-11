FROM python:3

WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y pipenv libtag1-dev libchromaprint-tools ffmpeg cron

RUN echo "1 17 * * 0 root cd `pwd` && pipenv run python -u import.py >> /var/log/cron.log 2>&1" > /etc/cron.d/import
COPY cron.sh .

COPY Pipfile* ./
RUN pipenv install
COPY import.py .

CMD [ "./cron.sh"]