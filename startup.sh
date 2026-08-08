#!/bin/sh
set -e

# printenv doesn't quote values, which is a problem if one contains a space
# So do some hacky regexes to quote stuff
printenv | sed 's/"/\\"/g' | sed 's/=/="/g' | sed 's/$/"/g' > .env
[ -p /var/log/cron.log ] || mkfifo /var/log/cron.log
service cron start

# docker stop only sends SIGTERM to PID 1 (this shell) — cron's children never see it,
# so a scan is later SIGKILLed outright when the grace period expires and the whole PID
# namespace is torn down. Forward SIGTERM to any in-progress job so its own handler gets
# a chance to flush a checkpoint / post an honest failure first. See #173.
shutdown() {
	echo "[startup.sh] SIGTERM received - forwarding to running import job"
	pkill -TERM -f "python -u import\.py" 2>/dev/null || true
	pkill -TERM -f "python -u new_files\.py" 2>/dev/null || true
	deadline=$(($(date +%s) + 8))
	while pgrep -f "python -u (import|new_files)\.py" >/dev/null 2>&1 && [ "$(date +%s)" -lt "$deadline" ]; do
		sleep 0.2
	done
	exit 0
}
trap shutdown TERM

cat <> /var/log/cron.log &
wait $!
