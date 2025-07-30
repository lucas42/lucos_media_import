import json, sys, os, requests
from datetime import datetime

if not os.environ.get("MEDIA_API"):
	sys.exit("\033[91mMEDIA_API not set\033[0m")
apiurl = os.environ.get("MEDIA_API")
if (apiurl.endswith("/")):
	sys.exit("\033[91mDon't include a trailing slash in the API url\033[0m")

if not os.environ.get("KEY_LUCOS_MEDIA_METADATA_API"):
	sys.exit("\033[91mKEY_LUCOS_MEDIA_METADATA_API not set\033[0m")
apiKey = os.environ.get("KEY_LUCOS_MEDIA_METADATA_API")

trackKey = os.environ.get("TRACK_KEY", "fingerprint")

verbose = False

session = requests.Session()
retries = requests.adapters.Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
adapter = requests.adapters.HTTPAdapter(max_retries=retries)
session.mount(apiurl, adapter)

def log(message, error=False, debug=False):
	if (debug and not verbose):
		return
	if error:
		print("\033[91m ["+datetime.now().isoformat()+"] ** Error ** "+str(message)+"\033[0m", file=sys.stderr)
	else:
		print ("\033[92m ["+datetime.now().isoformat()+"] "+str(message)+"\033[0m")

def insertTrack(trackdata):
	url = trackdata["url"] # Used for Logging
	keyValue = trackdata[trackKey] # The primary key for sending to the API
	del trackdata[trackKey] # Don't include the primary key in the request body, as it'll be part of the URL parameters
	log(trackKey + "=" + keyValue + ", " + str(trackdata), debug=True)
	trackresult = session.put(apiurl+"/v2/tracks", params={trackKey: keyValue}, data=json.dumps(trackdata), allow_redirects=False, headers={"If-None-Match": "*", "Authorization":"key "+apiKey, 'User-Agent': "lucos_media_import"})
	if (trackresult.status_code == 400):
		log("Bad Request: "+trackresult.text, error=True)
	trackresult.raise_for_status()
	trackAction = trackresult.headers.get("Track-Action")
	if (trackAction == "noChange"):
		log("No change for track " + url, debug=True)
	else:
		log(trackAction + " " + url)