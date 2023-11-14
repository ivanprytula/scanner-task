from pathlib import Path

from decouple import config

DEBUG = config("DEBUG", default=False, cast=bool)
PRODUCTION = not DEBUG

BASE_DIR = Path(__file__).resolve(strict=True).parent

LOG_FILE = BASE_DIR / "scanner.log"

TIMEOUT_IN_MS = 5_000

RESULTS_DIR_NAME = "results"
