#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Default configuration parameters for the MLB GameDay parser
"""
from __future__ import print_function, division

# ----------------------------------------------------------------------------------------------------------------------
# Database Parameters
#
DB_NAME = "gameday"
DATABASE_URI = "sqlite:///gameday.db"  # sqlite database
# DATABASE_URI = "postgresql+psycopg2://user:passwd@localhost/" + DB_NAME  # Postgres database
