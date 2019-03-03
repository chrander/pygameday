#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Provides functionality for scraping MLB GameDay data from the GameDay website
"""
import requests
import logging
from datetime import datetime

from .constants import GD_SERVER
from .constants import GD_BASE_PATH

logger = logging.getLogger(__name__)


def get_url(url):
    """Fetches a URL, returning the page content

    Parameters
    ----------
    url : str
        The URL to get

    Returns
    -------
    requests response
        The requests page corresonding to the URL
    """
    logger.debug('Fetching URL: {}'.format(url))
    page = requests.get(url)

    if not page.ok:
        logger.error('Error fetching {}'.format(url))
        return None

    return page


def fetch_master_scoreboard(date):
    """Fetch the master scoreboard page containing of games on a given day

    Parameters
    ----------
    date : datetime.datetime
        The day to fetch

    Returns
    -------
    dict
        Dictionary of games data on the given day
    """
    url = "http://{}{}/year_{:d}/month_{:02d}/day_{:02d}/master_scoreboard.json".format(
        GD_SERVER, GD_BASE_PATH, date.year, date.month, date.day)
    response = requests.get(url)
    if response.ok:
        return response.json()
    else:
        logger.error('Error fetching URL {}'.format(url))
        return None


def fetch_epg(date):
    """Fetch epg.xml (possibly stands for "event page"?) for a given day

    Parameters
    ----------
    date : datetime.datetime
        The day to fetch

    Returns
    -------
    page : text
        XML-formatted data containing metadata on baseball games that took
        place on the given day.

    """
    url = "http://{}{}/year_{:d}/month_{:02d}/day_{:02d}/epg.xml".format(
        GD_SERVER, GD_BASE_PATH, date.year, date.month, date.day)
    return get_url(url)


def fetch_inning_all(game_directory):
    """Fetch the inning_all.xml file for a given game

    The inning_all.xml file for a game contains the full set of game events.

    Parameters
    ----------
    game_directory : str
        The relative path to the game directory

    Returns
    -------
    page : text
        XML-formatted data containing game event data.

    """
    url = 'http://' + GD_SERVER + game_directory + '/inning/inning_all.xml'
    return get_url(url)


def fetch_hit_chart(game_directory):
    """Fetch inning_hit.xml for a given game

    The inning_hit.xml file contains ball-in-play data.

    Parameters
    ----------
    game_directory : str
        The relative path to the game directory

    Returns
    -------
    page : text
        XML-formatted data containing ball-in-play data.

    """
    url = 'http://' + GD_SERVER + game_directory + '/inning/inning_hit.xml'
    return get_url(url)


def fetch_players(game_directory):
    """Fetch players.xml for a given game

    The players.xml file contains player data for the game.

    Parameters
    ----------
    game_directory : str
        The relative path to the game directory

    Returns
    -------
    page : text
        XML-formatted data containing player data.

    """
    url = 'http://' + GD_SERVER + game_directory + '/players.xml'
    return get_url(url)


def save_page(page, file_path):
    """Save page content to disk

    Parameters
    ----------
    page : requests get result

    file_path : str
        The path to the file that will store the page contents

    """
    with open(file_path, 'w') as f:
        f.write(page.text)


def test():
    year = 2014
    month = 4
    day = 4

    print("Fetching epg page")
    epg_page = fetch_epg(datetime(year, month, day))
    save_page(epg_page, 'epg.xml')

    game_directory = '/components/game/mlb/year_2014/month_04/day_04/gid_2014_04_04_anamlb_houmlb_1'

    print("Fetching player page")
    players_page = fetch_players(game_directory)
    save_page(players_page, 'players.xml')

    print("Fetching hit chart page")
    hit_chart_page = fetch_hit_chart(game_directory)
    save_page(hit_chart_page, 'inning_hit.xml')

    print("Fetching inning event page")
    inning_event_page = fetch_inning_all(game_directory)
    save_page(inning_event_page, 'inning_all.xml')

#    parser = etree.XMLParser(recover=True, encoding='UTF-8')
#    root = etree.parse(url)
#    root = etree.fromstring(page.content)
#
#    pretty_string = etree.tostring(root, pretty_print=False)
#    f = open('sample_epg.xml', 'w')
#    f.write(pretty_string)
#    f.close()


if __name__ == "__main__":
    test()
