import requests
from datetime import datetime

def loganneRequest(data):
	data["source"] = "lucos_media_import"
	loganne_reponse = requests.post('https://loganne.l42.eu/events', json=data);
	if loganne_reponse.status_code != 202:
		print ("\033[91m ["+datetime.now().isoformat()+"] ** Error ** Call to Loganne failed with "+str(loganne_response.status_code)+" response: " +  loganne_response.text + "\033[0m")