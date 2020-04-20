#!/bin/sh
set -e
printenv > .env
mkfifo /var/log/cron.log
service cron start;
cat < /var/log/cron.log;