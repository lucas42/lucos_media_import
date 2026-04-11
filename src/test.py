#! /usr/local/bin/python3
import os, traceback, unittest
from unittest.mock import patch, MagicMock

# Set the media prefix to a known value for testing
os.environ["MEDIA_PREFIX"] = "http://example.org/media_library/"

# Set MEDIA_API and KEY_LUCOS_MEDIA_METADATA_API to broken values to avoid errors for not having it set
# (Shouldn't actually be called within logic tests)
os.environ["MEDIA_API"] = "http://localhost:000/null"
os.environ["KEY_LUCOS_MEDIA_METADATA_API"] = "invalidkey"

# Units under test
from logic import scan_file, scan_insert_file
from media_api import lookupOrCreateAlbum

testcases = [
	{
		'comment': "Normal Track",
		'path': "test_tracks/A Testing Day.mp3",
		'expected_data': {
			'duration': 4,
			'tags': {
				'title': [{'name': 'A Testing Day'}],
				'artist': [{'name': 'Computerface'}],
			},
			'url': "http://example.org/media_library/test_tracks/A Testing Day.mp3",
			'fingerprint': 'AQAAEA8lJhmDMwyeZRmMH_mHZDmD5j1-XKGJ_MbUEezx43gIwIghQgAhmIBCSEKpBA',
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
				'title': [{'name': 'No Title'}],
				'artist': [{'name': 'Computerface'}],
			},
			'url': "http://example.org/media_library/test_tracks/No Title.mp3",
			'fingerprint': 'AQAAD1dCbZqQa4RLpXj0QHnwH2nFI4-SHTzuHOeK_vAaHS2PE4GMMQogp4QFgAlDEAM',
		}
	},
	{
		'comment': "An artists of 'Various' is ignored",
		'path': "test_tracks/Various Artists.mp3",
		'expected_data': {
			'duration': 3,
			'tags': {
				'title': [{'name': 'Testing Artists'}],
				'album': [{'name': 'Compilations'}],
			},
			'url': "http://example.org/media_library/test_tracks/Various Artists.mp3",
			'fingerprint': 'AQAABtm2i1GChOrx4cmH8QO5MwAAARVGAA',
		}
	},
	{
		'comment': "A non-audio file returns None",
		'path': "test_tracks/lockdown-compositions.jpg",
		'expected_data': None,
	},
	{
		'comment': "Tracks in directory of known provenance set provenance tag",
		'path': "test_tracks/ceol srl/bandcamp/A Testing Band.mp3",
		'expected_data': {
			'duration': 4,
			'tags': {
				'title': [{'name': 'A Testing Band'}],
				'artist': [{'name': 'The Very Camp Band'}],
				'comment': [{'name': ''}],
				'provenance': [{'name': 'bandcamp'}],
			},
			'url': "http://example.org/media_library/test_tracks/ceol srl/bandcamp/A Testing Band.mp3",
			'fingerprint': 'AQAAEpU0R1tQNUcfNMezIHwbNM9xDX-hKuvxXkmC6YIfFEePo9cBIwARQiAIDAEWYREJAQ',
		}
	},
	{
		'comment': "A track longer than 60 seconds",
		'path': "test_tracks/An Extended Testing Day.mp3",
		'expected_data': {
			'duration': 63,
			'tags': {
				'title': [{'name': 'An Extended Testing Day'}],
			},
			'url': "http://example.org/media_library/test_tracks/An Extended Testing Day.mp3",
			'fingerprint': 'AQABz6-UKWPwMhPOcIHx4y2aTw_CPNAvIk_GJnjhM8HxkHgWPoFH48kFPw4uMtPxLNkC4w-eHMmzI4-Cdmj245KDB_lNPHbgWReFZxmRH36MR0nGBFcHH7GO5EmEWtJRRzc-7Exz_GCyTEqOUA9PJA3V43jgK3hesAr2ZUc-J3jhH2cOrY_hHTmL5sd7HF9UmFNyJKeR33CeDW8enMwI40c_HblyQ3tF5DyePEZ_NKeOv8LHDg3HxCr6oNeP5smGi3nwTMpg_PihL8O1o-FR_sEj4yfyE62PMNe2FA96NHW241GSR-iZEc0R60iWR0LTJDnxC_-xpwGbEx6VREfSjDxiRsOD5jnKE0_Ah8GuREf8OUHzotJJaM-Q8sZf-ES_F8eJhzJSNjOSJ0cTX-g3vFmWDM1IFD98TUfCJzty4snY4G_QPPFRGTfOMCLh5cXhH9dmXFmWJUczC11v_EiePciXDxe8HM_xHPkL3Y8gLr6RJ5uOH76Ef1PwKAmXoPmLSjd0Db6SwFZPHGeD-WkIhqkSNFeCxDxyBoefH88DVsGVLNgf_CHC7Kh8QisXI93xw8_R4zbxLDLKTEKyzBnyw7mHM4vwlJPgHz96IcwVJHyo4x-ejGlwHX6CH89WlBkTfWhGPDl8ChcnJsbDKIP_4w-FP0Py0ciTHUWz-HgiZ_gZ5MfTOEhnZTOemcVPuKaGM2UyXMoy-CmuQ8sj4dLRNKqOY2caPC-oOQpOSYOaRcV7_Icf4gcf7Mti_An6IsyPM4fWx0j34jyaD8eJh3KQspmF5Ppw5zr8bHhYZnhG-PiP5hPSJ9mR7MSTPfjToHl-9LhvPBw5mD8e9DqaJ5txZWVQMhHRPPiFPI-RnIlynIf5408aPMfPIP_Q0I_RaxPyHD2LRvsW4UoYBn1GovmRVC7CXBGaRj3xY3-OpwHTDs0XIWkWpYgpCg-aH-Xx5AefSMGePcjDCs1R8kTLHfqP9PCP_riJb8YzKUc6Z1CdI_3xKcHDcIF_HLeG5ksuhHl4JM7xjE3ww5fxB_9W4hkTwTuewz_-LAmeJcrg8fiNB8mzI4-Cw4uPy8FP_MjTOIJnccaz9Mhv-McXL8GlLIN_XIeuCL2So1ePY2dzPG_AZNSC8MmQNNRxl3jg8QqeF9mDj4LCH-F-NCN6xToupMiPl4OPfDiax5iP5qjMDM2PPsc7tD-Os02MD_5w9MFrHE3EJNlCAAAAAAAAAAAAAAAAAAAAAAAgCDEQCAEMsABoAhg0gBBBQQCGAcAYAAQwJZFA5DAHsBHEESGYZZAwASBkghCAGYJOsEcYI0YIQowByhBBBGAOCMCcEAIYIIiwBApGKABOMAcAYGIIIcghCglGjCOCUAAgEUIQYoQgThCDSUPOMEEMAIJpQQgCmlBHhASEgQAMI4xK4AxgAAhFmKQICMAMA4IzAQTjgBDCkGFAGIMdQY4wxqBhAihiGBCIMAECApgJphAgQAFBiRNKAcYEoIQxJQgGhiBlvCEMMOMAooYBIYlhghDgnBOYNOQAAUgwTowggElBiEAAOAAYEUwIA7CAggFFnCAEOCGYA0AoaAERTAGBjCGEAioAJIIAIxwzABBDlVMGOwIgMFYAhgkAgikCCmIMAAIeNAAYgoUFwTAGoAPCCkaUQUAQYIFhwgHBDSHCCMAEYQAJgwABkngitECAYCAQE8ARJ6xyDA',
		}
	},
]
failures = 0

