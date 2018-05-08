#!/usr/bin/python
#
# import sys

# sys.path.append("..")

# from dateutil import parser
from datetime import datetime

from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from pygameday.models import Game, AtBat, Pitch, Player
from pygameday.models import create_db_tables
from pygameday.models import db_connect
import config


def test():
    """Test database functionality """

    engine = db_connect(config.DATABASE_URI)
    create_db_tables(engine)
    sm = sessionmaker(bind=engine)
    session = sm()

    player = gen_fake_player_data()
    game = gen_fake_game_data()
    atbat = gen_fake_atbat_data()
    pitch = gen_fake_pitch_data()

    atbat.pitches.append(pitch)
    game.at_bats.append(atbat)
    # game.pitches.append(pitch)

    try:
        session.add(player)
        session.commit()
        print("Committed player: {}".format(str(player)))

    except IntegrityError:
        session.rollback()
        msg = "IntegrityError when inserting player: {}".format(str(player))
        print(msg)

    except Exception as ex:
        session.rollback()
        msg = "Exception when inserting player"
        print(msg)
        print(ex)

    try:
        session.add(game)
        session.commit()
        print("Committed game: {}".format(str(game)))

    except Exception as ex:
        session.rollback()
        msg = "Exception when inserting game"
        print(msg)
        print(ex)


def gen_fake_game_data():
    """Creates an example Game object"""
    game = Game(
        gameday_id='2014/04/04/atlmlb-wasmlb-1',
        venue='Nationals Park',
        # start_time=parser.parse('2014-04-04T13:05:00-0400'),
        start_time=datetime.strptime('2014-04-04T13:05:00-0400', '%Y-%m-%dT%H:%M:%S%z'),
        game_data_directory='/components/game/mlb/year_2014/month_04/day_04/gid_2014_04_04_atlmlb_wasmlb_1',
        home_name_abbrev='WSH',
        home_team_city='Washington',
        home_team_name='Nationals',
        away_name_abbrev='ATL',
        away_team_city='Atlanta',
        away_team_name='Braves',
        home_team_runs=1,
        away_team_runs=2
    )

    return game


def gen_fake_atbat_data():
    """Creates an example AtBat object"""
    at_bat = AtBat(
        inning=1,
        inning_half='T',
        n_pitches=3,
        n_balls=1,
        n_strikes=1,
        n_outs=1,
        batter_id=116380,
        pitcher_id=116380,
        batter_stance='R',
        des='Mike Trout homers to left center',
        event='Home Run'
    )

    return at_bat


def gen_fake_pitch_data():
    """Creates an example Pitch object"""
    pitch = Pitch(
        inning=1,
        inning_half='T',
        des='Ball',
        result_type='B',
        gameday_sv_id='140404_191151',
        x=92.70,
        y=181.33,
        start_speed=85.7,
        end_speed=78.9,
        sz_top=3.66,
        sz_bot=1.75,
        pfx_x=-2.86,
        pfx_z=5.87,
        px=0.141,
        pz=1.004,
        x0=-2.59,
        y0=50.0,
        z0=5.953,
        vx0=7.645,
        vy0=-125.205,
        vz0=-7.503,
        ax=-4.503,
        ay=26.885,
        az=-22.844,
        break_y=23.8,
        break_angle=7.0,
        break_length=4.9,
        pitch_type='FT',
        type_conf=0.890,
        zone=11,
        nasty=59,
        spin_dir=230.193,
        spin_rate=1042.434
        )

    return pitch


def gen_fake_player_data():
    """Generates an example Player object"""
    player = Player(
            player_id=116380,
            first="Raul",
            last="Ibanez",
            boxname="Ibanez",
            rl="R",
            bats="L",
            )

    return player


if __name__ == '__main__':
    test()
