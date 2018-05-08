#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Default configuration parameters for the MLB GameDay parser

This file is version controlled.

*** DO NOT USE THIS FILE TO DEFINE USER NAMES, PASSWORDS, OR OTHER POTENTIALLY SENSITIVE INFORMATION ***

Define such information in a file named config_mine.py, which should never be version controlled. The program will
look for config information in that file first, and only refer to this file if it can't find config_mine.py.

config_mine.py should look exactly like this file, but with username/password information filled in.
"""

# ----------------------------------------------------------------------------------------------------------------------
# Database Parameters
#
DB_NAME = "gameday"
DATABASE_URI = "sqlite:///gameday.db"  # sqlite database on the local machine
# DATABASE_URI = "postgresql+psycopg2://user:passwd@localhost/" + DB_NAME  # Postgres database