for case in testcases:
	try:
		actual_data = scan_file(case["path"])
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
			traceback.print_exception(error)
			failures += 1
		elif case["expected_error"] != str(error):
			print("\033[91mFailed\033[0m \"" + case['comment'] + "\".  Mismatched error message: Returned \033[91m" + str(error) + "\033[0m, expected " + str(case['expected_error']))
			traceback.print_exception(error)
			failures += 1

if (failures > 0):
	print("\033[91m"+str(failures) + " failures\033[0m in " + str(len(testcases)) + " cases.")
	exit(1)
else:
	print("All " + str(len(testcases)) + " cases passed.")


class TestScanInsertFileAlbum(unittest.TestCase):
	"""Tests for album URI resolution in scan_insert_file."""

	@patch('logic.insertTrack')
	@patch('logic.lookupOrCreateAlbum')
	def test_album_tag_resolved_via_lookup(self, mock_lookup, mock_insert):
		"""When track has an album tag, lookupOrCreateAlbum is called and the tag value includes the URI."""
		mock_lookup.return_value = {"name": "Compilations", "uri": "https://media.l42.eu/albums/5"}
		scan_insert_file("test_tracks/Various Artists.mp3")
		mock_lookup.assert_called_once_with("Compilations")
		trackdata = mock_insert.call_args[0][0]
		self.assertEqual(trackdata["tags"]["album"], [{"name": "Compilations", "uri": "https://media.l42.eu/albums/5"}])

	@patch('logic.insertTrack')
	@patch('logic.lookupOrCreateAlbum')
	def test_no_album_tag_skips_lookup(self, mock_lookup, mock_insert):
		"""When track has no album tag, lookupOrCreateAlbum is not called."""
		scan_insert_file("test_tracks/A Testing Day.mp3")
		mock_lookup.assert_not_called()
		mock_insert.assert_called_once()
		trackdata = mock_insert.call_args[0][0]
		self.assertNotIn("album", trackdata["tags"])

	@patch('logic.insertTrack')
	@patch('logic.lookupOrCreateAlbum')
	def test_non_audio_file_skips_both(self, mock_lookup, mock_insert):
		"""Non-audio files result in neither lookup nor insert being called."""
		scan_insert_file("test_tracks/lockdown-compositions.jpg")
		mock_lookup.assert_not_called()
		mock_insert.assert_not_called()


