#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Converts pybaseball Statcast DataFrames into SQLAlchemy model instances."""
import logging
from datetime import datetime

import pandas as pd

from .models import AtBat, Game, HitInPlay, Pitch, Player

logger = logging.getLogger(__name__)


def _safe(value, cast=None):
    """Return None for NaN/None values; optionally cast to a type."""
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    return cast(value) if cast else value


def parse_games(df):
    """Extract one Game object per unique game_pk from a Statcast DataFrame.

    Uses the last pitch row per game for final score and metadata since
    home_score/away_score reflect the running total through each pitch.
    """
    games = []
    for game_pk, gdf in df.groupby('game_pk'):
        last = gdf.iloc[-1]
        game_date = _safe(last.get('game_date'))
        if isinstance(game_date, str):
            game_date = datetime.strptime(game_date, '%Y-%m-%d')

        games.append(Game(
            game_pk=int(game_pk),
            game_date=game_date,
            game_type=_safe(last.get('game_type')),
            venue_name=_safe(last.get('venue_name')),
            home_team=_safe(last.get('home_team')),
            away_team=_safe(last.get('away_team')),
            home_score=_safe(last.get('home_score'), int),
            away_score=_safe(last.get('away_score'), int),
        ))
    return games


def parse_players(df):
    """Extract unique Player objects from a Statcast DataFrame.

    Pitchers: name available from 'player_name' ("Last, First"), throwing hand from 'p_throws'.
    Batters: only MLBAM ID and batting stance available without a separate lookup.
    If a player appears as both batter and pitcher, the pitcher record (with name) takes precedence.
    """
    players = {}

    for pitcher_id, group in df.groupby('pitcher'):
        pid = int(pitcher_id)
        row = group.iloc[0]
        name = _safe(row.get('player_name')) or ''
        parts = name.split(', ', 1) if ', ' in name else [name, '']
        players[pid] = Player(
            player_id=pid,
            last=parts[0],
            first=parts[1] if len(parts) > 1 else '',
            throws=_safe(row.get('p_throws')),
        )

    for batter_id, group in df.groupby('batter'):
        bid = int(batter_id)
        if bid not in players:
            row = group.iloc[0]
            players[bid] = Player(
                player_id=bid,
                bats=_safe(row.get('stand')),
            )

    return list(players.values())


def parse_at_bats(gdf):
    """Extract AtBat (and nested Pitch) objects from a single-game Statcast DataFrame."""
    at_bats = []
    sort_col = 'pitch_number' if 'pitch_number' in gdf.columns else None

    for ab_num, abdf in gdf.groupby('at_bat_number'):
        if sort_col:
            abdf = abdf.sort_values(sort_col)
        last = abdf.iloc[-1]

        ab = AtBat(
            at_bat_number=int(ab_num),
            inning=_safe(last.get('inning'), int),
            inning_half=_safe(last.get('inning_topbot')),
            n_pitches=len(abdf),
            n_balls=_safe(last.get('balls'), int),
            n_strikes=_safe(last.get('strikes'), int),
            n_outs=_safe(last.get('outs_when_up'), int),
            batter_id=_safe(last.get('batter'), int),
            pitcher_id=_safe(last.get('pitcher'), int),
            batter_stance=_safe(last.get('stand')),
            des=_safe(last.get('des')),
            events=_safe(last.get('events')),
        )

        for i, (_, row) in enumerate(abdf.iterrows()):
            ab.pitches.append(_parse_pitch(row, i))

        at_bats.append(ab)
    return at_bats


def _parse_pitch(row, index):
    return Pitch(
        at_bat_pitch_num=index,
        inning=_safe(row.get('inning'), int),
        inning_half=_safe(row.get('inning_topbot')),
        des=_safe(row.get('description')),
        result_type=_safe(row.get('type')),
        pitch_type=_safe(row.get('pitch_type')),
        zone=_safe(row.get('zone'), int),
        release_speed=_safe(row.get('release_speed'), float),
        effective_speed=_safe(row.get('effective_speed'), float),
        plate_x=_safe(row.get('plate_x'), float),
        plate_z=_safe(row.get('plate_z'), float),
        sz_top=_safe(row.get('sz_top'), float),
        sz_bot=_safe(row.get('sz_bot'), float),
        pfx_x=_safe(row.get('pfx_x'), float),
        pfx_z=_safe(row.get('pfx_z'), float),
        release_pos_x=_safe(row.get('release_pos_x'), float),
        release_pos_y=_safe(row.get('release_pos_y'), float),
        release_pos_z=_safe(row.get('release_pos_z'), float),
        vx0=_safe(row.get('vx0'), float),
        vy0=_safe(row.get('vy0'), float),
        vz0=_safe(row.get('vz0'), float),
        ax=_safe(row.get('ax'), float),
        ay=_safe(row.get('ay'), float),
        az=_safe(row.get('az'), float),
        spin_rate=_safe(row.get('release_spin_rate'), float),
        spin_axis=_safe(row.get('spin_axis'), float),
        release_extension=_safe(row.get('release_extension'), float),
    )


def parse_hits_in_play(gdf):
    """Extract HitInPlay objects from a single-game Statcast DataFrame.

    Selects only rows where result_type == 'X' (ball put in play).
    """
    if 'type' not in gdf.columns:
        return []
    hip_df = gdf[gdf['type'] == 'X']
    hips = []
    for _, row in hip_df.iterrows():
        hips.append(HitInPlay(
            batter_id=_safe(row.get('batter'), int),
            pitcher_id=_safe(row.get('pitcher'), int),
            inning=_safe(row.get('inning'), int),
            inning_half=_safe(row.get('inning_topbot')),
            bb_type=_safe(row.get('bb_type')),
            hc_x=_safe(row.get('hc_x'), float),
            hc_y=_safe(row.get('hc_y'), float),
            launch_speed=_safe(row.get('launch_speed'), float),
            launch_angle=_safe(row.get('launch_angle'), float),
            des=_safe(row.get('des')),
        ))
    return hips
