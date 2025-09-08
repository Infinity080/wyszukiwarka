import logging
from pythonjsonlogger import jsonlogger

logger = logging.getLogger(__name__)

formatter = jsonlogger.JsonFormatter(
    "%(timestamp)s %(levelname)s %(message)s %(request_path)s %(status_code)s"
)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

file_handler = logging.FileHandler("requests.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

logger.setLevel(logging.INFO)