import logging

class LoggerMixin:
    @property
    def logger(self):
        # Logger named after module + class
        name = f"{self.__class__.__module__}.{self.__class__.__name__}"
        return logging.getLogger(name)
