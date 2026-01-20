#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HKJC赛程表爬虫测试
测试赛程表爬虫的核心功能
"""

import pytest
import sys
import os
import re
from unittest.mock import Mock, patch, MagicMock
from bs4 import BeautifulSoup

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from hkjc_scrapers.race_schedule_scraper import RaceScheduleScraper


class TestRaceScheduleScraper:
    """HKJC赛程表爬虫测试类"""
    
    @pytest.fixture
    def scraper(self):
        """创建爬虫实例"""
        return RaceScheduleScraper()
    
    @pytest.fixture
    def sample_html(self):
        """示例HTML内容（赛程表页面）"""
        return """
        <html>
        <head><title>赛程表</title></head>
        <body>
            <table>
                <tr>
                    <th>日</th>
                    <th>一</th>
                    <th>二</th>
                    <th>三</th>
                    <th>四</th>
                    <th>五</th>
                    <th>六</th>
                </tr>
                <tr>
                    <td colspan="7">二0二六年一月</td>
                </tr>
                <tr>
                    <td>1</td>
                    <td>2</td>
                    <td>
                        3
                        <img src="/general/-/media/Sites/JCRW/Remarks/Fixture/st-ch" alt="沙田">
                        <img src="/general/-/media/Sites/JCRW/Remarks/Fixture/day" alt="日賽">
                        <img src="/general/-/media/Sites/JCRW/Remarks/Fixture/turf" alt="草地">
                    </td>
                    <td>4</td>
                    <td>5</td>
                    <td>6</td>
                    <td>7</td>
                </tr>
                <tr>
                    <td>8</td>
                    <td>9</td>
                    <td>10</td>
                    <td>
                        11
                        <img src="/general/-/media/Sites/JCRW/Remarks/Fixture/hv-ch" alt="跑馬地">
                        <img src="/general/-/media/Sites/JCRW/Remarks/Fixture/night" alt="夜賽">
                        <img src="/general/-/media/Sites/JCRW/Remarks/Fixture/class_g1" alt="一級賽">
                        C
                    </td>
                    <td>12</td>
                    <td>13</td>
                    <td>14</td>
                </tr>
            </table>
            <div>
                <p>原定於2025年9月24日（星期三）在跑馬地馬場舉行的賽事將予取消。</p>
            </div>
        </body>
        </html>
        """
    
    def test_scraper_initialization(self, scraper):
        """测试爬虫初始化"""
        assert scraper is not None
        assert scraper.session is not None
        assert 'User-Agent' in scraper.session.headers
    
    def test_url_parsing(self, scraper):
        """测试URL解析功能"""
        url = "https://racing.hkjc.com/zh-hk/local/information/fixture?b_cid=SPLDSPA_hkjc-home_MegaMenu"
        
        with patch('hkjc_scrapers.race_schedule_scraper.requests.Session.get') as mock_get:
            mock_response = Mock()
            mock_response.text = "<html><body>Test</body></html>"
            mock_response.encoding = 'utf-8'
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response
            
            result = scraper.scrape_schedule(url)
            
            assert result is not None
            assert result.get('source_url') == url
            assert 'scraped_at' in result
    
    def test_extract_months(self, scraper, sample_html):
        """测试月份提取"""
        soup = BeautifulSoup(sample_html, 'html.parser')
        months = scraper._extract_months(soup)
        
        assert isinstance(months, list)
    
    def test_extract_legend(self, scraper, sample_html):
        """测试图例提取"""
        soup = BeautifulSoup(sample_html, 'html.parser')
        legend = scraper._extract_legend(soup)
        
        assert isinstance(legend, dict)
        assert 'venues' in legend
        assert 'race_types' in legend
        assert 'track_types' in legend
        assert 'race_classes' in legend
        assert 'special_marks' in legend
    
    def test_extract_notices(self, scraper, sample_html):
        """测试通知提取"""
        soup = BeautifulSoup(sample_html, 'html.parser')
        notices = scraper._extract_notices(soup)
        
        assert isinstance(notices, list)
        # 示例HTML中包含取消通知
        assert len(notices) > 0
    
    def test_extract_race_days(self, scraper, sample_html):
        """测试赛马日提取"""
        soup = BeautifulSoup(sample_html, 'html.parser')
        race_days = scraper._extract_race_days(soup)
        
        assert isinstance(race_days, list)
        # 示例HTML中应该至少有两个赛马日（3号和11号）
        assert len(race_days) >= 2
    
    def test_parse_race_day_cell(self, scraper, sample_html):
        """测试日期单元格解析"""
        soup = BeautifulSoup(sample_html, 'html.parser')
        
        # 找到包含赛马信息的单元格
        cell = soup.find('td', string=re.compile(r'3'))
        if cell:
            # 找到包含图片的父单元格
            for td in soup.find_all('td'):
                if td.find('img'):
                    race_day = scraper._parse_race_day_cell(td, 3, '一月', '2026')
                    if race_day:
                        assert race_day['day'] == 3
                        assert 'venues' in race_day
                        assert 'race_types' in race_day
                        break
    
    def test_convert_chinese_month(self, scraper):
        """测试中文月份转换"""
        assert scraper._convert_chinese_month('一月') == 1
        assert scraper._convert_chinese_month('十二月') == 12
        assert scraper._convert_chinese_month('九月') == 9
        assert scraper._convert_chinese_month('无效') is None
    
    def test_convert_chinese_year(self, scraper):
        """测试中文年份转换"""
        assert scraper._convert_chinese_year('二0二六年') == '2026'
        assert scraper._convert_chinese_year('2026年') == '2026'
        assert scraper._convert_chinese_year('二零二六年') == '2026'
    
    def test_get_race_days_by_month(self, scraper):
        """测试按月份筛选赛马日"""
        schedule_data = {
            'race_days': [
                {'day': 3, 'month': '一月', 'year': '2026'},
                {'day': 11, 'month': '一月', 'year': '2026'},
                {'day': 5, 'month': '二月', 'year': '2026'}
            ]
        }
        
        january_days = scraper.get_race_days_by_month(schedule_data, '一月')
        assert len(january_days) == 2
        assert all(day['month'] == '一月' for day in january_days)
    
    def test_get_race_days_by_venue(self, scraper):
        """测试按场地筛选赛马日"""
        schedule_data = {
            'race_days': [
                {'day': 3, 'venues': ['沙田']},
                {'day': 11, 'venues': ['跑马地']},
                {'day': 15, 'venues': ['沙田']}
            ]
        }
        
        st_days = scraper.get_race_days_by_venue(schedule_data, '沙田')
        assert len(st_days) == 2
        assert all('沙田' in day['venues'] for day in st_days)
    
    def test_save_to_json(self, scraper, tmp_path):
        """测试JSON保存功能"""
        test_data = {
            'source_url': 'test_url',
            'scraped_at': '2026-01-01T00:00:00',
            'race_days': [
                {'day': 3, 'month': '一月', 'year': '2026', 'venues': ['沙田']}
            ]
        }
        
        json_file = tmp_path / 'test_schedule.json'
        scraper.save_to_json(test_data, str(json_file))
        
        assert json_file.exists()
        
        # 验证JSON内容
        import json
        with open(json_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
            assert loaded_data['source_url'] == 'test_url'
            assert len(loaded_data['race_days']) == 1
    
    def test_save_to_csv(self, scraper, tmp_path):
        """测试CSV保存功能"""
        test_data = {
            'race_days': [
                {
                    'date': '2026-01-03',
                    'day': 3,
                    'month': '一月',
                    'year': '2026',
                    'venues': ['沙田'],
                    'race_types': ['日赛'],
                    'track_types': ['草地'],
                    'race_classes': [],
                    'special_marks': [],
                    'prize_money': [],
                    'notes': []
                },
                {
                    'date': '2026-01-11',
                    'day': 11,
                    'month': '一月',
                    'year': '2026',
                    'venues': ['跑马地'],
                    'race_types': ['夜赛'],
                    'track_types': ['草地'],
                    'race_classes': ['一级赛'],
                    'special_marks': ['C'],
                    'prize_money': [],
                    'notes': []
                }
            ]
        }
        
        csv_file = tmp_path / 'test_schedule.csv'
        scraper.save_to_csv(test_data, str(csv_file))
        
        assert csv_file.exists()
        
        # 验证CSV内容
        import csv
        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 2
            assert rows[0]['day'] == '3'
            assert rows[1]['venues'] == '跑马地'
    
    def test_save_to_csv_empty_data(self, scraper, tmp_path):
        """测试CSV保存空数据"""
        test_data = {'race_days': []}
        
        csv_file = tmp_path / 'test_empty.csv'
        scraper.save_to_csv(test_data, str(csv_file))
        
        # 空数据不应该创建文件或应该创建空文件
        # 根据实现，这里可能不创建文件
    
    def test_error_handling_invalid_url(self, scraper):
        """测试无效URL的错误处理"""
        with patch('hkjc_scrapers.race_schedule_scraper.requests.Session.get') as mock_get:
            mock_get.side_effect = Exception("Connection error")
            
            result = scraper.scrape_schedule("invalid_url")
            
            # 应该返回空字典而不是抛出异常
            assert isinstance(result, dict)
    
    def test_result_structure(self, scraper):
        """测试返回结果的结构"""
        url = "https://racing.hkjc.com/zh-hk/local/information/fixture?b_cid=SPLDSPA_hkjc-home_MegaMenu"
        
        with patch('hkjc_scrapers.race_schedule_scraper.requests.Session.get') as mock_get:
            mock_response = Mock()
            mock_response.text = "<html><body><table><tr><td>Test</td></tr></table></body></html>"
            mock_response.encoding = 'utf-8'
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response
            
            result = scraper.scrape_schedule(url)
            
            # 验证必需字段存在
            required_fields = ['source_url', 'scraped_at', 'months', 'race_days', 
                             'legend', 'notices']
            for field in required_fields:
                assert field in result, f"缺少必需字段: {field}"
            
            # 验证字段类型
            assert isinstance(result['months'], list)
            assert isinstance(result['race_days'], list)
            assert isinstance(result['legend'], dict)
            assert isinstance(result['notices'], list)
    
    def test_default_url(self, scraper):
        """测试使用默认URL"""
        with patch('hkjc_scrapers.race_schedule_scraper.requests.Session.get') as mock_get:
            mock_response = Mock()
            mock_response.text = "<html><body>Test</body></html>"
            mock_response.encoding = 'utf-8'
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response
            
            result = scraper.scrape_schedule()
            
            assert result is not None
            assert 'source_url' in result
            # 验证使用了默认URL
            assert 'fixture' in result['source_url']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

