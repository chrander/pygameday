import pytest
import pandas as pd

from pygameday import parse
from pygameday.models import Game, AtBat, Pitch, Player, HitInPlay


def _make_pitch_row(**kwargs):
    """Build a minimal statcast-like row dict with sensible defaults."""
    defaults = {
        'game_pk': 748532,
        'game_date': '2023-07-04',
        'game_type': 'R',
        'venue_name': 'Angel Stadium',
        'home_team': 'LAA',
        'away_team': 'HOU',
        'home_score': 3,
        'away_score': 5,
        'at_bat_number': 1,
        'pitch_number': 1,
        'inning': 1,
        'inning_topbot': 'Top',
        'balls': 0,
        'strikes': 0,
        'outs_when_up': 0,
        'batter': 660271,
        'pitcher': 543037,
        'player_name': 'Kershaw, Clayton',
        'p_throws': 'L',
        'stand': 'R',
        'des': 'Called Strike',
        'description': 'called_strike',
        'events': float('nan'),
        'type': 'S',
        'pitch_type': 'CU',
        'zone': 9,
        'release_speed': 73.4,
        'effective_speed': 71.2,
        'plate_x': -0.21,
        'plate_z': 1.82,
        'sz_top': 3.42,
        'sz_bot': 1.61,
        'pfx_x': 5.1,
        'pfx_z': -8.3,
        'release_pos_x': -2.3,
        'release_pos_y': 54.1,
        'release_pos_z': 6.0,
        'vx0': -4.2,
        'vy0': -106.8,
        'vz0': -4.9,
        'ax': 7.3,
        'ay': 24.1,
        'az': -37.2,
        'release_spin_rate': 2750.0,
        'spin_axis': 55.0,
        'release_extension': 6.1,
        'bb_type': float('nan'),
        'hc_x': float('nan'),
        'hc_y': float('nan'),
        'launch_speed': float('nan'),
        'launch_angle': float('nan'),
    }
    defaults.update(kwargs)
    return defaults


# ---------------------------------------------------------------------------
# parse_games
# ---------------------------------------------------------------------------

def test_parse_single_game():
    df = pd.DataFrame([_make_pitch_row()])
    games = parse.parse_games(df)
    assert len(games) == 1
    g = games[0]
    assert isinstance(g, Game)
    assert g.game_pk == 748532
    assert g.home_team == 'LAA'
    assert g.away_team == 'HOU'
    assert g.game_type == 'R'


def test_parse_two_games():
    df = pd.DataFrame([_make_pitch_row(game_pk=1), _make_pitch_row(game_pk=2)])
    assert len(parse.parse_games(df)) == 2


# ---------------------------------------------------------------------------
# parse_players
# ---------------------------------------------------------------------------

def test_pitcher_has_name():
    players = parse.parse_players(pd.DataFrame([_make_pitch_row()]))
    pitcher = next(p for p in players if p.player_id == 543037)
    assert pitcher.last == 'Kershaw'
    assert pitcher.first == 'Clayton'
    assert pitcher.throws == 'L'


def test_batter_without_name():
    players = parse.parse_players(pd.DataFrame([_make_pitch_row()]))
    batter = next((p for p in players if p.player_id == 660271), None)
    assert batter is not None
    assert batter.bats == 'R'


def test_no_duplicate_players():
    players = parse.parse_players(pd.DataFrame([_make_pitch_row(), _make_pitch_row()]))
    ids = [p.player_id for p in players]
    assert len(ids) == len(set(ids))


# ---------------------------------------------------------------------------
# parse_at_bats
# ---------------------------------------------------------------------------

def test_single_at_bat_three_pitches():
    rows = [
        _make_pitch_row(at_bat_number=1, pitch_number=1, type='B', events=float('nan')),
        _make_pitch_row(at_bat_number=1, pitch_number=2, type='S', events=float('nan')),
        _make_pitch_row(at_bat_number=1, pitch_number=3, type='S', events='strikeout'),
    ]
    at_bats = parse.parse_at_bats(pd.DataFrame(rows))
    assert len(at_bats) == 1
    ab = at_bats[0]
    assert isinstance(ab, AtBat)
    assert ab.n_pitches == 3
    assert ab.events == 'strikeout'
    assert len(ab.pitches) == 3
    for i, p in enumerate(ab.pitches):
        assert p.at_bat_pitch_num == i


# ---------------------------------------------------------------------------
# parse_hits_in_play
# ---------------------------------------------------------------------------

def test_only_in_play_rows_extracted():
    rows = [
        _make_pitch_row(type='B'),
        _make_pitch_row(type='S'),
        _make_pitch_row(type='X', bb_type='fly_ball',
                        hc_x=110.0, hc_y=85.0,
                        launch_speed=104.5, launch_angle=27.0),
    ]
    hips = parse.parse_hits_in_play(pd.DataFrame(rows))
    assert len(hips) == 1
    h = hips[0]
    assert isinstance(h, HitInPlay)
    assert h.bb_type == 'fly_ball'
    assert h.launch_speed == pytest.approx(104.5)


def test_no_in_play_rows():
    rows = [_make_pitch_row(type='B'), _make_pitch_row(type='S')]
    assert parse.parse_hits_in_play(pd.DataFrame(rows)) == []
