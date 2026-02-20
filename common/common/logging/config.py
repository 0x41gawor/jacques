# import logging

# def configure_logging(level: int = logging.INFO) -> None:
#     """
#     Configures the logging system with a basic configuration.

#     Args:
#         level (int): The logging level to set. Default is logging.INFO.
#     """
#     logging.basicConfig(
#         level=level,
#         format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
#         datefmt='%Y-%m-%d %H:%M:%S'
#     )

import logging
import json
import sys


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # extra fields
        if hasattr(record, "__dict__"):
            for key, value in record.__dict__.items():
                if key not in (
                    "name", "msg", "args", "levelname", "levelno",
                    "pathname", "filename", "module", "exc_info",
                    "exc_text", "stack_info", "lineno", "funcName",
                    "created", "msecs", "relativeCreated",
                    "thread", "threadName", "processName", "process"
                ):
                    log_record[key] = value

        return json.dumps(log_record)


def configure_logging(level=logging.INFO):
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers = [handler]
    # wyciszenie werkzeug
    logging.getLogger("werkzeug").setLevel(logging.WARNING)
