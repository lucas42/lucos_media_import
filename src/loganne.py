import os, sys, requests
from datetime import datetime

if not os.environ.get("LOGANNE_ENDPOINT"):
	sys.exit("\033[91mLOGANNE_ENDPOINT not set\033[0m")
loganne_endpoint = os.environ.get("LOGANNE_ENDPOINT")

def loganneRequest(data):
	data["source"] = "lucos_media_import"
	try:
		loganne_reponse = requests.post(loganne_endpoint, json=data, headers={'User-Agent': "lucos_media_import"})
		loganne_reponse.raise_for_status()
	except Exception as error:
		print("\033[91m [{}] ** Error from Loganne: {}\033[0m".format(datetime.now().isoformat(),error))