import logging

from logging.handlers import RotatingFileHandler
from varken.helpers import mkdir_p


FILENAME = "varken.log"
MAX_SIZE = 5000000  # 5 MB
MAX_FILES = 5
LOG_FOLDER = 'logs'


# Taken from Hellowlol/HTPC-Manager/Tautulli
class BlacklistFilter(logging.Filter):
    """
    Log filter for blacklisted tokens and passwords
    """
    blacklisted_strings = ['apikey',  'username',  'password']

    def __init__(self, filteredstrings):
        self.filtered_strings = filteredstrings

    def filter(self, record):
        for item in self.filtered_strings:
            try:
                if item in record.msg:
                    record.msg = record.msg.replace(item, 8 * '*' + item[-2:])
                if any(item in str(arg) for arg in record.args):
                    record.args = tuple(arg.replace(item, 8 * '*' + item[-2:]) if isinstance(arg, str) else arg
                                        for arg in record.args)

            except:
                pass
        return True


class VarkenLogger(object):
    """docstring for ."""
    def __init__(self, log_path=None, debug=None, data_folder=None):
        self.data_folder = data_folder
        self.log_level = debug

        # Set log level
        if self.log_level:
            self.log_level = logging.DEBUG

        else:
            self.log_level = logging.INFO


        # Make the log directory if it does not exist
        mkdir_p('{}/{}'.format(self.data_folder, LOG_FOLDER))

        # Create the Logger
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)

        # Create a Formatter for formatting the log messages
        logger_formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(module)s : %(message)s', '%Y-%m-%d %H:%M:%S')

        # Create the Handler for logging data to a file
        file_logger = RotatingFileHandler('{}/{}/{}'.format(self.data_folder, LOG_FOLDER, FILENAME),
                                          mode='a', maxBytes=MAX_SIZE,
                                          backupCount=MAX_FILES,
                                          encoding=None, delay=0
                                          )

        file_logger.setLevel(self.log_level)

        # Add the Formatter to the Handler
        file_logger.setFormatter(logger_formatter)

        # Add the console logger
        console_logger = logging.StreamHandler()
        console_logger.setFormatter(logger_formatter)
        console_logger.setLevel(self.log_level)

        # Add the Handler to the Logger
        self.logger.addHandler(file_logger)
        self.logger.addHandler(console_logger)
