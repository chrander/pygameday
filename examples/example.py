#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Runs pygameday using the StatcastClient
"""
from datetime import datetime
from pygameday import StatcastClient


database_uri = "sqlite:///gameday.db"  # sqlite database on the local machine
# database_uri = "postgresql+psycopg2://user:passwd@localhost/gameday"  # Example Postgres database URI

start_date = datetime(2023, 7, 4)
end_date = datetime(2023, 7, 5)

client = StatcastClient(database_uri)
client.process_date_range(start_date, end_date)
