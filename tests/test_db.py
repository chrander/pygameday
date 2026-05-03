import pytest
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from pygameday.models import Game, AtBat, Pitch, Player, HitInPlay, create_db_tables, db_connect


@pytest.fixture
def session():
    engine = db_connect('sqlite:///:memory:')
    create_db_tables(engine)
    s = sessionmaker(bind=engine)()
    yield s
    s.close()


def test_insert_game_with_at_bat_and_pitch(session):
    player = Player(player_id=116380, first='Mike', last='Trout', bats='R', throws='R')
    session.add(player)
    session.commit()

    pitch = Pitch(
        at_bat_pitch_num=0,
        inning=1, inning_half='Top',
        des='Ball', result_type='B',
        pitch_type='FF', zone=11,
        release_speed=96.4, effective_speed=94.1,
        plate_x=0.14, plate_z=2.5,
        sz_top=3.5, sz_bot=1.6,
        pfx_x=-4.2, pfx_z=8.1,
        release_pos_x=-1.5, release_pos_y=54.2, release_pos_z=6.1,
        vx0=6.3, vy0=-140.1, vz0=-5.2,
        ax=-8.1, ay=28.4, az=-14.3,
        spin_rate=2340.0, spin_axis=210.0, release_extension=6.2,
    )
    at_bat = AtBat(
        at_bat_number=1,
        inning=1, inning_half='Top',
        n_pitches=1, n_balls=1, n_strikes=0, n_outs=0,
        batter_id=116380, pitcher_id=999999,
        batter_stance='R', des='Ball', events=None,
    )
    at_bat.pitches.append(pitch)

    game = Game(
        game_pk=748532, game_date=datetime(2023, 7, 4),
        game_type='R', venue_name='Angel Stadium',
        home_team='LAA', away_team='HOU',
        home_score=3, away_score=5,
    )
    game.at_bats.append(at_bat)
    session.add(game)
    session.commit()

    result = session.query(Game).filter_by(game_pk=748532).first()
    assert result is not None
    assert result.home_team == 'LAA'
    assert len(result.at_bats) == 1
    assert len(result.at_bats[0].pitches) == 1


def test_duplicate_game_raises_integrity_error(session):
    game1 = Game(game_pk=111111, game_date=datetime(2023, 7, 4), home_team='BOS', away_team='NYY')
    game2 = Game(game_pk=111111, game_date=datetime(2023, 7, 4), home_team='BOS', away_team='NYY')
    session.add(game1)
    session.commit()
    session.add(game2)
    with pytest.raises(IntegrityError):
        session.commit()


def test_hit_in_play(session):
    game = Game(game_pk=222222, game_date=datetime(2023, 7, 4), home_team='LAD', away_team='SFG')
    hip = HitInPlay(
        batter_id=660271, pitcher_id=543037,
        inning=3, inning_half='Top',
        bb_type='fly_ball',
        hc_x=120.5, hc_y=90.3,
        launch_speed=105.2, launch_angle=28.0,
        des='Mookie Betts homers (12)',
    )
    game.hits_in_play.append(hip)
    session.add(game)
    session.commit()

    result = session.query(Game).filter_by(game_pk=222222).first()
    assert len(result.hits_in_play) == 1
    assert result.hits_in_play[0].launch_speed == pytest.approx(105.2)
