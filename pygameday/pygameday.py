#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Defines GameDayClient, the primary class for scraping, parsing, and ingesting MLB GameDay data.
"""
from __future__ import print_function, division, absolute_import

import logging
from datetime import timedelta
from dateutil import parser

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

import pygameday.util as util
import pygameday.parse as parse
import pygameday.scrape as scrape
from pygameday.models import Game
from pygameday.models import Player
from pygameday.models import AtBat
from pygameday.models import Pitch
from pygameday.models import HitInPlay
from pygameday.models import create_db_tables
from pygameday.models import db_connect

logger = logging.getLogger("pygameday")


class GameDayClient(object):
    """Class for ingesting GameDay data into a database

    Database parameters are defined in config.py.
    """
    def __init__(self, database_uri, ingest_spring_training=False, log_level="INFO"):
        """Constructor

        Initializes database connection and session
        Creates database tables if they do not already exist
        Sets up logging

        Parameters
        ----------
        database_uri : str
            The URI for the database.
            Examples: "sqlite:///gameday.db"  (sqlite)
                      "postgresql+psycopg2://user:passwd@localhost/gameday"  (Postgres via psycopg2)

            See SQLAlchemy's documentation for valid database URIs.

        ingest_spring_training : bool
            Whether to ingest spring training games. [Default: False]

        log_level : str
            The logging level. Must be one of NOTSET, DEBUG, INFO, WARN, ERROR, CRITICAL [Default: "INFO"]
        """
        util.set_logging_level(log_level)

        engine = db_connect(database_uri)
        create_db_tables(engine)
        self.Session = sessionmaker(bind=engine)
        logger.info("Initialized GameDayClient using '{}'".format(database_uri))

        self.database_uri = database_uri
        self.ingest_spring_training = ingest_spring_training
        self.player_ids = set()  # Player IDs that have already been inserted into the database
        self.gameday_ids = set()  # Game IDs that have already been inserted into the database

        self.update_inserted_data()  # Update the set of players and games that are already inserted

    def db_stats(self):
        """Prints information about the current database contents
        """
        session = self.Session()
        game_count = session.query(func.count(Game.game_id)).scalar()
        player_count = session.query(func.count(Player.player_id)).scalar()
        atbat_count = session.query(func.count(AtBat.at_bat_id)).scalar()
        pitch_count = session.query(func.count(Pitch.pitch_id)).scalar()
        hip_count = session.query(func.count(HitInPlay.hip_id)).scalar()
        session.close()

        print("")
        print("======================")
        print("{:^22}".format("DATABASE CONTENTS"))
        print("----------------------")
        print("   TABLE    |  COUNT  ")
        print("------------ ---------")
        print("{: <12} {: >8}".format("Games", game_count))
        print("{: <12} {: >8}".format("At Bats", atbat_count))
        print("{: <12} {: >8}".format("Hits in Play", hip_count))
        print("{: <12} {: >8}".format("Pitches", pitch_count))
        print("{: <12} {: >8}".format("Players", player_count))
        print("======================")
        print("")

    def update_inserted_data(self):
        """Updates the set of player IDs and Game GameDay IDs that already exist in the database

        Keeping track of games and players already inserted saves us from trying to insert objects that are already
        there.  It also helps with limiting the number of times we have to query the database.
        """
        session = self.Session()

        self.gameday_ids = {gid[0] for gid in session.query(Game.gameday_id)}
        self.player_ids = {pid[0] for pid in session.query(Player.player_id)}

        logger.debug("There are currently {} games and {} players in the database".format(
                len(self.gameday_ids), len(self.player_ids)))

    def process_date_range(self, start_date, end_date):
        """Ingests GameDay data within a range of specified dates

        All dates within the begin date and end date are processed.

        Parameters
        ----------
        start_date: datetime.date object
            The first date to process.
            Can also be a string, in which case the function will parse it into a datetime object.

        end_date: datetime.date object
            The final date to process.
            Can also be a string, in which case the function will parse it into a datetime object.
        """
        start_date = util.validate_date(start_date)  # Ensure dates are datetime objects
        end_date = util.validate_date(end_date)

        if end_date < start_date:
            tmp = end_date
            end_date = start_date
            start_date = tmp

        date_range = (end_date - start_date).days + 1  # Add 1 so the range is inclusive of begin_date and end_date

        msg = "Ingesting GameDay data within date range {} to {}".format(start_date.date(), end_date.date())
        logger.info(msg)

        for day in range(date_range):
            date = start_date + timedelta(day)
            self.process_date(date)

    def process_date(self, date):
        """Ingests one day of GameDay data

        Parameters
        ----------
        date : datetime.date object
            The date to process
            Can also be a string, in which case the function will parse it into a datetime object.
        """
        date = util.validate_date(date)  # Ensure date is a datetime object
        epg_page = scrape.fetch_epg(date.year, date.month, date.day)

        if epg_page is None:
            msg = "No games found on {}".format(date.date())
            logger.warn(msg)

        else:
            game_xml_nodes = parse.parse_epg(epg_page)
            msg = "Processing {} games on {}".format(len(game_xml_nodes), date.date())
            logger.info(msg)

            for game in game_xml_nodes:
                self.process_game(game)

    def process_game(self, game_xml_node):
        """Ingests a single game's GameDay data

        Parameters
        ----------
        game_xml_node : lxml node
            The XML node of the game to process
        """
        session = self.Session()

        game_dir = game_xml_node.get("game_data_directory")
        gameday_id = game_xml_node.get("id")

        if gameday_id in self.gameday_ids:
            # The game has been processed and should already be in the database
            logger.warn("Skipping game: {}. It's already in the DB.".format(gameday_id))
            return

        # Parse the game
        db_game = parse.parse_game(game_xml_node)

        # If no data comes back, the game probably wasn't a Final. Abort.
        if db_game is None:
            msg = ("Skipping game: {}. It contained no data, "
                   "probably because its status isn't Final").format(gameday_id)
            logger.warn(msg)
            return

        # If the game is a spring training game, skip it if ingest_spring_training is False
        if not self.ingest_spring_training and (db_game.game_type == "S" or db_game.game_type == "E"):
            msg = "Skipping game: {}. It's a spring training or exhibition game.".format(gameday_id)
            logger.warn(msg)
            return

        msg = "Processing game ID {}".format(gameday_id)
        logger.info(msg)

        # --------------------------------------------------------------------------------------------------------------
        # Fetch game data
        #
        hit_chart_page = scrape.fetch_hit_chart(game_dir)
        players_page = scrape.fetch_players(game_dir)
        inning_all_page = scrape.fetch_inning_all(game_dir)

        # do some error checking
        if hit_chart_page is None:
            msg = "Error fetching hit chart page for game {}".format(gameday_id)
            logger.error(msg)
        if players_page is None:
            msg = "Error fetching players page for game {}".format(gameday_id)
            logger.error(msg)
        if inning_all_page is None:
            msg = "Error fetching inning events page for game {}".format(gameday_id)
            logger.error(msg)

        # --------------------------------------------------------------------------------------------------------------
        # Parse AtBats (including Pitches), HitsInPlay, Players
        #
        db_at_bats = parse.parse_inning_all(inning_all_page)  # Appends Pitches to AtBats
        db_hips = parse.parse_hit_chart(hit_chart_page)
        db_players = parse.parse_players(players_page)

        # --------------------------------------------------------------------------------------------------------------
        # Append the AtBats to the Game. Note that Pitches are appended to AtBats
        # when the AtBats are parsed, so we don't have to do anything with Pitches.
        #
        for db_ab in db_at_bats:
            db_game.at_bats.append(db_ab)

        # --------------------------------------------------------------------------------------------------------------
        # Append the hits in play to the Game
        #
        for db_h in db_hips:
            db_game.hits_in_play.append(db_h)

        # --------------------------------------------------------------------------------------------------------------
        # Add the players using the database session and commit
        # This has to be done one at a time (instead of using session.add_all)
        # because add_all will fail if ANY of the players in the list are
        # duplicated, which could lead to some players being excluded from
        # the database.
        #
        for player in db_players:

            if int(player.player_id) in self.player_ids:
                # The player has been processed and should already be in the database
                logger.debug("Skipping player: {} because it has already been processed.".format(player.player_id))

            else:
                # We haven't inserted this player yet
                error_occurred = False

                try:
                    session.add(player)
                    session.commit()

                except IntegrityError:
                    # If an IntegrityError occurs, it's probably because the data
                    # has already been inserted.
                    session.rollback()
                    msg = ("IntegrityError when inserting player: {}, "
                           "probably because it's already in the database".format(str(player)))
                    logger.error(msg)
                    error_occurred = True

                except Exception as ex:
                    # Just log other exceptions for now, and continue
                    session.rollback()
                    logger.error(str(ex))
                    error_occurred = True

                if not error_occurred:
                    self.player_ids.add(player.player_id)

        # --------------------------------------------------------------------------------------------------------------
        # Add the game data
        #
        if db_game.gameday_id in self.gameday_ids:
            # The game has been processed and should already be in the database
            logger.info("Skipping game: {} because it has already been ingested.".format(db_game.gameday_id))

        else:
            # We haven't inserted this game yet
            error_occurred = False

            try:
                session.add(db_game)
                session.commit()

            except IntegrityError:
                # If an IntegrityError occurs, it's probably because the data
                # has already been inserted.
                session.rollback()
                msg = ("IntegrityError when inserting game: {}, "
                       "probably because it's already in the database".format(db_game.gameday_id))
                logger.error(msg)
                error_occurred = True

            except Exception as ex:
                # Just log other exceptions for now, and continue
                session.rollback()
                logger.error(str(ex))
                error_occurred = True

            if not error_occurred:
                self.gameday_ids.add(db_game.gameday_id)

        # We are done
        session.close()


# ----------------------------------------------------------------------------------------------------------------------
# Unit tests
#
def test_single_day():
    import config
    date_string = "2015-06-07"
    date = parser.parse(date_string)

    ingester = GameDayClient(config.DATABASE_URI)
    ingester.process_date(date)


def test_date_range():
    start_date_string = "2015-06-07"
    end_date_string = "2015-06-07"

    start_date = parser.parse(start_date_string)
    end_date = parser.parse(end_date_string)

    import config
    ingester = GameDayClient(config.DATABASE_URI)
    ingester.process_date_range(start_date, end_date)


if __name__ == "__main__":
    pass
