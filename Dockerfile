FROM python:3.12-alpine

WORKDIR /usr/src/app

#RUN apt-get update && apt-get install -y pipenv libtag1-dev libchromaprint-tools ffmpeg cron
RUN apk add taglib-dev chromaprint ffmpeg
RUN pip install pipenv
# Default version of sed in alpine isn't the full GNU one, so install that
RUN apk add sed

# Every week, run a full scan of all files in the media library
# Every minute, run a scan of files which have been recently added/modified
RUN echo -e "30 12 * * 6 cd `pwd` && pipenv run python -u import.py >> /var/log/cron.log 2>&1 \n\
* * * * * cd `pwd` && pipenv run python -u new_files.py >> /var/log/cron.log 2>&1 \
" | crontab -

COPY startup.sh .

COPY Pipfile* ./
RUN pipenv install

COPY src/* ./

CMD [ "./startup.sh"]