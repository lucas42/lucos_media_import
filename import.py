#! /usr/local/bin/python3

import os, sys
import requests, taglib, acoustid
if len(sys.argv) < 3:
	exit("Usage: "+sys.argv[0]+" [media directory path] [media API url]")
dirpath = sys.argv[1]
apiurl = sys.argv[2]
verbose = False

for root, dirs, files in os.walk(dirpath):
	for name in files:
		try:
			path = os.path.join(root, name)
			song = taglib.File(path)
			tags = {}
			for key in song.tags:
				if len(song.tags[key]) < 1:
					continue
				tags[key.lower()] = song.tags[key][0]

			duration, fingerprint = acoustid.fingerprint_file(path, maxlength=60)
			if verbose:
				print (path, tags, duration, fingerprint.decode('UTF-8'))
			else:
				print (path)
		except OSError as error:
			if verbose:
				print (error, file=sys.stderr)