class TestLookupOrCreateAlbum(unittest.TestCase):
	"""Tests for the lookupOrCreateAlbum function in media_api."""

	@patch('media_api.session')
	def test_found_on_initial_lookup(self, mock_session):
		"""GET returns an exact match — returns tag value without POSTing."""
		mock_get = MagicMock()
		mock_get.json.return_value = {"albums": [{"name": "Abbey Road", "uri": "https://media.l42.eu/albums/1"}]}
		mock_session.get.return_value = mock_get

		result = lookupOrCreateAlbum("Abbey Road")

		self.assertEqual(result, {"name": "Abbey Road", "uri": "https://media.l42.eu/albums/1"})
		mock_session.post.assert_not_called()

	@patch('media_api.session')
	def test_partial_match_ignored_on_lookup(self, mock_session):
		"""GET returns a partial match but no exact match — proceeds to POST."""
		mock_get = MagicMock()
		mock_get.json.return_value = {"albums": [{"name": "Abbey Road (Deluxe)", "uri": "https://media.l42.eu/albums/2"}]}
		mock_session.get.return_value = mock_get

		mock_post = MagicMock()
		mock_post.status_code = 201
		mock_post.json.return_value = {"id": 99, "name": "Abbey Road", "uri": "https://media.l42.eu/albums/99"}
		mock_session.post.return_value = mock_post

		result = lookupOrCreateAlbum("Abbey Road")

		self.assertEqual(result, {"name": "Abbey Road", "uri": "https://media.l42.eu/albums/99"})
		mock_session.post.assert_called_once()

	@patch('media_api.session')
	def test_not_found_creates_album(self, mock_session):
		"""GET returns no match — POSTs to create, returns tag value with URI."""
		mock_get = MagicMock()
		mock_get.json.return_value = {"albums": []}
		mock_session.get.return_value = mock_get

		mock_post = MagicMock()
		mock_post.status_code = 201
		mock_post.json.return_value = {"id": 42, "name": "New Album", "uri": "https://media.l42.eu/albums/42"}
		mock_session.post.return_value = mock_post

		result = lookupOrCreateAlbum("New Album")

		self.assertEqual(result, {"name": "New Album", "uri": "https://media.l42.eu/albums/42"})
		mock_session.post.assert_called_once()

	@patch('media_api.session')
	def test_race_condition_409_retry_succeeds(self, mock_session):
		"""POST returns 409 — retries GET which now finds the album."""
		mock_get_first = MagicMock()
		mock_get_first.json.return_value = {"albums": []}
		mock_get_retry = MagicMock()
		mock_get_retry.json.return_value = {"albums": [{"name": "Race Album", "uri": "https://media.l42.eu/albums/7"}]}
		mock_session.get.side_effect = [mock_get_first, mock_get_retry]

		mock_post = MagicMock()
		mock_post.status_code = 409
		mock_session.post.return_value = mock_post

		result = lookupOrCreateAlbum("Race Album")

		self.assertEqual(result, {"name": "Race Album", "uri": "https://media.l42.eu/albums/7"})
		self.assertEqual(mock_session.get.call_count, 2)

	@patch('media_api.session')
	def test_race_condition_409_retry_fails(self, mock_session):
		"""POST returns 409 but retry GET also finds nothing — raises exception."""
		mock_get = MagicMock()
		mock_get.json.return_value = {"albums": []}
		mock_session.get.return_value = mock_get

		mock_post = MagicMock()
		mock_post.status_code = 409
		mock_session.post.return_value = mock_post

		with self.assertRaises(Exception) as ctx:
			lookupOrCreateAlbum("Missing Album")

		self.assertIn("Missing Album", str(ctx.exception))


if __name__ == '__main__':
	unittest.main()