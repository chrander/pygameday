#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Defines functionality for parsing MLB GameDay data from web content into database classes
"""
from __future__ import print_function, division, absolute_import

import logging

from dateutil import parser
from lxml import etree

from pygameday.models import AtBat
from pygameday.models import Game
from pygameday.models import HitInPlay
from pygameday.models import Pitch
from pygameday.models import Player

LOG = logging.getLogger("pygameday")


def parse_epg(epg_page):
    """Parse epg.xml to find all games in a given day

    Parameters
    ----------
    epg_page : requests page
        The result of a request for an epg.xml page

    Returns
    -------
    game_nodes : lxml list

    """
    root = etree.fromstring(epg_page.content)
    game_nodes = root.xpath('descendant::game')  # find all <game> nodes in the tree

    return game_nodes


def parse_game(game_node):
    """Parses a Game XML node into a Game database object

    Parameters
    ----------
    game_node : lxml node
        The Game node to parse

    Returns
    -------
    A Game object
    """
    db_game = None

    # Only parse games if they are final
    if game_node.get("status") in ["Final", "Completed Early"]:

        start_datetime = parser.parse(game_node.get("start"))

        db_game = Game(gameday_id=game_node.get("id"),
                       venue=game_node.get("venue"),
                       start_time=start_datetime,
                       game_data_directory=game_node.get("game_data_directory"),
                       game_type=game_node.get("game_type"),
                       home_name_abbrev=game_node.get("home_name_abbrev"),
                       home_team_city=game_node.get("home_team_city"),
                       home_team_name=game_node.get("home_team_name"),
                       away_name_abbrev=game_node.get("away_name_abbrev"),
                       away_team_city=game_node.get("away_team_city"),
                       away_team_name=game_node.get("away_team_name"),
                       home_team_runs=game_node.get("home_team_runs"),
                       away_team_runs=game_node.get("away_team_runs"),
                       league=game_node.get("league")
                       )
    else:
        msg = "GameDay ID {} was not parsed because its status is {}" \
                .format(game_node.get("id"), game_node.get("status"))
        LOG.info(msg)

    return db_game


def parse_players(players_page):
    """Parses a players.xml page

    Parameters
    ----------
    players_page : XML data
        The player page retrieved by the requests module

    Returns
    -------
    list
        A list of Player database objects
    """
    root = etree.fromstring(players_page.content)
    player_nodes = root.xpath('descendant::player')  # find all <player> nodes

    db_players_list = [parse_player_node(p) for p in player_nodes]
    return db_players_list


def parse_player_node(player_node):
    """Parses a player XML node

    Parameters
    ----------
    player_node : lxml node
        The player node to parse

    Returns
    -------
    A Player database object
    """
    db_player = Player(player_id=player_node.get("id"),
                       first=player_node.get("first"),
                       last=player_node.get("last"),
                       boxname=player_node.get("boxname"),
                       rl=player_node.get("rl"),
                       bats=player_node.get("bats"),
                       )
    return db_player


def parse_hit_chart(hit_chart_page):
    """Parses inning_hit.xml

    Parameters
    ----------
    hit_chart_page
        The dadta from inning_hit.xml
    """
    root = etree.fromstring(hit_chart_page.content)
    hip_nodes = root.xpath('descendant::hip')  # find all <hip> nodes

    db_hips_list = [parse_hit_in_play_node(h) for h in hip_nodes]
    return db_hips_list


def parse_hit_in_play_node(hip_node):
    """Parses a Hit In Play node

    Parameters
    ----------
    hip_node : lxml node
        The hit in play node to parse

    Returns
    -------
    A HitInPlay object
    """
    hip = HitInPlay(batter_id=hip_node.get("batter"),
                    pitcher_id=hip_node.get("pitcher"),
                    des=hip_node.get("des"),
                    hip_type=hip_node.get("type"),
                    team=hip_node.get("team"),
                    inning=hip_node.get("inning"),
                    x=hip_node.get("x"),
                    y=hip_node.get("y")
                    )
    return hip


def parse_inning_all(inning_all_page):
    """Parses inning_all.xml for atbats and pitches

    Parameters
    ----------
    inning_all_page
        The data from inning_all.xml
    """
    root = etree.fromstring(inning_all_page.content)
    inning_nodes = root.xpath('descendant::inning')  # Find all <atbat> nodes

    db_at_bat_list = []
    ab_nodes_top = []
    ab_nodes_bot = []

    for inn in inning_nodes:
        inning_num = inn.get("num")  # the inning number

        inning_top = inn.xpath('top')  # the top of the inning, as a list
        inning_bot = inn.xpath('bottom')  # the bottom of the inning, as a list

        if inning_top:  # if the top of the inning exists (is not empty)
            ab_nodes_top = inning_top[0].xpath('descendant::atbat')

        if inning_bot:  # if the bottom of the inning exists (is not empty)
            ab_nodes_bot = inning_bot[0].xpath('descendant::atbat')

        for ab in ab_nodes_top:
            db_at_bat = parse_at_bat(ab, inning_num, 'T')
            db_at_bat_list.append(db_at_bat)

        for ab in ab_nodes_bot:
            db_at_bat = parse_at_bat(ab, inning_num, 'B')
            db_at_bat_list.append(db_at_bat)

    return db_at_bat_list


def parse_at_bat(at_bat, inning_num, inning_half):
    """Parses an at bat XML node

    Parameters
    ----------
    at_bat : lxml node
        The at bat node to parse
    inning_num : int
        The inning number (e.g., 1 for first inning)
    inning_half : str
        'T' if top of the inning, 'B' if bottom of the inning

    Returns
    -------
    An AtBat database object
    """
    pitches = at_bat.xpath('descendant::pitch')  # find all <pitch> nodes

    db_at_bat = AtBat(
            inning=inning_num,
            inning_half=inning_half,
            n_pitches=len(pitches),
            n_balls=at_bat.get("b"),
            n_strikes=at_bat.get("s"),
            n_outs=at_bat.get("o"),
            batter_id=at_bat.get("batter"),
            pitcher_id=at_bat.get("pitcher"),
            batter_stance=at_bat.get("stand"),
            des=at_bat.get("des"),
            event=at_bat.get("event")
            )

    for index, pitch in enumerate(pitches):
        db_pitch = parse_pitch(pitch, inning_num, inning_half, index)
        db_at_bat.pitches.append(db_pitch)

    return db_at_bat


def parse_pitch(pitch, inning_num, inning_half, index):
    """Parses a pitch XML node

    Parameters
    ----------
    pitch : lxml node
        The pitch node to parse
    inning_num : int
        The inning number (e.g., 1 for first inning)
    inning_half : str
        'T' if top of the inning, 'B' if bottom of the inning
    index : int
        Index of the pitch within the ab-bat it occurred in

    Returns
    -------
    A Pitch database object
    """
    db_pitch = Pitch(
            at_bat_pitch_num=index,
            inning=inning_num,
            inning_half=inning_half,
            des=pitch.get("des"),
            result_type=pitch.get("type"),
            gameday_sv_id=pitch.get("sv_id"),
            x=pitch.get("x"),
            y=pitch.get("y"),
            start_speed=pitch.get("start_speed"),
            end_speed=pitch.get("end_speed"),
            sz_top=pitch.get("sz_top"),
            sz_bot=pitch.get("sz_bot"),
            pfx_x=pitch.get("pfx_x"),
            pfx_z=pitch.get("pfx_z"),
            px=pitch.get("px"),
            pz=pitch.get("pz"),
            x0=pitch.get("x0"),
            y0=pitch.get("y0"),
            z0=pitch.get("z0"),
            vx0=pitch.get("vx0"),
            vy0=pitch.get("vy0"),
            vz0=pitch.get("vz0"),
            ax=pitch.get("ax"),
            ay=pitch.get("ay"),
            az=pitch.get("az"),
            break_y=pitch.get("break_y"),
            break_angle=pitch.get("break_angle"),
            break_length=pitch.get("break_length"),
            pitch_type=pitch.get("pitch_type"),
            type_conf=pitch.get("type_conf"),
            zone=pitch.get("zone"),
            nasty=pitch.get("nasty"),
            spin_dir=pitch.get("spin_dir"),
            spin_rate=pitch.get("spin_rate")
            )
    return db_pitch


def save_page(page, filename):
    """Writes the text of an html page to disk

    Parameters
    ----------
    page : requests page object
        The page to write
    filename
        The name of the file to create
    """
    with open(filename, 'w') as f:
        f.write(page.text)


def test():
    game_directory = '/components/game/mlb/year_2014/month_04/day_04/gid_2014_04_04_anamlb_houmlb_1'

#    print "Fetching epg page"
#    epg_page = gds.fetch_epg(year, month, day)
#    print "Parsing epg page"
#    parser.parse_epg(epg_page)
#
#    print "Fetching players page"
#    players_page = gds.fetch_players(game_directory)
#    print "Parsing players page"
#    parser.parse_players(players_page)
#
#    print "Fetching hit chart page"
#    hit_chart_page = gds.fetch_hit_chart(game_directory)
#    print "Parsing hit chart page"
#    parser.parse_hit_chart(hit_chart_page)
    from pygameday import scrape

    print("Fetching innings_all page")
    inning_all_page = scrape.fetch_inning_all(game_directory)
    print("Parsing innings_all page")
    at_bats = parse_inning_all(inning_all_page)
    print(at_bats)


if __name__ == "__main__":
    test()
