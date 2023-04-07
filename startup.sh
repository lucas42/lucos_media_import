#!/bin/sh
set -e

# printenv doesn't quote values, which is a problem if one contains a space
# So do some hacky regexes to quote stuff
printenv | sed 's/"/\\"/g' | sed 's/=/="/g' | sed 's/$/"/g' > .env
[ -p /var/log/cron.log ] || mkfifo /var/log/cron.log
service cron start
cat <> /var/log/cron.log