#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, division

import os
import logging
from datetime import datetime
from dateutil import parser

import constants


DATE_STRING_FORMAT = "%Y-%m-%d"  # This controls how Don't change this until you understand the consequences


def init_logging(log_to_file=False):
    """ Initializes logging functionality

    Most logging properties are set in constants.py
    """

    logger = logging.getLogger("pygameday")
    logger.setLevel(constants.LOG_LEVEL)

    # Set up log formatting
    formatter = logging.Formatter(constants.LOG_FORMAT)

    if log_to_file:
        # First create the log folder if it doesn't exist
        if not os.path.exists(constants.LOG_FOLDER):
            os.mkdir(constants.LOG_FOLDER)

        # Set up a handler to log to file
        today = datetime.now()
        log_file_name = "pygameday_{:4d}-{:2d}-{:2d}.log".format(today.year, today.month, today.day)
        fh = logging.FileHandler(os.path.join(constants.LOG_FOLDER, log_file_name))
        fh.setLevel(constants.LOG_LEVEL)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    # Set up a handler to log to console
    ch = logging.StreamHandler()
    ch.setLevel(constants.LOG_LEVEL)  # Can set a different console logging level here
    ch.setFormatter(formatter)
    logger.addHandler(ch)


def parse_date_string(date_string):
    date = parser.parse(date_string)
    return date
