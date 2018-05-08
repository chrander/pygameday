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

logger = logging.getLogger('pygameday')


db_name = 'gameday'  # Database name to create
database_uri = 'postgresql://chris:chris@nas-1/postgres'  # Connection parameters


with psycopg2.connect(database_uri) as conn:
    conn.autocommit = True
    with conn.cursor() as cur:
        try:
            cur.execute('CREATE DATABASE {};'.format(db_name))
            logger.info('Created database')
        except Exception as ex:
            logger.exception('Error creating database', ex)

