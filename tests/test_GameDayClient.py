#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, division

from dateutil import parser
from pygameday import GameDayClient


def test_ingest():
    start_date = parser.parse("2015-04-30")
    end_date = parser.parse("2015-04-30")

    database_uri = "sqlite:///gameday.db"

    client = GameDayClient(database_uri)
    client.db_stats()
    client.process_date_range(start_date, end_date)
    client.db_stats()


if __name__ == "__main__":
    test_ingest()
