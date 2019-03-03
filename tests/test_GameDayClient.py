#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from datetime import datetime
import logging

from pygameday import GameDayClient

logging.getLogger('pygameday').setLevel(logging.INFO)

class TestGameDayClient(unittest.TestCase):

    def test_ingest(self):
        start_date = datetime(2018, 4, 6)
        end_date = datetime(2018, 4, 6)

        database_uri = "sqlite:///gameday.db"
        n_workers = 4

        client = GameDayClient(database_uri, n_workers=n_workers)
        client.db_stats()
        client.process_date_range(start_date, end_date)
        client.db_stats()


if __name__ == '__main__':
    unittest.main()