import json, requests, os
from datetime import datetime

SCHEDULE_TRACKER_ENDPOINT = os.environ.get('SCHEDULE_TRACKER_ENDPOINT')
if not SCHEDULE_TRACKER_ENDPOINT:
	exit("SCHEDULE_TRACKER_ENDPOINT environment variable not set - needs to be the URL of a running lucos_contacts instance.")

# Inform the schedule tracker that the job is complete
def updateScheduleTracker(success=True, message=None, system="lucos_media_import", frequency=1):
	payload = {
		"system": system,
		"frequency": frequency,
		"status": "success" if success else "error",
		"message": message,
	}
	try:
		schedule_tracker_response = requests.post(SCHEDULE_TRACKER_ENDPOINT, json=payload);
		schedule_tracker_response.raise_for_status()
	except Exception as error:
		print("\033[91m ["+datetime.now().isoformat()+"] ** Error ** Call to schedule-tracker failed.  "+type(error).__name__ + " " + str(error) + "\033[0m")