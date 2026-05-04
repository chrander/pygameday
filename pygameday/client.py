#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Defines StatcastClient, the primary class for ingesting MLB Statcast data."""
import logging
from datetime import timedelta

from tqdm import tqdm
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from . import parse
from . import scrape
from .models import Game, Player, AtBat, Pitch, HitInPlay, create_db_tables, db_connect

logger = logging.getLogger(__name__)


class StatcastClient:
    """Ingests MLB Statcast data (via pybaseball) into a SQLAlchemy-backed database."""

    def __init__(self, database_uri, ingest_spring_training=False):
        """Initialize the client and connect to the database.

        Parameters
        ----------
        database_uri : str
            SQLAlchemy connection string, e.g. "sqlite:///gameday.db" or
            "postgresql+psycopg2://user:passwd@localhost/gameday".
        ingest_spring_training : bool
            Whether to ingest spring training ('S') and exhibition ('E') games.
        """
        engine = db_connect(database_uri)
        create_db_tables(engine)
        logger.info(f"Initialized StatcastClient using '{database_uri}'")

        self.database_uri = database_uri
        self.ingest_spring_training = ingest_spring_training
        self.game_pks = set()
        self.player_ids = set()

        self.update_inserted_data()

    def db_stats(self):
        """Print a summary of row counts for each table in the database."""
        engine = db_connect(self.database_uri)
        session = sessionmaker(bind=engine)()
        game_count = session.query(func.count(Game.game_id)).scalar()
        player_count = session.query(func.count(Player.player_id)).scalar()
        atbat_count = session.query(func.count(AtBat.at_bat_id)).scalar()
        pitch_count = session.query(func.count(Pitch.pitch_id)).scalar()
        hip_count = session.query(func.count(HitInPlay.hip_id)).scalar()
        session.close()

        print("")
        print("======================")
        print(f"{'DATABASE CONTENTS':^22}")
        print("----------------------")
        print("   TABLE    |  COUNT  ")
        print("------------ ---------")
        print(f"{'Games': <12} {game_count: >8}")
        print(f"{'At Bats': <12} {atbat_count: >8}")
        print(f"{'Hits in Play': <12} {hip_count: >8}")
        print(f"{'Pitches': <12} {pitch_count: >8}")
        print(f"{'Players': <12} {player_count: >8}")
        print("======================")
        print("")

    def update_inserted_data(self):
        """Refresh in-memory sets of already-ingested game_pks and player_ids."""
        engine = db_connect(self.database_uri)
        session = sessionmaker(bind=engine)()
        self.game_pks = {row[0] for row in session.query(Game.game_pk)}
        self.player_ids = {row[0] for row in session.query(Player.player_id)}
        session.close()
        logger.debug(f'Database contains {len(self.game_pks)} games and {len(self.player_ids)} players')

    def process_date_range(self, start_date, end_date):
        """Ingest all games within an inclusive date range.

        Parameters
        ----------
        start_date, end_date : datetime.datetime
        """
        if end_date < start_date:
            start_date, end_date = end_date, start_date

        date_range = [start_date + timedelta(days=d)
                      for d in range((end_date - start_date).days + 1)]
        logger.info(f'Ingesting Statcast data from {start_date.date()} to {end_date.date()}')

        for date in tqdm(date_range, total=len(date_range)):
            self.process_date(date)

    def process_date(self, date):
        """Ingest all games played on a single date.

        Parameters
        ----------
        date : datetime.datetime
        """
        df = scrape.fetch_statcast_data(date, date)
        if df is None or df.empty:
            logger.warning(f'No Statcast data returned for {date.date()}')
            return

        for game_pk, gdf in df.groupby('game_pk'):
            game_pk = int(game_pk)

            if game_pk in self.game_pks:
                logger.warning(f'Skipping game {game_pk} (already in DB)')
                continue

            game_type = gdf.iloc[-1].get('game_type', '')
            if not self.ingest_spring_training and game_type in ('S', 'E'):
                logger.info(f'Skipping spring training/exhibition game {game_pk}')
                continue

            self._process_game(game_pk, gdf)

    def _process_game(self, game_pk, gdf):
        """Parse and insert a single game's data (players, at-bats, pitches, hits in play)."""
        engine = db_connect(self.database_uri)
        session = sessionmaker(bind=engine)()
        logger.info(f'Processing game {game_pk}')

        try:
            db_games = parse.parse_games(gdf)
            if not db_games:
                logger.warning(f'No game object parsed for game_pk {game_pk}')
                return
            db_game = db_games[0]
            db_game.at_bats = parse.parse_at_bats(gdf)
            db_game.hits_in_play = parse.parse_hits_in_play(gdf)
            db_players = parse.parse_players(gdf)

            for player in db_players:
                if player.player_id in self.player_ids:
                    continue
                try:
                    session.add(player)
                    session.commit()
                    self.player_ids.add(player.player_id)
                except IntegrityError:
                    session.rollback()
                except Exception:
                    session.rollback()
                    logger.exception(f'Error inserting player {player.player_id}')

            try:
                session.add(db_game)
                session.commit()
                self.game_pks.add(game_pk)
            except IntegrityError:
                session.rollback()
                logger.error(f'IntegrityError inserting game {game_pk} (already exists)')
            except Exception:
                session.rollback()
                logger.exception(f'Error inserting game {game_pk}')

        finally:
            session.close()
