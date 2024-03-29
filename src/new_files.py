#! /usr/local/bin/python3

import os, sys
from datetime import datetime, timedelta
from logic import scan_insert_file
from schedule_tracker import updateScheduleTracker


## Make sure required environment varible is set
if not os.environ.get("MEDIA_DIRECTORY"):
	sys.exit("\033[91mMEDIA_DIRECTORY not set\033[0m")
dirpath = os.environ.get("MEDIA_DIRECTORY")

if not os.path.isdir(dirpath):
	sys.exit("\033[91mMEDIA_DIRECTORY \""+dirpath+"\" is not a directory\033[0m")

## Make sure only running once at a time, using lockfile
try:
	lockfile = open("new_files.lock", "r")
	pid = lockfile.read()
	lockfile.close()
	if os.path.exists("/proc/"+pid+"/"): # Not fullproof as pids can be reused
		sys.exit("\033[91mNew files import already running (pid "+pid+")\033[0m")
except FileNotFoundError:
	pass
lockfile = open("new_files.lock", "w")
lockfile.write(str(os.getpid()))
lockfile.close()

# Checks with a file or directory has recently been modified (based on `ctime`)
# Returns boolean
def isRecent(root, file):
	# Ignore hidden files regardless of recency
	if file[0] == ".":
		return False
	path = os.path.join(root, file)
	last_modified = datetime.fromtimestamp(os.path.getctime(path))
	file_age = datetime.now() - last_modified
	return file_age < timedelta(minutes=2)

errorCount = 0

print("Starting new_files scan of "+dirpath)
for root, dirs, files in os.walk(dirpath):
	# Build a list of directories which have recently been modified
	# Ensuring os.walk dosen't decend into the other directories
	dirs[:] = [d for d in dirs if isRecent(root, d)]
	for name in files:
		try:
			if isRecent(root, name):
				scan_insert_file(os.path.join(root, name))
		except Exception as error:
			print("\033[91m"+type(error).__name__ + " " + str(error) + " " + name + "\033[0m")
			errorCount += 1

updateScheduleTracker(success=(errorCount == 0), message="New files import encountered "+str(errorCount)+" errors", system="lucos_media_import_new_files", frequency=60)

os.remove("new_files.lock")
