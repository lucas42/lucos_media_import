import json, os


def _checkpoint_file():
	state_dir = os.environ.get("STATE_DIR", "/var/state")
	return os.path.join(state_dir, "import_checkpoint.json")


def load_checkpoint():
	"""Load checkpoint from disk, or return an empty checkpoint for a fresh start."""
	try:
		with open(_checkpoint_file(), "r") as f:
			return json.load(f)
	except (FileNotFoundError, json.JSONDecodeError):
		return {"root_files_done": False, "completed_dirs": []}


def save_checkpoint(checkpoint):
	"""Persist checkpoint to disk."""
	filepath = _checkpoint_file()
	os.makedirs(os.path.dirname(filepath), exist_ok=True)
	with open(filepath, "w") as f:
		json.dump(checkpoint, f)


def clear_checkpoint():
	"""Remove checkpoint file after clean completion."""
	try:
		os.remove(_checkpoint_file())
	except FileNotFoundError:
		pass
