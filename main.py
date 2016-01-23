#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Main command-line script for ingesting MLB GameDay data

See the usage() function for how to call this script
"""
from __future__ import print_function, division

import sys
from dateutil import parser

from pygameday.pygameday import GameDayClient

try:
    # Look for Database URI in config_mine.py first. (This config file is not version controlled)
    from config_mine import DATABASE_URI
except ImportError:
    from config import DATABASE_URI



def run():
    """Parses command line args and runs a GameDayClient that ingests data into a database

    Database connection settings from config.py are used.
    To configure logging, change settings in pygameday/constants.py
    """
    if len(sys.argv) > 2:
        # Both a start date and an end date are specified
        start_date_string = sys.argv[1]
        end_date_string = sys.argv[2]

    elif len(sys.argv) == 2:
        # Only a single date is specified; use it as start and end date
        start_date_string = sys.argv[1]
        end_date_string = sys.argv[1]

    else:
        usage()
        sys.exit(1)

    try:
        start_date = parser.parse(start_date_string)
        end_date = parser.parse(end_date_string)
    except:
        print("  Unable to parse dates: {}, {}".format(start_date_string, end_date_string))
        print("  Check your input dates and try again.")
        sys.exit(1)

    client = GameDayClient(DATABASE_URI)
    client.process_date_range(start_date, end_date)


def usage():
    print(
    """
    USAGE:
      $ python main.py [start_date]
      $ python main.py [start_date] [end_date]

        The parameters start_date and end_date must in the format 'yyyy-mm-dd'

        If only start_date is given, the GameDay data for that date will be ingested.  If start_date and end_date are
        both given, GameDay data for all days between start_date and end_date will be ingested (including the start
        date and end date).

    NOTE:
      Make certain that you have configured your database settings correctly in config.py!

    EXAMPLES:
      $ python main.py 2015-05-29
      $ python main.py 2015-05-29 2015-06-02
    """)

if __name__ == "__main__":
    run()
