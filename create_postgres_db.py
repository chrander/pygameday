#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Simple script for creating a Postgres database

This script invokes Postgres command line tools, specifically the "createdb" command.  The directory containing these
commands must be on your PATH for this script to work.

See the Postgres documentation for details on how to create databases.


Note that the name of the database to create is retrieved from the config.py file.
"""
import logging
import psycopg2


try:
    # Look for Database URI in config_mine.py first.
    # config_mine.py should not be version controlled, because it can contain username/password information.
    # config.py, a default config file, is version controlled. It should not have any usernames, passwords, or other
    # potentially sensitive information.
    from config_mine import DATABASE_URI
except ImportError:
    from config import DATABASE_URI


logger = logging.getLogger('pygameday')

db_name = 'gameday'  # Database name to create


with psycopg2.connect(DATABASE_URI) as conn:
    conn.autocommit = True
    with conn.cursor() as cur:
        try:
            cur.execute('CREATE DATABASE {};'.format(db_name))
            logger.info('Created database')
        except Exception as ex:
            logger.exception('Error creating database', ex)

