#! /usr/local/bin/python3
import os

# Set the media prefix to a known value for testing
os.environ["MEDIA_PREFIX"] = "http://example.org/media_library/"

# Set MEDIA_API to a broken value to avoid errors for not having it set
# (Shouldn't actually be called within logic tests)
os.environ["MEDIA_API"] = "http://localhost:000/null"

# Unit under test
from logic import scan_file

testcases = [
	{
		'comment': "Normal Track",
		'path': "test_tracks/A Testing Day.mp3",
		'expected_data': {
			'duration': 4,
			'tags': {
				'title': 'A Testing Day',
				'artist': 'Computerface',
			},
			'url': "http://example.org/media_library/test_tracks/A Testing Day.mp3",
		}
	},
	{
		'comment': "Short Track is skipped",
		'path': "test_tracks/Short.mp3",
		'expected_error': "Empty Track",
	},
	{
		'comment': "Empty Track is skipped",
		'path': "test_tracks/Empty.mp3",
		'expected_error': "Empty Track",
	},
	{
		'comment': "Track without title defaults to filename",
		'path': "test_tracks/No Title.mp3",
		'expected_data': {
			'duration': 4,
			'tags': {
				'title': 'No Title',
				'artist': 'Computerface',
			},
			'url': "http://example.org/media_library/test_tracks/No Title.mp3",
		}
	},
	{
		'comment': "An artists of 'Various' is ignored",
		'path': "test_tracks/Various Artists.mp3",
		'expected_data': {
			'duration': 3,
			'tags': {
				'title': 'Testing Artists',
				'album': 'Compilations',
			},
			'url': "http://example.org/media_library/test_tracks/Various Artists.mp3",
		}
	},
	{
		'comment': "A non-audio file returns None",
		'path': "test_tracks/lockdown-compositions.jpg",
		'expected_data': None,
	},
]
failures = 0

for case in testcases:
	try:
		(actual_fingerprint, actual_data) = scan_file(case["path"])
		if "expected_error" in case:
			print("\033[91mFailed\033[0m \"" + case['comment'] + "\".  No error raised.")
			print(actual_data["duration"])
			failures += 1
			continue
		if case["expected_data"] != actual_data:
			print("\033[91mFailed\033[0m \"" + case['comment'] + "\".  Returned \033[91m" + str(actual_data) + "\033[0m, expected " + str(case['expected_data']))
			failures += 1
	except Exception as error:
		if "expected_error" not in case:
			print("\033[91mFailed\033[0m \"" + case['comment'] + "\".  Unexpected error raised: \033[91m"+type(error).__name__ + " " + str(error) + "\033[0m")
			failures += 1
		elif case["expected_error"] != str(error):
			print("\033[91mFailed\033[0m \"" + case['comment'] + "\".  Mismatched error message: Returned \033[91m" + str(error) + "\033[0m, expected " + str(case['expected_error']))
			failures += 1

if (failures > 0):
	print("\033[91m"+str(failures) + " failures\033[0m in " + str(len(testcases)) + " cases.")
	exit(1)
else:
	print("All " + str(len(testcases)) + " cases passed.")