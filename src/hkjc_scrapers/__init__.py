#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HKJC Scrapers Package
香港赛马会爬虫包

包含多个爬虫模块：
- race_result_scraper: 比赛结果爬虫
- race_schedule_scraper: 赛程表爬虫
- horse_info_scraper: 马匹信息爬虫
"""

from .race_result_scraper import RaceResultScraper
from .race_schedule_scraper import RaceScheduleScraper
from .horse_info_scraper import HorseInfoScraper

__all__ = [
    'RaceResultScraper',
    'RaceScheduleScraper',
    'HorseInfoScraper',
]

__version__ = '0.1.0'

