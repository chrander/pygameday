#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from logging.handlers import RotatingFileHandler
import os

from .constants import (LOG_LEVEL, LOG_FOLDER, LOG_FORMAT_CONSOLE, LOG_FORMAT_FILE, LOG_FORMAT_TIME,
                        LOG_BACKUP_COUNT, LOG_FILE_MAX_BYTES)
from .client import GameDayClient

__all__ = ['GameDayClient']

file_handler_name = 'FileHandler'
stream_handler_name = 'StreamHandler'


def configure_logging(log_name, log_to_file=True):

    logger = logging.getLogger(log_name)
    log_level = logging.getLevelName(LOG_LEVEL)
    logger.setLevel(log_level)
    logger.propagate = 0

    # Set handlers
    # Keep track of handlers by name so we don't initialize handlers multiple times
    handler_names = [h.get_name() for h in logger.handlers]

    # Set up a handler to log to file
    if log_to_file and file_handler_name not in handler_names:
        # First create the log folder if it doesn't exist
        if not os.path.exists(LOG_FOLDER):
            os.mkdir(LOG_FOLDER)

        # Set up a handler to log to file
        log_file_path = os.path.join(LOG_FOLDER, 'pygameday.log')
        fh = RotatingFileHandler(log_file_path, maxBytes=LOG_FILE_MAX_BYTES, backupCount=LOG_BACKUP_COUNT)
        fh.set_name(file_handler_name)
        fh.setLevel(log_level)
        file_formatter = logging.Formatter(LOG_FORMAT_FILE, LOG_FORMAT_TIME)
        fh.setFormatter(file_formatter)
        logger.addHandler(fh)

    # Set up a handler to log to console
    if stream_handler_name not in handler_names:
        ch = logging.StreamHandler()
        ch.set_name(stream_handler_name)
        ch.setLevel(log_level)  # Can set a different console logging level here
        console_formatter = logging.Formatter(LOG_FORMAT_CONSOLE, LOG_FORMAT_TIME)
        ch.setFormatter(console_formatter)
        logger.addHandler(ch)


configure_logging('pygameday')
