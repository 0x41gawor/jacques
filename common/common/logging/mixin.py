import logging

from common.logging.config import configure_logging


class LoggingMixin:
    """
    A mixin class that provides a logger instance for any class that inherits from it.
    """
    @property
    def logger(self) -> logging.Logger:
        """
        Returns a logger instance specific to the class that inherits this mixin.

        Returns:
            logging.Logger: A logger instance for the class.
        """
        name = f"{self.__class__.__module__}.{self.__class__.__name__}"
        return logging.getLogger(name)

