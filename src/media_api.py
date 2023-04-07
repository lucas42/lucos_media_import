import json, sys, os, requests

if not os.environ.get("MEDIA_API"):
	sys.exit("\033[91mMEDIA_API not set\033[0m")
apiurl = os.environ.get("MEDIA_API")
if (apiurl.endswith("/")):
	sys.exit("\033[91mDon't include a trailing slash in the API url\033[0m")

verbose = False

def log(message, error=False, debug=False):
	if (debug and not verbose):
		return
	if error:
		print("\033[91m** Error ** "+str(message)+"\033[0m", file=sys.stderr)
	else:
		print ("\033[92m"+str(message)+"\033[0m")

def insertTrack(fingerprint, trackdata):
	log(fingerprint.decode("UTF-8") + ", " + str(trackdata), debug=True)
	trackresult = requests.put(apiurl+"/v2/tracks", params={"fingerprint": fingerprint.decode('UTF-8')}, data=json.dumps(trackdata), allow_redirects=False, headers={"If-None-Match": "*"})
	if trackresult.ok:
		trackAction = trackresult.headers.get("Track-Action")
		if (trackAction == "noChange"):
			log("No change for track " + trackdata["url"], debug=True)
		else:
			log(trackAction + " " + trackdata["url"])
	else:
		raise Exception("HTTP Status code "+str(trackresult.status_code)+" returned by API: " +  trackresult.text.rstrip() + " <" + trackdata["url"] + ">")