#! /usr/local/bin/python3

import os, sys
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

loganne_result = requests.post("https://loganne.l42.eu/events", json={"source":"lucos_media_import","type":"import","humanReadable":"Scanning for new tracks to include in media library"}, allow_redirects=False)
if not loganne_result:
	print ("\033[91m** Error ** Call to Loganne failed with "+str(loganne_result.status_code)+" response: " +  loganne_result.text + "\033[0m")

verbose = False
errorCount = 0

for root, dirs, files in os.walk(dirpath):

	# Ignore hidden files and directories
	files = [f for f in files if not f[0] == '.']
	dirs[:] = [d for d in dirs if not d[0] == '.']
	for name in files:
		try:
			path = os.path.join(root, name)

			# In future, could use urllib.parse.quote for consistency
			# But for now do specific replacements for backwards-compatibility
			urlpath = path.replace("%", "%25")
			urlpath = urlpath.replace("#", "%23")
			trackurl = mediaprefix + urlpath
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

			duration, fingerprint = acoustid.fingerprint_file(path, maxlength=60)
			if fingerprint.decode('UTF-8') in ["AQAAAA", "AQAAAQkz9UsCAQ"]:
				if verbose:
					print("Skipping empty track", trackurl)
				continue
			if duration < 1:
				print("\033[91m** Error ** Track with duration less than 1 second ", trackurl, "\033[0m")
				errorCount += 1
				continue
			if verbose:
				print (trackurl, tags, duration, fingerprint.decode('UTF-8'))
			else:
				print (trackurl)
			trackdata = {
				"fingerprint": fingerprint.decode('UTF-8'),
				"duration": int(duration),
			}
			trackresult = requests.put(apiurl+"/tracks", params={"url": trackurl}, data=json.dumps(trackdata), allow_redirects=False, headers={"If-None-Match": "*"})
			if trackresult.ok:
				if verbose:
					print ("\033[92mTrack Updated: " +  trackresult.text + "\033[0m")
				trackid = trackresult.json()["trackid"]
				for key, value in tags.items():
					if verbose:
						print("Tag:", trackid, key, json.dumps(value))
					tagresult = requests.put(apiurl+"/tags/"+str(trackid)+"/"+key, data=value.encode('utf-8'), allow_redirects=False, headers={"If-None-Match": "*"})
					if tagresult.ok:
						if verbose:
							print ("\033[92mTag Updated: " +  tagresult.text + "\033[0m")
					else:
						print ("\033[91m** Error ** HTTP Status code "+str(tagresult.status_code)+" returned by API: " +  tagresult.text + "\033[0m")
						errorCount += 1
			else:
				print ("\033[91m** Error ** HTTP Status code "+str(trackresult.status_code)+" returned by API: " +  trackresult.text + "[fingerprint: " + fingerprint.decode('UTF-8') + " ]\033[0m")
				errorCount += 1

		except OSError as error:
			if verbose:
				print(error, file=sys.stderr)
		except Exception as error:
			print ("\033[91m", type(error).__name__, error, name, "\033[0m", file=sys.stderr)
			errorCount += 1

# Save the current time as a global in the media API
summaryresult = requests.put(apiurl+"/globals/latest_import-timestamp", data=datetime.datetime.utcnow().isoformat().encode('utf-8'), allow_redirects=False)
if summaryresult.ok:
	print ("\033[92mLast import timestamp updated: " +  summaryresult.text + "\033[0m")
else:
	print ("\033[91m** Error ** HTTP Status code "+str(summaryresult.status_code)+" returned by API: " +  summaryresult.text + "\033[0m")
	errorCount += 1

# Save the number of errors as a global in the media API
summaryresult = requests.put(apiurl+"/globals/latest_import-errors", data=str(errorCount), allow_redirects=False)
if summaryresult.ok:
	print ("\033[92mLast import error count updated: " +  summaryresult.text + "\033[0m")
else:
	print ("\033[91m** Error ** HTTP Status code "+str(summaryresult.status_code)+" returned by API: " +  summaryresult.text + "\033[0m")
	errorCount += 1

os.remove("import.lock")