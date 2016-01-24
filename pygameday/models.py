#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Defines classes for database mappings, plus some database helper functions
"""
from __future__ import print_function, division, absolute_import

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Float
from sqlalchemy import String
from sqlalchemy import Sequence
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


BASE = declarative_base()


def db_connect(database_uri):
    """Connects to a database using database settings in config.py

    Parameters
    ----------
    database_uri : str
        The database URI.
        Examples: "postgresql+psycopg2://user:passwd@localhost/dbname"
                  "sqlite:///dbname.db"

    Returns
    -------
    engine : sqlalchemy engine instance
    """
    return create_engine(database_uri)


def create_db_tables(engine):
    """Creates database tables

    Parameters
    ----------
    engine : sqlalchemy engine instance
    """
    BASE.metadata.create_all(engine, checkfirst=True)


class Game(BASE):
    __tablename__ = 'games'

    game_id = Column(Integer, Sequence('game_id_seq'), primary_key=True)
    gameday_id = Column(String, unique=True, index=True)
    venue = Column(String)
    start_time = Column(DateTime)
    game_data_directory = Column(String)
    game_type = Column(String)
    home_name_abbrev = Column(String(3))
    home_team_city = Column(String)
    home_team_name = Column(String)
    away_name_abbrev = Column(String(3))
    away_team_city = Column(String)
    away_team_name = Column(String)
    home_team_runs = Column(Integer)
    away_team_runs = Column(Integer)
    league = Column(String)

    at_bats = relationship('AtBat', order_by='AtBat.at_bat_id', backref='games')
    hits_in_play = relationship('HitInPlay', order_by='HitInPlay.hip_id', backref='games')

    def __repr__(self):
        return "<Game(game_id=\'{}\', time=\'{}\', {} {} at {} {})>" \
                    .format(self.game_id, self.start_time,
                            self.away_team_city, self.away_team_name,
                            self.home_team_city, self.home_team_name)


class AtBat(BASE):
    __tablename__ = 'at_bats'

    at_bat_id = Column(Integer, Sequence('at_bat_id_seq'), primary_key=True)
    game_id = Column(Integer, ForeignKey('games.game_id'))
    inning = Column(Integer)
    inning_half = Column(String)
    n_pitches = Column(Integer)
    n_balls = Column(Integer)
    n_strikes = Column(Integer)
    n_outs = Column(Integer)
    batter_id = Column(Integer)
    pitcher_id = Column(Integer)
    batter_stance = Column(String)
    des = Column(String)
    event = Column(String)

    pitches = relationship('Pitch', order_by='Pitch.pitch_id', backref='at_bats')

    def __repr__(self):
        return "<AtBat(at_bat_id={}, batter_id={}, pitcher_id={}, des={})>" \
                .format(self.at_bat_id, self.batter_id, self.pitcher_id, self.des)


class Pitch(BASE):
    __tablename__ = 'pitches'

    pitch_id = Column(Integer, Sequence('pitch_id_seq'), primary_key=True)
    at_bat_id = Column(Integer, ForeignKey('at_bats.at_bat_id'))
    at_bat_pitch_num = Column(Integer)
    inning = Column(Integer)
    inning_half = Column(String)
    des = Column(String)
    result_type = Column(String)
    gameday_sv_id = Column(String)
    x = Column(Float)
    y = Column(Float)
    start_speed = Column(Float)
    end_speed = Column(Float)
    sz_top = Column(Float)
    sz_bot = Column(Float)
    pfx_x = Column(Float)
    pfx_z = Column(Float)
    px = Column(Float)
    pz = Column(Float)
    x0 = Column(Float)
    y0 = Column(Float)
    z0 = Column(Float)
    vx0 = Column(Float)
    vy0 = Column(Float)
    vz0 = Column(Float)
    ax = Column(Float)
    ay = Column(Float)
    az = Column(Float)
    break_y = Column(Float)
    break_angle = Column(Float)
    break_length = Column(Float)
    pitch_type = Column(String)
    type_conf = Column(String)
    zone = Column(Integer)
    nasty = Column(Integer)
    spin_dir = Column(Float)
    spin_rate = Column(Float)

    def __repr__(self):
        return "<Pitch(pitch_type={}, start_speed={}, result_type={}, des={})>" \
                .format(self.pitch_type, self.start_speed, self.result_type, self.des)


class Player(BASE):
    __tablename__ = 'players'

    player_id = Column(Integer, primary_key=True)
    first = Column(String)
    last = Column(String)
    boxname = Column(String)
    rl = Column(String)
    bats = Column(String)

    def __repr__(self):
        return "<Player(player_id={}, {} {})>" \
            .format(self.player_id, self.first, self.last)


class HitInPlay(BASE):
    __tablename__ = 'hits_in_play'

    hip_id = Column(Integer, Sequence('hip_id_sequence'), primary_key=True)
    game_id = Column(Integer, ForeignKey('games.game_id'))
    batter_id = Column(Integer)
    pitcher_id = Column(Integer)
    des = Column(String)
    hip_type = Column(String)
    team = Column(String)
    inning = Column(Integer)
    x = Column(Float)
    y = Column(Float)

    def __repr__(self):
        return "<HitInPlay(batter_id={}, pitcher_id={}, {})>" \
            .format(self.batter_id, self.pitcher_id, self.des)
