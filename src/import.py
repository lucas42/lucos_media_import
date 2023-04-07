#! /usr/local/bin/python3

import os, sys
from logic import scan_file
from loganne import loganneRequest
from schedule_tracker import updateScheduleTracker


## Make sure required environment varible is set
if not os.environ.get("MEDIA_DIRECTORY"):
	sys.exit("\033[91mMEDIA_DIRECTORY not set\033[0m")
dirpath = os.environ.get("MEDIA_DIRECTORY")

if not os.path.isdir(dirpath):
	sys.exit("\033[91mMEDIA_DIRECTORY \""+dirpath+"\" is not a directory\033[0m")

## Make sure only running once at a time, using lockfile
try:
	lockfile = open("import.lock", "r")
	pid = lockfile.read()
	lockfile.close()
	if os.path.exists("/proc/"+pid+"/"): # Not fullproof as pids can be reused
		sys.exit("\033[91mImport already running (pid "+pid+")\033[0m")
except FileNotFoundError:
	pass
lockfile = open("import.lock", "w")
lockfile.write(str(os.getpid()))
lockfile.close()


# Record in loganne that the script has started
loganneRequest({
	"type":"import",
	"humanReadable": "Scanning for new tracks to include in media library",
	"dir": dirpath,
})

errorCount = 0

print("Starting scan of "+dirpath)
for root, dirs, files in os.walk(dirpath):

	# Ignore hidden files and directories
	files = [f for f in files if not f[0] == '.']
	dirs[:] = [d for d in dirs if not d[0] == '.']
	for name in files:
		try:
			path = os.path.join(root, name)
			scan_file(path)
		except:
			errorCount += 1

updateScheduleTracker(success=(errorCount == 0), message="Import encountered "+str(errorCount)+" errors")

os.remove("import.lock")
