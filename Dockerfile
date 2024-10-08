FROM python:3.10

WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y libchromaprint-tools ffmpeg cron

# Version 2.0 of taglib isn't yet packaged for debian on armv7l, so try building from source
RUN apt-get install -y cmake libutfcpp-dev
RUN curl "https://taglib.org/releases/taglib-2.0.tar.gz" | tar -zxv
WORKDIR /usr/src/app/taglib-2.0
RUN cmake -DCMAKE_INSTALL_PREFIX=/usr/local -DCMAKE_BUILD_TYPE=Release .
RUN make
RUN make install
WORKDIR /usr/src/app

# Every week, run a full scan of all files in the media library
RUN echo "30 12 * * 6 root cd `pwd` && pipenv run python -u import.py >> /var/log/cron.log 2>&1" > /etc/cron.d/import

# Every minutes, run a scan of files which have been recently added/modified
RUN echo "* * * * * root cd `pwd` && pipenv run python -u new_files.py >> /var/log/cron.log 2>&1" >> /etc/cron.d/import
COPY startup.sh .

RUN pip install pipenv
COPY Pipfile* ./
RUN pipenv install

COPY src/* ./

CMD [ "./startup.sh"]