import os, sys, urllib
import requests, taglib, acoustid, json, datetime


## Make sure required environment varibles are set
if not os.environ.get("MEDIA_PREFIX"):
	sys.exit("\033[91mMEDIA_PREFIX not set\033[0m")
mediaprefix = os.environ.get("MEDIA_PREFIX")
if not os.environ.get("MEDIA_API"):
	sys.exit("\033[91mMEDIA_API not set\033[0m")
apiurl = os.environ.get("MEDIA_API")

verbose = False

def log(message, error=False, debug=False):
	if (debug and not verbose):
		return
	if error:
		print("\033[91m** Error ** "+str(message)+"\033[0m", file=sys.stderr)
	else:
		print ("\033[92m"+str(message)+"\033[0m")

def scan_file(path):
	try:
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
		if "title" not in tags:
			tags["title"] = path.split("/")[-1].rsplit(".", 1)[0]

		duration, fingerprint = acoustid.fingerprint_file(path, maxlength=60)
		if fingerprint.decode('UTF-8') in ["AQAAAA", "AQAAAQkz9UsCAQ"]:
			log("Skipping empty track " + trackurl, error=True)
			return
		if duration < 1:
			log("Track with duration less than 1 second " + trackurl, error=True)
			raise Exception("Track with duration less than 1 second")
		trackdata = {
			"duration": int(duration),
			"tags": tags,
			"url": trackurl,
		}
		log(fingerprint.decode("UTF-8") + ", " + str(trackdata), debug=True)
		trackresult = requests.put(apiurl+"/v2/tracks", params={"fingerprint": fingerprint.decode('UTF-8')}, data=json.dumps(trackdata), allow_redirects=False, headers={"If-None-Match": "*"})
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
		raise error