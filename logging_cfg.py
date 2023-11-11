import os
from pathlib import Path

from decouple import config
from loguru import logger

DEBUG = config("DEBUG", default=False, cast=bool)
PRODUCTION = not DEBUG

PROJECT_ROOT = Path(__file__).resolve(strict=True).parent
LOG_FILE = PROJECT_ROOT / "scanner.log"

if PRODUCTION:
    # Remove all handlers added so far, including the default one.
    # Avoids logs to be printed twice on the terminal or if we want add new handler
    # NB: If we want to see logs on the terminal - don't remove default one
    logger.remove()

    def opener(file, flags):
        """
        https://chmod-calculator.com/
        r (read): 4
        w (write): 2
        x (execute): 1

        Owner:  rw- = 4+2+0 = 6
        Group:  --- = 0+0+0 = 0
        Others: --- = 0+0+0 = 0
        """
        return os.open(file, flags, 0o600)

    fmt = "{time:YYYY-MM-DD at HH:mm:ss} | {level: <8} | {name: ^15} | {function: ^15} | {line: >3} | {message}"

    logger.add(
        LOG_FILE,
        level="INFO",  # >= INFO | 20
        format=fmt,
        serialize=True,
        diagnose=False,
        rotation="100 MB",
        compression="zip",
        opener=opener,
    )

# handler_id = logger.add(
#     # logging.StreamHandler(sys.stdout),
#     sys.stderr,
#     # level="INFO",
#     # format="<green>{time}</green> <level>{message}</level>",
#     colorize=True,
# )


# if DEBUG:
#     # Remove all handlers added so far, including the default one.
#     # It is needed to avoid logs to be printed twice on the terminal
#     logger.remove()

#     logger.add(
#         # logging.StreamHandler(sys.stdout),
#         sys.stderr,
#         # level="INFO",
#         # format="<green>{time}</green> <level>{message}</level>",
#         colorize=True,
#     )
#     dev_logger = logger
# elif PRODUCTION:

#     def opener(file, flags):
#         """
#         https://chmod-calculator.com/
#         r (read): 4
#         w (write): 2
#         x (execute): 1

#         Owner:  rw- = 4+2+0 = 6
#         Group:  --- = 0+0+0 = 0
#         Others: --- = 0+0+0 = 0
#         """
#         return os.open(file, flags, 0o600)

#     fmt = "{time:YYYY-MM-DD at HH:mm:ss} | {level: <8} | {name: ^15} | {function: ^15} | {line: >3} | {message}"

#     logger.add(
#         PRODUCTION_LOG_FILE,
#         level="INFO",  # >= INFO
#         format=fmt,
#         serialize=True,
#         diagnose=False,
#         rotation="100 MB",
#         compression="zip",
#         opener=opener,
#     )
#     prod_logger = logger
