#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from datetime import datetime
from pygameday import GameDayClient


class TestGameDayClient(unittest.TestCase):

    def test_ingest(self):
        start_date = datetime(2016, 4, 8)
        end_date = datetime(2016, 4, 8)

        database_uri = "sqlite:///gameday.db"

        client = GameDayClient(database_uri)
        client.db_stats()
        client.process_date_range(start_date, end_date)
        client.db_stats()


if __name__ == '__main__':
    unittest.main()