from datetime import datetime
import os
import logging
from logging.handlers import TimedRotatingFileHandler

from middleware import (
    get_current_user_id_from_ctx,
    get_request_id,
)


class RequestIdFilter(logging.Filter):
    def filter(self, record):
        try:
            record.request_id = get_request_id()
        except LookupError:
            record.request_id = "kafka request"
        return True


class UserIdFilter(logging.Filter):
    def filter(self, record):
        try:
            record.user_id = get_current_user_id_from_ctx()
        except LookupError:
            record.request_id = "kafka"
        return True


def setup_logging():
    log_dir = "/logs"
    os.makedirs(log_dir, exist_ok=True)
    log_filename = datetime.now().strftime("%Y-%m-%d.log")

    log_format = "%(asctime)s - %(levelname)s - [%(request_id)s] - [%(user_id)s] - %(name)s:%(lineno)d - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    logging.getLogger().addFilter(RequestIdFilter())
    logging.getLogger().addFilter(UserIdFilter())

    sqlalchemy_logger = logging.getLogger("sqlalchemy.engine")
    sqlalchemy_logger.setLevel(logging.WARNING)
    sqlalchemy_logger.propagate = False

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    stream_handler = logging.StreamHandler()
    stream_handler.addFilter(RequestIdFilter())
    stream_handler.addFilter(UserIdFilter())
    stream_handler.setFormatter(logging.Formatter(fmt=log_format, datefmt=date_format))
    stream_handler.setLevel(logging.INFO)

    logger.addHandler(stream_handler)

    file_handler = TimedRotatingFileHandler(
        os.path.join(log_dir, log_filename),
        when="midnight",
        interval=1,
        backupCount=7,
        encoding="utf-8",
    )

    file_handler.addFilter(RequestIdFilter())
    file_handler.addFilter(UserIdFilter())
    file_handler.setFormatter(logging.Formatter(fmt=log_format, datefmt=date_format))
    logger.addHandler(file_handler)
