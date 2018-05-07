#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Simple script for creating a PostgreSQL database

This script invokes Postgres command line tools, specifically the "createdb" command.  The directory containing these
commands must be on your PATH for this script to work.

See the Postgres documentation for details on how to create databases.


Note that the name of the database to create is retrieved from the config.py file.
"""
from __future__ import print_function, division

from subprocess import call

from config import DB_NAME

create_db_cmd = 'createdb ' + DB_NAME

call('echo -n Creating database...', shell=True)
call(create_db_cmd, shell=True)
call('echo Done.', shell=True)
