#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from datetime import datetime

from pygameday import scrape


class TestScraping(unittest.TestCase):

    def test_fetch_statcast_data(self):
        """Verify that a known regular-season date returns pitch data."""
        date = datetime(2023, 7, 4)
        df = scrape.fetch_statcast_data(date, date)
        self.assertIsNotNone(df)
        self.assertFalse(df.empty)
        self.assertIn('game_pk', df.columns)
        self.assertIn('pitch_type', df.columns)
        self.assertIn('release_speed', df.columns)
        self.assertIn('plate_x', df.columns)


if __name__ == '__main__':
    unittest.main()
