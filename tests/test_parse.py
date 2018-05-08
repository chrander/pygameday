import unittest
from pygameday import parse
import json
from pprint import pprint


class TestParsing(unittest.TestCase):

    def setUp(self):
        with open('master_scoreboard.json', 'r') as f:
            scoreboard = json.load(f)
        self.games = parse.parse_scoreboard(scoreboard)

    def test_parse_scoreboard(self):
        db_games = [parse.parse_game(game) for game in self.games]
        pprint(db_games)


if __name__ == '__main__':
    unittest.main()