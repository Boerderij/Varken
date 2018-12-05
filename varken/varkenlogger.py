import logging

class VarkenLogger(object):
    """docstring for ."""
    def __init__(self, log_path=None, log_level=None):
        # Create the Logger
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)

        # Create a Formatter for formatting the log messages
        logger_formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(module)s : %(message)s', '%Y-%m-%d %H:%M:%S')

        # Create the Handler for logging data to a file
        file_logger = logging.FileHandler('varken.log')
        file_logger.setLevel(logging.DEBUG)

        # Add the Formatter to the Handler
        file_logger.setFormatter(logger_formatter)

        # Add the console logger
        console_logger = logging.StreamHandler()
        console_logger.setFormatter(logger_formatter)
        console_logger.setLevel(logging.INFO)

        # Add the Handler to the Logger
        self.logger.addHandler(file_logger)
        self.logger.addHandler(console_logger)
