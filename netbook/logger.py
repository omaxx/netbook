import logging
import colorlog


logger = logging.getLogger(__name__.split(".")[0])


def setup_stderr_logger(logger, level="INFO"):
    stderr = colorlog.StreamHandler()
    stderr.setFormatter(colorlog.ColoredFormatter('%(log_color)s%(asctime)-32s%(levelname)-10s%(message)s'))
    stderr.setLevel(level)
    logger.addHandler(stderr)


def setup_file_logger(logger, filename, level="DEBUG"):
    log_file = logging.FileHandler(filename)
    log_file.setFormatter(logging.Formatter('%(asctime)-32s%(levelname)-10s%(message)s'))
    log_file.setLevel(level)
    logger.addHandler(log_file)


logger.setLevel("DEBUG")
setup_stderr_logger(logger, "DEBUG")
