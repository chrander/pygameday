#!/usr/bin/env python
# -*- coding: utf-8 -*-
LOG_FOLDER = 'logs'
LOG_LEVEL = 'INFO'
LOG_FORMAT_FILE = '%(asctime)s | %(filename)s | %(funcName)s (%(lineno)d) | %(levelname)s | %(message)s'
LOG_FORMAT_CONSOLE = '%(asctime)s | %(levelname)s | %(message)s'
LOG_FORMAT_TIME = '%Y-%m-%d %H:%M:%S'
LOG_FILE_MAX_BYTES = 5e6  # 5 MB
LOG_BACKUP_COUNT = 5
