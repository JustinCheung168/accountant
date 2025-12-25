import logging

# Suppress low-level matplotlib logs.
import matplotlib 
logging.getLogger('matplotlib').setLevel(logging.WARNING)

class LoggerMixin:
    @property
    def logger(self):
        # Logger named after module + class
        name = f"{self.__class__.__module__}.{self.__class__.__name__}"
        return logging.getLogger(name)
