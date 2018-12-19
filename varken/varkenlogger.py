from logging.handlers import RotatingFileHandler
from logging import Filter, DEBUG, INFO, getLogger, Formatter, StreamHandler

from varken.helpers import mkdir_p


class BlacklistFilter(Filter):
    """
    Log filter for blacklisted tokens and passwords
    """
    filename = "varken.log"
    max_size = 5000000  # 5 MB
    max_files = 5
    log_folder = 'logs'

    blacklisted_strings = ['apikey',  'username',  'password', 'url']

    def __init__(self, filteredstrings):
        super().__init__()
        self.filtered_strings = filteredstrings

    def filter(self, record):
        for item in self.filtered_strings:
            try:
                if item in record.msg:
                    record.msg = record.msg.replace(item, 8 * '*' + item[-5:])
                if any(item in str(arg) for arg in record.args):
                    record.args = tuple(arg.replace(item, 8 * '*' + item[-5:]) if isinstance(arg, str) else arg
                                        for arg in record.args)
            except TypeError:
                pass
        return True


class VarkenLogger(object):
    def __init__(self, debug=None, data_folder=None):
        self.data_folder = data_folder
        self.log_level = debug

        # Set log level
        if self.log_level:
            self.log_level = DEBUG

        else:
            self.log_level = INFO

        # Make the log directory if it does not exist
        mkdir_p(f'{self.data_folder}/{BlacklistFilter.log_folder}')

        # Create the Logger
        self.logger = getLogger()
        self.logger.setLevel(DEBUG)

        # Create a Formatter for formatting the log messages
        logger_formatter = Formatter('%(asctime)s : %(levelname)s : %(module)s : %(message)s', '%Y-%m-%d %H:%M:%S')

        # Create the Handler for logging data to a file
        file_logger = RotatingFileHandler(f'{self.data_folder}/{BlacklistFilter.log_folder}/{BlacklistFilter.filename}',
                                          mode='a', maxBytes=BlacklistFilter.max_size, encoding=None, delay=0,
                                          backupCount=BlacklistFilter.max_files)

        file_logger.setLevel(self.log_level)

        # Add the Formatter to the Handler
        file_logger.setFormatter(logger_formatter)

        # Add the console logger
        console_logger = StreamHandler()
        console_logger.setFormatter(logger_formatter)
        console_logger.setLevel(self.log_level)

        # Add the Handler to the Logger
        self.logger.addHandler(file_logger)
        self.logger.addHandler(console_logger)
