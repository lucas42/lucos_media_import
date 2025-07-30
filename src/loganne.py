import os, sys, requests
from datetime import datetime

if not os.environ.get("LOGANNE_ENDPOINT"):
	sys.exit("\033[91mLOGANNE_ENDPOINT not set\033[0m")
loganne_endpoint = os.environ.get("LOGANNE_ENDPOINT")

def loganneRequest(data):
	data["source"] = "lucos_media_import"
	loganne_reponse = requests.post(loganne_endpoint, json=data, headers={'User-Agent': "lucos_media_import"});
	if loganne_reponse.status_code != 202:
		print ("\033[91m ["+datetime.now().isoformat()+"] ** Error ** Call to Loganne failed with "+str(loganne_response.status_code)+" response: " +  loganne_response.text + "\033[0m")