FROM python:3.13

WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y libchromaprint-tools ffmpeg cron

# Version 2.0 of taglib isn't yet packaged for debian on armv7l, so try building from source
RUN apt-get install -y cmake libutfcpp-dev
RUN curl "https://taglib.org/releases/taglib-2.0.2.tar.gz" | tar -zxv
WORKDIR /usr/src/app/taglib-2.0.2
RUN cmake -DCMAKE_INSTALL_PREFIX=/usr/local -DCMAKE_BUILD_TYPE=Release -DCMAKE_POSITION_INDEPENDENT_CODE=ON -DWITH_ZLIB=OFF .
RUN make
RUN make install
WORKDIR /usr/src/app

# Every week, run a full scan of all files in the media library
RUN echo "30 12 * * 6 root cd `pwd` && /usr/local/bin/pipenv --quiet run python -u import.py >> /var/log/cron.log 2>&1" > /etc/cron.d/import

# Every minutes, run a scan of files which have been recently added/modified
RUN echo "* * * * * root cd `pwd` && /usr/local/bin/pipenv --quiet run python -u new_files.py >> /var/log/cron.log 2>&1" >> /etc/cron.d/import
COPY startup.sh .

RUN pip install pipenv
COPY Pipfile* ./
RUN pipenv install

COPY test_tracks ./test_tracks
COPY src/* ./

CMD [ "./startup.sh"]