#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
赛程表爬虫使用示例
演示如何使用RaceScheduleScraper提取赛程表信息
"""

import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from hkjc_scrapers import RaceScheduleScraper
import json


def print_schedule_summary(result: dict):
    """打印赛程表摘要信息"""
    print("\n" + "="*60)
    print("赛程表信息摘要")
    print("="*60)
    
    print(f"\n【基本信息】")
    print(f"  来源URL: {result.get('source_url', 'N/A')}")
    print(f"  爬取时间: {result.get('scraped_at', 'N/A')}")
    
    months = result.get('months', [])
    if months:
        print(f"\n【月份列表】")
        print(f"  共 {len(months)} 个月份: {', '.join(months)}")
    
    race_days = result.get('race_days', [])
    if race_days:
        print(f"\n【赛马日统计】")
        print(f"  总赛马日数: {len(race_days)}")
        
        # 按场地统计
        venues_count = {}
        for day in race_days:
            for venue in day.get('venues', []):
                venues_count[venue] = venues_count.get(venue, 0) + 1
        
        if venues_count:
            print(f"  场地分布:")
            for venue, count in venues_count.items():
                print(f"    - {venue}: {count} 天")
        
        # 按赛马类型统计
        race_types_count = {}
        for day in race_days:
            for race_type in day.get('race_types', []):
                race_types_count[race_type] = race_types_count.get(race_type, 0) + 1
        
        if race_types_count:
            print(f"  赛马类型分布:")
            for race_type, count in race_types_count.items():
                print(f"    - {race_type}: {count} 天")
        
        # 显示前10个赛马日
        print(f"\n【前10个赛马日】")
        for i, day in enumerate(race_days[:10], 1):
            date_str = day.get('date', f"{day.get('year', '')}-{day.get('month', '')}-{day.get('day', '')}")
            venues = ', '.join(day.get('venues', []))
            race_types = ', '.join(day.get('race_types', []))
            print(f"  {i}. {date_str} - {venues} ({race_types})")
            if day.get('race_classes'):
                print(f"     赛事级别: {', '.join(day.get('race_classes', []))}")
            if day.get('special_marks'):
                print(f"     特殊标记: {', '.join(day.get('special_marks', []))}")
    
    notices = result.get('notices', [])
    if notices:
        print(f"\n【重要通知】")
        for notice in notices:
            print(f"  - {notice}")
    
    legend = result.get('legend', {})
    if legend:
        print(f"\n【图例说明】")
        if legend.get('venues'):
            print(f"  场地: {list(legend['venues'].keys())}")
        if legend.get('race_types'):
            print(f"  赛马类型: {list(legend['race_types'].keys())}")
        if legend.get('track_types'):
            print(f"  赛道类型: {list(legend['track_types'].keys())}")
        if legend.get('race_classes'):
            print(f"  赛事级别: {list(legend['race_classes'].keys())}")
        if legend.get('special_marks'):
            print(f"  特殊标记: {legend['special_marks']}")
    
    print("\n" + "="*60)


def main():
    """主函数"""
    # 创建爬虫实例
    scraper = RaceScheduleScraper()
    
    # 默认URL
    url = "https://racing.hkjc.com/zh-hk/local/information/fixture?b_cid=SPLDSPA_hkjc-home_MegaMenu"
    
    print(f"正在爬取赛程表: {url}")
    print("请稍候...")
    
    # 爬取数据
    result = scraper.scrape_schedule(url)
    
    if result:
        # 打印摘要
        print_schedule_summary(result)
        
        # 保存为JSON
        json_file = 'race_schedule.json'
        scraper.save_to_json(result, json_file)
        
        # 保存为CSV
        csv_file = 'race_schedule.csv'
        scraper.save_to_csv(result, csv_file)
        
        print(f"\n✓ 数据已保存:")
        print(f"  - JSON: {json_file}")
        print(f"  - CSV: {csv_file}")
        
        # 演示筛选功能
        print(f"\n【筛选示例】")
        
        # 按月份筛选
        january_days = scraper.get_race_days_by_month(result, '一月')
        if january_days:
            print(f"  一月份的赛马日: {len(january_days)} 天")
        
        # 按场地筛选
        st_days = scraper.get_race_days_by_venue(result, '沙田')
        if st_days:
            print(f"  沙田的赛马日: {len(st_days)} 天")
        
        hv_days = scraper.get_race_days_by_venue(result, '跑马地')
        if hv_days:
            print(f"  跑马地的赛马日: {len(hv_days)} 天")
        
    else:
        print("❌ 爬取失败，请检查URL和网络连接")


if __name__ == '__main__':
    main()

