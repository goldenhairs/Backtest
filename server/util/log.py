import logging.config

from Backtest.server.util.config import Config


logging.config.fileConfig(Config().log_path)


def get_logger(filename):
    logger = logging.getLogger(filename)
    return logger
