#! /usr/local/bin/python3

import os, sys, urllib
import requests, taglib, acoustid, json, datetime

## Make sure required environment varibles are set
if not os.environ.get("MEDIA_DIRECTORY"):
	sys.exit("\033[91mMEDIA_DIRECTORY not set\033[0m")
dirpath = os.environ.get("MEDIA_DIRECTORY")
if not os.environ.get("MEDIA_PREFIX"):
	sys.exit("\033[91mMEDIA_PREFIX not set\033[0m")
mediaprefix = os.environ.get("MEDIA_PREFIX")
if not os.environ.get("MEDIA_API"):
	sys.exit("\033[91mMEDIA_API not set\033[0m")
apiurl = os.environ.get("MEDIA_API")

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

verbose = False

def log(message, error=False, debug=False):
	if (debug and not verbose):
		return
	if error:
		print("\033[91m** Error ** "+str(message)+"\033[0m", file=sys.stderr)
	else:
		print ("\033[92m"+str(message)+"\033[0m")

loganne_result = requests.post("https://loganne.l42.eu/events", json={"source":"lucos_media_import","type":"import","humanReadable":"Scanning for new tracks to include in media library","dir": dirpath}, allow_redirects=False)
if not loganne_result:
	log("Call to Loganne failed with "+str(loganne_result.status_code)+" response: " +  loganne_result.text.rstrip(), error=True)

errorCount = 0

log("Starting scan of "+dirpath)
for root, dirs, files in os.walk(dirpath):

	# Ignore hidden files and directories
	files = [f for f in files if not f[0] == '.']
	dirs[:] = [d for d in dirs if not d[0] == '.']
	for name in files:
		try:
			path = os.path.join(root, name)
			trackurl = mediaprefix + urllib.parse.quote(path, safe='/ ')
			filemetadata = taglib.File(path)
			tags = {}
			for key, values in filemetadata.tags.items():
				if len(values) < 1:
					continue
				key = key.lower()
				value = " & ".join(values)
				if key not in ["title", "album", "artist", "year", "genre", "comment", "lyrics"]:
					continue
				tags[key] = value

			# To begin with, as there's lots of files without an 'added' tag, use last modification date
			# on the filesystem to estimate when it was added to the media library
			# In future, the API should add this automatically for any new files (using current datetime)
			last_modified = datetime.datetime.fromtimestamp(os.path.getmtime(path))
			tags["added"] = last_modified.isoformat()

			# If there's no title in the ID3 tags, default to filename (ignoring extension)
			if not hasattr(tags, "title"):
				tags["title"] = path.split("/")[-1].rsplit(".", 1)[0]

			duration, fingerprint = acoustid.fingerprint_file(path, maxlength=60)
			if fingerprint.decode('UTF-8') in ["AQAAAA", "AQAAAQkz9UsCAQ"]:
				log("Skipping empty track " + trackurl, debug=True)
				continue
			if duration < 1:
				log("Track with duration less than 1 second " + trackurl, error=True)
				errorCount += 1
				continue
			trackdata = {
				"duration": int(duration),
				"tags": tags,
				"url": trackurl,
			}
			log(fingerprint.decode("UTF-8") + ", " + str(trackdata), debug=True)
			trackresult = requests.put(apiurl+"/tracks", params={"fingerprint": fingerprint.decode('UTF-8')}, data=json.dumps(trackdata), allow_redirects=False, headers={"If-None-Match": "*"})
			if trackresult.ok:
				trackAction = trackresult.headers.get("Track-Action")
				if (trackAction == "noChange"):
					log("No change for track " + trackurl, debug=True)
				else:
					log(trackAction + " " + trackurl)
			else:
				log("HTTP Status code "+str(trackresult.status_code)+" returned by API: " +  trackresult.text.rstrip() + " <" + trackurl + ">", error=True)
				errorCount += 1
		except OSError as error:
			log(error, error=True, debug=True)
		except Exception as error:
			log(type(error).__name__ + " " + str(error) + " " + name, error=True)
			errorCount += 1

# Save the current time as a global in the media API
summaryresult = requests.put(apiurl+"/globals/latest_import-timestamp", data=datetime.datetime.utcnow().isoformat().encode('utf-8'), allow_redirects=False)
if summaryresult.ok:
	log("Last import timestamp updated: " +  summaryresult.text.rstrip())
else:
	log("HTTP Status code "+str(summaryresult.status_code)+" returned by API: " +  summaryresult.text.rstrip(), error=True)
	errorCount += 1

# Save the number of errors as a global in the media API
summaryresult = requests.put(apiurl+"/globals/latest_import-errors", data=str(errorCount), allow_redirects=False)
if summaryresult.ok:
	log("Last import error count updated: " +  summaryresult.text.rstrip())
else:
	log("HTTP Status code "+str(summaryresult.status_code)+" returned by API: " +  summaryresult.text.rstrip(), error=True)
	errorCount += 1

os.remove("import.lock")
