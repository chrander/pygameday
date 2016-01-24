#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import

import os
import sys
import logging
from datetime import datetime
from dateutil import parser

from pygameday import constants

logger = logging.getLogger("pygameday")

def configure_logging(log_name, log_to_file=False):

    logger = logging.getLogger(log_name)
    log_level = logging.DEBUG
    logger.setLevel(log_level)
    logger.propagate = 0

    # Set handlers
    # Keep track of handlers by name so we don't initialize handlers multiple times
    handler_names = [h.get_name() for h in logger.handlers]

    # Set up a handler to log to file
    if log_to_file and "FileHandler" not in handler_names:
        # First create the log folder if it doesn't exist
        if not os.path.exists(constants.LOG_FOLDER):
            os.mkdir(constants.LOG_FOLDER)

        # Set up a handler to log to file
        today = datetime.now()
        log_file_name = "pygameday_{:4d}-{:2d}-{:2d}.log".format(today.year, today.month, today.day)
        fh = logging.FileHandler(os.path.join(constants.LOG_FOLDER, log_file_name))
        fh.set_name("FileHandler")
        fh.setLevel(log_level)
        file_formatter = logging.Formatter(constants.LOG_FORMAT_FILE, constants.LOG_FORMAT_TIME)
        fh.setFormatter(file_formatter)

    # Set up a handler to log to console
    if "StreamHandler" not in handler_names:
        ch = logging.StreamHandler()
        ch.set_name("StreamHandler")
        ch.setLevel(log_level)  # Can set a different console logging level here
        console_formatter = logging.Formatter(constants.LOG_FORMAT_CONSOLE, constants.LOG_FORMAT_TIME)
        ch.setFormatter(console_formatter)
        logger.addHandler(ch)


def set_logging_level(level):
    """Sets the logging level

    Parameters
    ----------
    level : str
        String corresponding to a valid logging level.
        Acceptable values: NOTSET, DEBUG, WARN, INFO, ERROR, CRITICAL
    """
    logger = logging.getLogger("pygameday")
    logger.setLevel(logging.getLevelName(level))


def validate_date(date):
    if type(date) == datetime:
        return date

    elif type(date) == str:
        try:
            date = parser.parse(date)

        except ValueError:
            msg = "Invalid date: {}. Aborting.".format(date)
            logger.critical(msg)
            sys.exit(1)

        return date

    else:
        msg = "Invalid date: {}. Aborting.".format(date)
        logger.critical(msg)
        sys.exit(1)
