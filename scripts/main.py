#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Runs pygameday using the GameDayClient
"""
from datetime import datetime
from pygameday import GameDayClient

try:
    # Look for Database URI in config_mine.py first.
    # config_mine.py should not be version controlled, because it can contain username/password information.
    # config.py, a default config file, is version controlled. It should not have any usernames, passwords, or other
    # potentially sensitive information.
    from config_mine import DATABASE_URI
except ImportError:
    from config import DATABASE_URI


start_date = datetime(2018, 5, 11)
end_date = datetime(2018, 5, 31)

client = GameDayClient(DATABASE_URI, n_workers=4)
client.process_date_range(start_date, end_date)
