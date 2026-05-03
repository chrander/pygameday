#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, Float, String, Sequence, DateTime, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, declarative_base

BASE = declarative_base()


def db_connect(database_uri):
    return create_engine(database_uri)


def create_db_tables(engine):
    BASE.metadata.create_all(engine, checkfirst=True)


class Game(BASE):
    __tablename__ = 'games'

    game_id = Column(Integer, Sequence('game_id_seq'), primary_key=True)
    game_pk = Column(Integer, unique=True, index=True)   # MLB MLBAM game ID
    game_date = Column(DateTime)
    game_type = Column(String)                           # 'R' regular, 'S' spring, 'E' exhibition, etc.
    venue_name = Column(String)
    home_team = Column(String(3))
    away_team = Column(String(3))
    home_score = Column(Integer)
    away_score = Column(Integer)

    at_bats = relationship('AtBat', order_by='AtBat.at_bat_id', backref='game')
    hits_in_play = relationship('HitInPlay', order_by='HitInPlay.hip_id', backref='game')

    def __repr__(self):
        return f"<Game(game_pk={self.game_pk}, {self.away_team} at {self.home_team}, {self.game_date})>"


class AtBat(BASE):
    __tablename__ = 'at_bats'

    at_bat_id = Column(Integer, Sequence('at_bat_id_seq'), primary_key=True)
    game_id = Column(Integer, ForeignKey('games.game_id'))
    at_bat_number = Column(Integer)   # sequential within the game (1-indexed)
    inning = Column(Integer)
    inning_half = Column(String)      # 'Top' or 'Bot'
    n_pitches = Column(Integer)
    n_balls = Column(Integer)
    n_strikes = Column(Integer)
    n_outs = Column(Integer)
    batter_id = Column(Integer)
    pitcher_id = Column(Integer)
    batter_stance = Column(String)
    des = Column(String)              # description of the final pitch/outcome
    events = Column(String)           # at-bat result (e.g. 'single', 'strikeout')

    pitches = relationship('Pitch', order_by='Pitch.pitch_id', backref='at_bat')

    def __repr__(self):
        return f"<AtBat(at_bat_id={self.at_bat_id}, batter={self.batter_id}, events={self.events})>"


class Pitch(BASE):
    __tablename__ = 'pitches'

    pitch_id = Column(Integer, Sequence('pitch_id_seq'), primary_key=True)
    at_bat_id = Column(Integer, ForeignKey('at_bats.at_bat_id'))
    at_bat_pitch_num = Column(Integer)  # 0-indexed within the at-bat
    inning = Column(Integer)
    inning_half = Column(String)
    des = Column(String)                # pitch outcome description
    result_type = Column(String)        # 'B' ball, 'S' strike, 'X' in play
    pitch_type = Column(String)
    zone = Column(Integer)
    # Velocity
    release_speed = Column(Float)
    effective_speed = Column(Float)
    # Location at plate (feet, catcher's perspective)
    plate_x = Column(Float)
    plate_z = Column(Float)
    # Strike zone bounds
    sz_top = Column(Float)
    sz_bot = Column(Float)
    # Pitch movement (inches)
    pfx_x = Column(Float)
    pfx_z = Column(Float)
    # Release point (feet)
    release_pos_x = Column(Float)
    release_pos_y = Column(Float)
    release_pos_z = Column(Float)
    # Initial velocity components (ft/s)
    vx0 = Column(Float)
    vy0 = Column(Float)
    vz0 = Column(Float)
    # Acceleration components (ft/s²)
    ax = Column(Float)
    ay = Column(Float)
    az = Column(Float)
    # Spin
    spin_rate = Column(Float)           # RPM (Statcast: release_spin_rate)
    spin_axis = Column(Float)           # degrees
    release_extension = Column(Float)   # feet from rubber at release

    def __repr__(self):
        return f"<Pitch(pitch_type={self.pitch_type}, release_speed={self.release_speed}, result_type={self.result_type})>"


class Player(BASE):
    __tablename__ = 'players'

    player_id = Column(Integer, primary_key=True)   # MLBAM ID
    first = Column(String)
    last = Column(String)
    bats = Column(String)    # batting stance ('R', 'L', 'S')
    throws = Column(String)  # throwing hand ('R', 'L')

    def __repr__(self):
        return f"<Player(player_id={self.player_id}, {self.first} {self.last})>"


class HitInPlay(BASE):
    __tablename__ = 'hits_in_play'

    hip_id = Column(Integer, Sequence('hip_id_sequence'), primary_key=True)
    game_id = Column(Integer, ForeignKey('games.game_id'))
    batter_id = Column(Integer)
    pitcher_id = Column(Integer)
    inning = Column(Integer)
    inning_half = Column(String)
    bb_type = Column(String)        # 'fly_ball', 'ground_ball', 'line_drive', 'popup'
    hc_x = Column(Float)            # hit coordinate x (pixels on field diagram)
    hc_y = Column(Float)            # hit coordinate y
    launch_speed = Column(Float)    # exit velocity (mph)
    launch_angle = Column(Float)    # degrees
    des = Column(String)

    def __repr__(self):
        return f"<HitInPlay(batter_id={self.batter_id}, pitcher_id={self.pitcher_id}, bb_type={self.bb_type})>"
