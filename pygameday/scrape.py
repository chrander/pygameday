#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Fetches MLB Statcast data via pybaseball."""
import logging
import pybaseball

logger = logging.getLogger(__name__)

pybaseball.cache.enable()


def fetch_statcast_data(start_date, end_date):
    """Fetch Statcast pitch-by-pitch data for a date range.

    Parameters
    ----------
    start_date : datetime.datetime
    end_date : datetime.datetime

    Returns
    -------
    pandas.DataFrame or None
        One row per pitch. Returns None if no data is available or on error.
    """
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')
    logger.debug('Fetching Statcast data from %s to %s', start_str, end_str)

    try:
        df = pybaseball.statcast(start_dt=start_str, end_dt=end_str, verbose=False)
    except Exception:
        logger.exception('Error fetching Statcast data for %s to %s', start_str, end_str)
        return None

    if df is None or df.empty:
        logger.warning('No Statcast data returned for %s to %s', start_str, end_str)
        return None

    return df
