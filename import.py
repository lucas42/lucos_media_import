#! /usr/local/bin/python3

import os, sys
import requests, taglib, acoustid, json
if len(sys.argv) < 3:
	exit("Usage: "+sys.argv[0]+" [media directory path] [track url prefix] [media API url]")
dirpath = sys.argv[1]
mediaprefix = sys.argv[2]
apiurl = sys.argv[3]
verbose = False

for root, dirs, files in os.walk(dirpath):
	for name in files:
		try:
			path = os.path.join(root, name)
			trackurl = mediaprefix + path
			song = taglib.File(path)
			tags = {}
			for key in song.tags:
				if len(song.tags[key]) < 1:
					continue
				tags[key.lower()] = song.tags[key][0]

			duration, fingerprint = acoustid.fingerprint_file(path, maxlength=60)
			if verbose:
				print (trackurl, tags, duration, fingerprint.decode('UTF-8'))
			else:
				print (trackurl)
			trackdata = {
				"url": trackurl,
				"duration": int(duration),
				"tags": tags,
			}
			result = requests.put(apiurl+"/tracks?fingerprint="+fingerprint.decode('UTF-8'), data=json.dumps(trackdata), allow_redirects=False, headers={"If-None-Match": "*"})
			if result.ok:
				if verbose:
					print ("\033[92mTrack Updated: " +  result.text + "\033[0m")
			else:
				print ("\033[91m** Error ** HTTP Status code "+str(result.status_code)+" returned by API: " +  result.text + "\033[0m")
		except OSError as error:
			if verbose:
				print (error, file=sys.stderr)