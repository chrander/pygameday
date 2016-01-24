#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Defines constants used by the MLB GameDay client.
"""
# ----------------------------------------------------------------------------------------------------------------------
# GameDay URL parameters
#
GD_SERVER = "http://gd2.mlb.com"
GD_BASE_PATH = "/components/game/mlb"

# ----------------------------------------------------------------------------------------------------------------------
# Logging
#
LOG_FOLDER = "logs"
LOG_FORMAT_FILE = '%(asctime)s | %(filename)s | %(funcName)s (%(lineno)d) | %(levelname)s | %(message)s'
LOG_FORMAT_CONSOLE = '%(asctime)s | %(levelname)s | %(message)s'
LOG_FORMAT_TIME = "%Y-%m-%d %H:%M:%S"