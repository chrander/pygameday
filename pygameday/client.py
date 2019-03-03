#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Defines GameDayClient, the primary class for scraping, parsing, and ingesting MLB GameDay data.
"""
import logging
from datetime import timedelta
from concurrent.futures import ProcessPoolExecutor

from tqdm import tqdm
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from . import util
from . import parse
from . import scrape
from .models import Game
from .models import Player
from .models import AtBat
from .models import Pitch
from .models import HitInPlay
from .models import create_db_tables
from .models import db_connect

logger = logging.getLogger('pygameday')


class GameDayClient(object):
    """Class for ingesting GameDay data into a database
    """
    def __init__(self, database_uri, ingest_spring_training=False, n_workers=4, log_level="INFO"):
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

        n_workers : int
            The number of parallel workers to use when ingesting games

        log_level : str
            The logging level. Must be one of NOTSET, DEBUG, INFO, WARN, ERROR, CRITICAL [Default: "INFO"]
        """
        util.set_logging_level(log_level)

        engine = db_connect(database_uri)
        create_db_tables(engine)
        logger.info("Initialized GameDayClient using '{}'".format(database_uri))

        self.database_uri = database_uri
        self.ingest_spring_training = ingest_spring_training
        self.n_workers = n_workers
        self.player_ids = set()  # Player IDs that have already been inserted into the database
        self.gameday_ids = set()  # Game IDs that have already been inserted into the database

        self.update_inserted_data()  # Update the set of players and games that are already inserted

    def db_stats(self):
        """Prints information about the current database contents
        """
        engine = db_connect(self.database_uri)
        session_maker = sessionmaker(bind=engine)
        session = session_maker()

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
        engine = db_connect(self.database_uri)
        session_maker = sessionmaker(bind=engine)
        session = session_maker()

        self.gameday_ids = {gid[0] for gid in session.query(Game.gameday_id)}
        self.player_ids = {pid[0] for pid in session.query(Player.player_id)}
        session.close()

        logger.debug('There are currently {} games and {} players in the database'.format(
                len(self.gameday_ids), len(self.player_ids)))

    def process_date_range(self, start_date, end_date):
        """Ingests GameDay data within a range of specified dates

        All dates within the begin date and end date are processed.

        Parameters
        ----------
        start_date: datetime.datetime
            The first date to process.
            Can also be a string, in which case the function will parse it into a datetime object.

        end_date: datetime.date object
            The final date to process.
            Can also be a string, in which case the function will parse it into a datetime object.
        """
        if end_date < start_date:
            logger.info('Swapping start date and end date to preserve causality')
            tmp = end_date
            end_date = start_date
            start_date = tmp

        # Construct the dates to iterate over. We add 1 to the range so that it is inclusive of begin_date and end_date.
        date_range = [start_date + timedelta(day) for day in range((end_date - start_date).days + 1)]

        logger.info('Ingesting GameDay data within date range {} to {}'.format(start_date.date(), end_date.date()))

        for date in tqdm(date_range, total=len(date_range)):
            self.process_date(date)

    def process_date(self, date):
        """Ingests one day of GameDay data

        Parameters
        ----------
        date : datetime.datetime
            The date to process
        """
        scoreboard = scrape.fetch_master_scoreboard(date)

        # Check if there are games on the date. If not, skip it.
        game_data = scoreboard['data']['games']
        if 'game' not in game_data or len(game_data['game']) == 0:
            logger.warning('No games found on {}'.format(date.date()))

        else:
            games = scoreboard['data']['games']['game']

            if self.n_workers > 1:
                # Process games in parallel
                with ProcessPoolExecutor(max_workers=self.n_workers) as executor:
                    executor.map(self.process_game, games)
            else:
                # Process games serially
                for game in games:
                    self.process_game(game)

    # TODO: clean up this function
    def process_game(self, game):
        """Ingests a single game's GameDay data

        Parameters
        ----------
        game : dict
            The game to process
        """
        # Create a new connection for each game so we don't run into weirdness with connections shared across
        # processes or threads
        engine = db_connect(self.database_uri)
        session_maker = sessionmaker(bind=engine)
        session = session_maker()

        game_dir = game["game_data_directory"]
        gameday_id = game["id"]

        if gameday_id in self.gameday_ids:
            # The game has been processed and should already be in the database
            logger.warning("Skipping game: {}. It's already in the DB.".format(gameday_id))
            return

        # Parse the game
        db_game = parse.parse_game(game)

        # If no data comes back, the game probably wasn't Final. Abort.
        if db_game is None:
            logger.warning("Skipping game: {}. It contained no data, probably because its status isn't Final".format(
                gameday_id))
            return

        # If the game is a spring training game, skip it if ingest_spring_training is False
        # A games type of 'S' (spring training) or 'E' (exhibition) means we won't ingest it if the flag is False
        if not self.ingest_spring_training and (db_game.game_type == "S" or db_game.game_type == "E"):
            logger.warning("Skipping game: {}. It's a spring training or exhibition game.".format(gameday_id))
            return

        logger.info("Processing game ID {}".format(gameday_id))

        #
        # Fetch game data
        #
        hit_chart_page = scrape.fetch_hit_chart(game_dir)
        players_page = scrape.fetch_players(game_dir)
        inning_all_page = scrape.fetch_inning_all(game_dir)

        # Do some error checking
        if hit_chart_page is None:
            logger.error("Error fetching hit chart page for game {}".format(gameday_id))
        if players_page is None:
            logger.error("Error fetching players page for game {}".format(gameday_id))
        if inning_all_page is None:
            logger.error("Error fetching inning events page for game {}".format(gameday_id))

        #
        # Parse AtBats (including Pitches), HitsInPlay, Players
        #
        db_at_bats = parse.parse_inning_all(inning_all_page)  # Appends Pitches to AtBats
        db_hips = parse.parse_hit_chart(hit_chart_page)
        db_players = parse.parse_players(players_page)

        #
        # Append the AtBats to the Game. Note that Pitches are appended to AtBats
        # when the AtBats are parsed, so we don't have to do anything with Pitches.
        #
        db_game.at_bats.extend(db_at_bats)

        #
        # Append the hits in play to the Game
        #
        db_game.hits_in_play.extend(db_hips)

        #
        # Add the players using the database session and commit
        # This has to be done one at a time (instead of using session.add_all)
        # because add_all will fail if ANY of the players in the list are
        # duplicated, which could lead to some players being excluded from
        # the database.
        #
        for player in db_players:

            if int(player.player_id) in self.player_ids:
                # The player has been processed and should already be in the database
                logger.debug("Skipping player {} because it has already been processed.".format(player.player_id))

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
                    msg = ("IntegrityError when inserting player {}, "
                           "probably because it's already in the database".format(str(player)))
                    logger.warning(msg)
                    error_occurred = True

                except Exception as ex:
                    # Just log other exceptions for now, and continue
                    session.rollback()
                    logger.exception('An error occurred', ex)
                    error_occurred = True

                if not error_occurred:
                    self.player_ids.add(player.player_id)

        #
        # Insert the game data
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
                logger.exception('Something went wrong', ex)
                error_occurred = True

            if not error_occurred:
                self.gameday_ids.add(db_game.gameday_id)

        # We are done
        session.close()
