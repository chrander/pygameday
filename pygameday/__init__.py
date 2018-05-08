#!/usr/bin/env python
# -*- coding: utf-8 -*-
from . import util
from .pygameday import GameDayClient

__all__ = ["GameDayClient"]

# Set up logging
util.configure_logging("pygameday")

