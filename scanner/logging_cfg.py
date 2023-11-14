import os

from constants import LOG_FILE, PRODUCTION
from loguru import logger

if PRODUCTION:
    # Remove all handlers added so far, including the default one.
    # Avoids logs to be printed twice on the terminal or if we want add new/overwrite handler
    # NB: If we want to see logs on the terminal alongside the log file - don't remove default one
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
