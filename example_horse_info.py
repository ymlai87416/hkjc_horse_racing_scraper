#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
马匹信息爬虫使用示例
演示如何使用HorseInfoScraper提取马匹信息
"""

import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from hkjc_scrapers import HorseInfoScraper
import json


def print_horse_summary(result: dict):
    """打印马匹信息摘要"""
    print("\n" + "="*60)
    print("马匹信息摘要")
    print("="*60)
    
    print(f"\n【基本信息】")
    print(f"  马匹ID: {result.get('horse_id', 'N/A')}")
    
    basic_info = result.get('basic_info', {})
    if basic_info:
        print(f"  马匹名称: {basic_info.get('horse_name', 'N/A')}")
        print(f"  马匹编号: {basic_info.get('horse_code', 'N/A')}")
        print(f"  性别: {basic_info.get('sex', 'N/A')}")
        print(f"  年龄: {basic_info.get('age', 'N/A')}")
        print(f"  毛色: {basic_info.get('colour', 'N/A')}")
        print(f"  练马师: {basic_info.get('trainer', 'N/A')}")
        print(f"  马主: {basic_info.get('owner', 'N/A')}")
        print(f"  父系: {basic_info.get('sire', 'N/A')}")
        print(f"  母系: {basic_info.get('dam', 'N/A')}")
        print(f"  外祖父: {basic_info.get('maternal_grandsire', 'N/A')}")
    
    race_records = result.get('race_records', [])
    if race_records:
        print(f"\n【赛绩记录】共 {len(race_records)} 场")
        print(f"{'日期':<12} {'场地':<8} {'距离':<8} {'班次':<8} {'名次':<8} {'骑师':<12} {'练马师':<12}")
        print("-" * 80)
        for record in race_records[:10]:  # 只显示前10场
            date = record.get('date', 'N/A')
            venue = record.get('venue', 'N/A')
            distance = record.get('distance', 'N/A')
            race_class = record.get('class', 'N/A')
            position = record.get('position', 'N/A')
            jockey = record.get('jockey', 'N/A')
            trainer = record.get('trainer', 'N/A')
            print(f"{date:<12} {venue:<8} {distance:<8} {race_class:<8} {position:<8} {jockey:<12} {trainer:<12}")
        if len(race_records) > 10:
            print(f"  ... 还有 {len(race_records) - 10} 场赛绩")
    
    equipment_legend = result.get('equipment_legend', {})
    if equipment_legend:
        print(f"\n【装备图例】共 {len(equipment_legend)} 项")
        for code, description in list(equipment_legend.items())[:5]:  # 只显示前5项
            print(f"  {code}: {description}")
        if len(equipment_legend) > 5:
            print(f"  ... 还有 {len(equipment_legend) - 5} 项")
    
    print("\n" + "="*60)


def main():
    """主函数"""
    # 创建爬虫实例
    scraper = HorseInfoScraper()
    
    # 示例URL
    url = "https://racing.hkjc.com/zh-hk/local/information/horse?horseid=HK_2020_E436&Option=1"
    
    print(f"正在爬取: {url}")
    print("请稍候...")
    
    # 爬取数据
    result = scraper.scrape_horse_info(url)
    
    if result:
        # 打印摘要
        print_horse_summary(result)
        
        # 保存为JSON
        json_file = 'horse_info.json'
        scraper.save_to_json(result, json_file)
        
        # 如果有赛绩记录，也保存为CSV
        if result.get('race_records'):
            csv_file = 'horse_race_records.csv'
            scraper.save_to_csv(result, csv_file)
            print(f"\n✓ 数据已保存:")
            print(f"  - JSON: {json_file}")
            print(f"  - CSV: {csv_file}")
        
        # 显示详细数据统计
        print(f"\n【数据统计】")
        print(f"  - 基本信息字段: {len(result.get('basic_info', {}))} 个")
        print(f"  - 赛绩记录: {len(result.get('race_records', []))} 条")
        print(f"  - 装备图例: {len(result.get('equipment_legend', {}))} 项")
        
    else:
        print("❌ 爬取失败，请检查URL和网络连接")


if __name__ == '__main__':
    main()

