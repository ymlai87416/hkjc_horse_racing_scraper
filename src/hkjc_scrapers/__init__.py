#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HKJC Scrapers Package
香港赛马会爬虫包

包含多个爬虫模块：
- race_result_scraper: 比赛结果爬虫
- race_calendar_scraper: 赛程表爬虫（待实现）
- horse_info_scraper: 马匹信息爬虫（待实现）
"""

from .race_result_scraper import RaceResultScraper

# 未来可以添加更多 scraper：
# from .race_calendar_scraper import RaceCalendarScraper
# from .horse_info_scraper import HorseInfoScraper

__all__ = [
    'RaceResultScraper',
    # 'RaceCalendarScraper',  # 待实现
    # 'HorseInfoScraper',     # 待实现
]

__version__ = '0.1.0'

