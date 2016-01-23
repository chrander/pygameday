#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Defines constants used by the MLB GameDay client.
"""
from __future__ import print_function, division

import logging


# ----------------------------------------------------------------------------------------------------------------------
# GameDay URL parameters
#
GD_SERVER = "http://gd2.mlb.com"
GD_BASE_PATH = "/components/game/mlb"

# ----------------------------------------------------------------------------------------------------------------------
# Logging
#
LOG_LEVEL = logging.INFO
LOG_FOLDER = "logs"
LOG_FORMAT = '%(asctime)s | %(filename)s | %(funcName)s (%(lineno)d) | %(levelname)s | %(message)s'
LOG_DATE_FORMAT = "%m/%d/%Y %I:%M:%S %p"
