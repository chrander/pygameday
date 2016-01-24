#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Provides functionality for scraping MLB GameDay data from the GameDay website
"""
from __future__ import print_function, division, absolute_import
import requests
import logging

from pygameday.constants import GD_SERVER
from pygameday.constants import GD_BASE_PATH

logger = logging.getLogger("pygameday")


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

    if page.status_code != 200:
        logger.error('Error fetching {}'.format(url))
        return None

    return page


def fetch_epg(year, month, day):
    """Fetch epg.xml (possibly stands for "event page"?) for a given day

    Parameters
    ----------
    year : int
        The year that the events took place
    month : int
        The month that the events took place
    day : int
        The day that the events took place

    Returns
    -------
    page : text
        XML-formatted data containing metadata on baseball games that took
        place on the given day.

    """
    url = "{}{}/year_{:d}/month_{:02d}/day_{:02d}/epg.xml".format(GD_SERVER, GD_BASE_PATH, year, month, day)
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
    url = GD_SERVER + game_directory + '/inning/inning_all.xml'
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
    url = GD_SERVER + game_directory + '/inning/inning_hit.xml'
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
    url = GD_SERVER + game_directory + '/players.xml'
    return get_url(url)


def save_page(page, filename):
    """Save page content to disk

    Parameters
    ----------
    page : requests get result

    filename : str
        The path to the file that will store the page contents

    """
    with open(filename, 'w') as f:
        f.write(page.text)
        f.close()


def test():
    year = 2014
    month = 4
    day = 4

    print("Fetching epg page")
    epg_page = fetch_epg(year, month, day)
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
