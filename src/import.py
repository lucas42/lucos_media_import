#! /usr/local/bin/python3

import os, sys, signal
from logic import scan_insert_file
from loganne import loganneRequest
from schedule_tracker import updateScheduleTracker
from checkpoint import load_checkpoint, save_checkpoint, clear_checkpoint
from datetime import datetime


## Make sure required environment variable is set
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

# Load checkpoint — resume from where a previous interrupted run left off
checkpoint = load_checkpoint()
is_resuming = checkpoint["root_files_done"] or len(checkpoint["completed_dirs"]) > 0

errorCount = 0

# Install SIGTERM handler: flush checkpoint and post failure to schedule-tracker before exiting.
# This ensures interrupted runs leave an honest alert state rather than going silent.
def handle_sigterm(signum, frame):
	print("["+datetime.now().isoformat()+"] SIGTERM received — flushing checkpoint and exiting", file=sys.stderr)
	save_checkpoint(checkpoint)
	updateScheduleTracker(success=False, message="Import interrupted by SIGTERM after "+str(errorCount)+" errors", frequency=(7 * 24 * 60 * 60))
	os.remove("import.lock")
	sys.exit(0)

signal.signal(signal.SIGTERM, handle_sigterm)

# Record in loganne that the script has started
if is_resuming:
	loganneRequest({
		"type": "import",
		"humanReadable": "Resuming interrupted scan of media library",
		"dir": dirpath,
	})
	print("["+datetime.now().isoformat()+"] Resuming interrupted scan of "+dirpath)
else:
	loganneRequest({
		"type": "import",
		"humanReadable": "Scanning for new tracks to include in media library",
		"dir": dirpath,
	})
	print("["+datetime.now().isoformat()+"] Starting scan of "+dirpath)

# Get top-level entries in sorted order (deterministic, so resume skips the right dirs)
top_level_entries = sorted([e for e in os.listdir(dirpath) if not e.startswith('.')])

# Step 1: process files directly in the root directory (if not already done)
if not checkpoint["root_files_done"]:
	for name in top_level_entries:
		path = os.path.join(dirpath, name)
		if not os.path.isfile(path):
			continue
		try:
			scan_insert_file(path)
		except Exception as error:
			print("\033[91m ["+datetime.now().isoformat()+"] "+type(error).__name__ + " " + str(error) + " " + path + "\033[0m", file=sys.stderr)
			errorCount += 1
	checkpoint["root_files_done"] = True
	save_checkpoint(checkpoint)

# Step 2: walk each top-level subdirectory, checkpointing after each one completes.
# Files added/removed mid-traversal are benign for a "find new files" pass — they'll
# be caught (or ignored) on the following week's traversal.
for top_dir in top_level_entries:
	top_dir_path = os.path.join(dirpath, top_dir)
	if not os.path.isdir(top_dir_path):
		continue
	if top_dir in checkpoint["completed_dirs"]:
		print("["+datetime.now().isoformat()+"] Skipping already-completed directory: "+top_dir)
		continue
	print("["+datetime.now().isoformat()+"] Processing directory: "+top_dir)
	for root, dirs, files in os.walk(top_dir_path):
		# Ignore hidden files and directories
		files = [f for f in files if not f[0] == '.']
		dirs[:] = [d for d in dirs if not d[0] == '.']
		for name in files:
			try:
				path = os.path.join(root, name)
				scan_insert_file(path)
			except Exception as error:
				print("\033[91m ["+datetime.now().isoformat()+"] "+type(error).__name__ + " " + str(error) + " " + path + "\033[0m", file=sys.stderr)
				errorCount += 1
	checkpoint["completed_dirs"].append(top_dir)
	save_checkpoint(checkpoint)

# Clean completion: clear the checkpoint so the next run starts fresh,
# and post result to schedule-tracker.
clear_checkpoint()
updateScheduleTracker(success=(errorCount == 0), message="Import encountered "+str(errorCount)+" errors", frequency=(7 * 24 * 60 * 60))

os.remove("import.lock")
