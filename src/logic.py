import os, sys, urllib
import taglib, acoustid
from media_api import insertTrack


## Make sure required environment varibles are set
if not os.environ.get("MEDIA_PREFIX"):
	sys.exit("\033[91mMEDIA_PREFIX not set\033[0m")
mediaprefix = os.environ.get("MEDIA_PREFIX")

verbose = False

def scan_file(path):
	trackurl = mediaprefix + urllib.parse.quote(path, safe='/ ')
	try:
		filemetadata = taglib.File(path)
	except OSError:
		return (None, None)
	tags = {}
	for key, values in filemetadata.tags.items():
		if len(values) < 1:
			continue
		key = key.lower()
		value = " & ".join(values)
		if key not in ["title", "album", "artist", "year", "genre", "comment", "lyrics"]:
			continue
		tags[key] = value

	# If there's no title in the ID3 tags, default to filename (ignoring extension)
	if "title" not in tags:
		tags["title"] = path.split("/")[-1].rsplit(".", 1)[0]

	# Many tracks from compilation albums are tagged with an artist of "Various" - this is really unhelpful in a library context, so ignore this tag
	if "artist" in tags and tags["artist"] == "Various":
		del tags["artist"]

	# Check whether the file is in a folder of known provenance - if so, set the provenance tag
	provenance_mapping = {
		'/ceol srl/bandcamp/': 'bandcamp',
		'/ceol srl/7digital/': '7digital',
		'/ceol srl/Amazon Music/': 'amazon',
		'/ceol srl/newgrounds/': 'newgrounds',
		'/ceol srl/iTunes/': 'itunes',
	}
	for path_match, provenance_tag in provenance_mapping.items():
		if path_match in path:
			tags["provenance"] = provenance_tag

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

def scan_insert_file(path):
	(fingerprint, trackdata) = scan_file(path)
	if trackdata is None:
		return
	insertTrack(fingerprint, trackdata)