import json, os


def _checkpoint_file():
	state_dir = os.environ.get("STATE_DIR", "/var/state")
	return os.path.join(state_dir, "import_checkpoint.json")


def load_checkpoint():
	"""Load checkpoint from disk, or return an empty checkpoint for a fresh start."""
	try:
		with open(_checkpoint_file(), "r") as f:
			checkpoint = json.load(f)
	except (FileNotFoundError, json.JSONDecodeError):
		checkpoint = {}
	checkpoint.setdefault("root_files_done", False)
	checkpoint.setdefault("completed_dirs", [])
	# Progress within the top-level directory currently being scanned, below
	# per-top-level-directory granularity (#173). None when no directory is in
	# progress. setdefault keeps checkpoints written before this key existed loading
	# cleanly, resuming that in-progress directory from scratch under the new scheme.
	checkpoint.setdefault("current_dir", None)
	return checkpoint


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
