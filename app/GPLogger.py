import logging

from time import gmtime, strftime


class GPLogger(object):
    def __init__(self, module_name):
        self.module_name = module_name
        self.log_level = logging.getLevelName("DEBUG")

    def format_message(self, level_name, msg, error=None):
        if not error:
            return "{} ({}) {} - {}".format(strftime("%Y-%m-%d %H:%M:%S", gmtime()), level_name, self.module_name, msg)

        #return "{} ({}) {} - {} : Error={}".format(strftime("%Y-%m-%d %H:%M:%S", gmtime()), level_name, self.module_name, msg, error.message)

    def setLevel(self, level):
        self.log_level = level

    def debug(self, msg):
        if self.log_level <= logging.getLevelName("DEBUG"):
            print(self.format_message("DEBUG", msg))

    def info(self, msg):
        if self.log_level <= logging.getLevelName("INFO"):
            print(self.format_message("INFO", msg))

    def warn(self, msg, error=None):
        self.warning(msg, error)

    def warning(self, msg, error=None):
        if self.log_level <= logging.getLevelName("WARNING"):
            print(self.format_message("WARNING", msg, error))

    def error(self, msg, error=None):
        if self.log_level <= logging.getLevelName("ERROR"):
            print(self.format_message("ERROR", msg, error))

    def critical(self, msg, error=None):
        if self.log_level <= logging.getLevelName("CRITICAL"):
            print(self.format_message("CRITICAL", msg, error))