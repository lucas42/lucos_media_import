import os, sys, urllib
import taglib, acoustid, datetime
from media_api import insertTrack


## Make sure required environment varibles are set
if not os.environ.get("MEDIA_PREFIX"):
	sys.exit("\033[91mMEDIA_PREFIX not set\033[0m")
mediaprefix = os.environ.get("MEDIA_PREFIX")

verbose = False

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
			raise Exception("Empty Track")
		if duration < 1:
			raise Exception("Track with duration less than 1 second")
		trackdata = {
			"duration": int(duration),
			"tags": tags,
			"url": trackurl,
		}
		return (fingerprint, trackdata)
	except Exception as error:
		raise error

def scan_insert_file(path):
	(fingerprint, trackdata) = scan_file(path)
	insertTrack(fingerprint, trackdata)