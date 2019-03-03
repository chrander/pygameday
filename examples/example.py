#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Runs pygameday using the GameDayClient
"""
from datetime import datetime
from pygameday import GameDayClient


database_uri = "sqlite:///gameday.db"  # sqlite database on the local machine
# database_uri = "postgresql+psycopg2://user:passwd@localhost/gameday"  # Example Postgres database URI

start_date = datetime(2018, 5, 11)
end_date = datetime(2018, 5, 12)

client = GameDayClient(database_uri, n_workers=1)  # Increase n_workers to make processing faster
client.process_date_range(start_date, end_date)
