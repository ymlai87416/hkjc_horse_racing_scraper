#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬虫使用示例
演示如何使用HKJCScraper提取比赛信息
"""

from hkjc_scraper import HKJCScraper
import json


def print_race_summary(result: dict):
    """打印比赛摘要信息"""
    print("\n" + "="*60)
    print("比赛信息摘要")
    print("="*60)
    
    print(f"\n【基本信息】")
    print(f"  比赛日期: {result.get('race_date', 'N/A')}")
    print(f"  场地: {result.get('racecourse', 'N/A')}")
    print(f"  场次: {result.get('race_no', 'N/A')}")
    
    race_info = result.get('race_info', {})
    if race_info:
        print(f"\n【比赛详情】")
        for key, value in race_info.items():
            if value:
                print(f"  {key}: {value}")
    
    horses = result.get('horses', [])
    if horses:
        print(f"\n【参赛马匹】共 {len(horses)} 匹")
        for i, horse in enumerate(horses[:5], 1):  # 只显示前5匹
            name = horse.get('horse_name', 'N/A')
            number = horse.get('number', 'N/A')
            jockey = horse.get('jockey', 'N/A')
            print(f"  {i}. {name} (编号: {number}, 骑师: {jockey})")
        if len(horses) > 5:
            print(f"  ... 还有 {len(horses) - 5} 匹马")
    
    incidents = result.get('incident_reports', [])
    if incidents:
        print(f"\n【事件报告】共 {len(incidents)} 条")
        for incident in incidents[:3]:  # 只显示前3条
            horse_name = incident.get('horse_name', 'N/A')
            desc = incident.get('description', 'N/A')
            print(f"  - {horse_name}: {desc[:50]}...")
    
    pedigree = result.get('pedigree', {})
    if pedigree:
        print(f"\n【胜出马匹血统】")
        print(f"  马名: {pedigree.get('horse_name', 'N/A')}")
        print(f"  父系: {pedigree.get('sire', 'N/A')}")
        print(f"  母系: {pedigree.get('dam', 'N/A')}")
    
    print("\n" + "="*60)


def main():
    """主函数"""
    # 创建爬虫实例
    scraper = HKJCScraper()
    
    # 示例URL
    url = "https://racing.hkjc.com/zh-hk/local/information/localresults?racedate=2026/01/18&Racecourse=ST&RaceNo=3"
    
    print(f"正在爬取: {url}")
    print("请稍候...")
    
    # 爬取数据
    result = scraper.scrape_race_result(url)
    
    if result:
        # 打印摘要
        print_race_summary(result)
        
        # 保存为JSON
        json_file = 'race_result.json'
        scraper.save_to_json(result, json_file)
        
        # 如果有马匹数据，也保存为CSV
        if result.get('horses'):
            csv_file = 'race_horses.csv'
            scraper.save_to_csv(result, csv_file)
            print(f"\n✓ 数据已保存:")
            print(f"  - JSON: {json_file}")
            print(f"  - CSV: {csv_file}")
        
        # 显示详细数据统计
        print(f"\n【数据统计】")
        print(f"  - 马匹信息: {len(result.get('horses', []))} 条")
        print(f"  - 事件报告: {len(result.get('incident_reports', []))} 条")
        print(f"  - 比赛结果: {len(result.get('race_result', {}).get('finishing_order', []))} 条")
        
    else:
        print("❌ 爬取失败，请检查URL和网络连接")


if __name__ == '__main__':
    main()

