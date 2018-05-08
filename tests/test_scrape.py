import unittest
from datetime import datetime
import json
from pprint import pprint

from pygameday import scrape


class TestScraping(unittest.TestCase):
    def test_fetch_master_scoreboard(self):
        date = datetime(2018, 4, 8)
        sb = scrape.fetch_master_scoreboard(date)
        with open('master_scoreboard.json', 'w') as f:
            json.dump(sb, f)
        pprint(sb)


if __name__ == '__main__':
    unittest.main()
