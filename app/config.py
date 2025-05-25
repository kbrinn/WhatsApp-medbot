from pathlib import Path

from decouple import AutoConfig

# Base directory of the project (two levels up from this file)
BASE_DIR = Path(__file__).resolve().parent.parent

# Configure decouple to load variables from the project's root `..env`
config = AutoConfig(search_path=BASE_DIR)
