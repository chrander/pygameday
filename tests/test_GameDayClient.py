#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, division

from dateutil import parser
from pygameday.pygameday import GameDayClient
import config


def test_ingest():
    start_date = parser.parse("2015-03-31")
    end_date = parser.parse("2015-03-31")

    client = GameDayClient(config.DATABASE_URI)
    client.db_stats()
    client.process_date_range(start_date, end_date)
    client.db_stats()


if __name__ == "__main__":
    test_ingest()
