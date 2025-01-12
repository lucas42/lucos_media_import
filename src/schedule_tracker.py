import json, requests
from datetime import datetime

# Inform the schedule tracker that the job is complete
def updateScheduleTracker(success=True, message=None, system="lucos_media_import", frequency=1):
	payload = {
		"system": system,
		"frequency": frequency,
		"status": "success" if success else "error",
		"message": message,
	}
	try:
		schedule_tracker_response = requests.post('https://schedule-tracker.l42.eu/report-status', json=payload);
		schedule_tracker_response.raise_for_status()
	except Exception as error:
		print("\033[91m ["+datetime.now().isoformat()+"] ** Error ** Call to schedule-tracker failed.  "+type(error).__name__ + " " + str(error) + "\033[0m")