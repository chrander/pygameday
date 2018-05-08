#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
from pygameday import GameDayClient


def test_ingest():
    start_date = datetime(2018, 4, 30)
    end_date = datetime(2018, 4, 30)

    database_uri = "sqlite:///gameday.db"

    client = GameDayClient(database_uri)
    client.db_stats()
    client.process_date_range(start_date, end_date)
    client.db_stats()


if __name__ == "__main__":
    test_ingest()
