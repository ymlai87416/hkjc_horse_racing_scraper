#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HKJC马匹信息爬虫测试
测试马匹信息爬虫的核心功能
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch
from bs4 import BeautifulSoup

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from hkjc_scrapers.horse_info_scraper import HorseInfoScraper


class TestHorseInfoScraper:
    """HKJC马匹信息爬虫测试类"""
    
    @pytest.fixture
    def scraper(self):
        """创建爬虫实例"""
        return HorseInfoScraper()
    
    @pytest.fixture
    def sample_html(self):
        """示例HTML内容"""
        return """
        <html>
        <head><title>马匹信息</title></head>
        <body>
            <h1>遨遊氣泡 (E436)</h1>
            <table>
                <tr>
                    <th>馬名</th>
                    <th>編號</th>
                    <th>性別</th>
                    <th>年齡</th>
                    <th>毛色</th>
                </tr>
                <tr>
                    <td>遨遊氣泡</td>
                    <td>E436</td>
                    <td>閹</td>
                    <td>7</td>
                    <td>棗</td>
                </tr>
            </table>
            <table>
                <tr>
                    <th>父系</th>
                    <th>母系</th>
                    <th>外祖父</th>
                </tr>
                <tr>
                    <td>Starspangledbanner</td>
                    <td>Red Pixie</td>
                    <td>Red Ransom</td>
                </tr>
            </table>
            <table>
                <tr>
                    <th>日期</th>
                    <th>場地</th>
                    <th>距離</th>
                    <th>班次</th>
                    <th>名次</th>
                    <th>騎師</th>
                    <th>練馬師</th>
                </tr>
                <tr>
                    <td>02/06/24</td>
                    <td>東京/草地</td>
                    <td>1600</td>
                    <td>G1</td>
                    <td>15</td>
                    <td><a href="/jockey?jockeyid=PZ">潘頓</a></td>
                    <td><a href="/trainer?trainerid=YPF">姚本輝</a></td>
                </tr>
                <tr>
                    <td>30/03/24</td>
                    <td>美丹/草地</td>
                    <td>1800</td>
                    <td>G1</td>
                    <td>10-1/2</td>
                    <td><a href="/jockey?jockeyid=BAM">巴米高</a></td>
                    <td><a href="/trainer?trainerid=YPF">姚本輝</a></td>
                </tr>
            </table>
            <table>
                <tr>
                    <td>B :  戴眼罩</td>
                    <td>BO :  只戴單邊眼罩</td>
                    <td>CP :  羊毛面箍</td>
                </tr>
            </table>
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
        url = "https://racing.hkjc.com/zh-hk/local/information/horse?horseid=HK_2020_E436&Option=1"
        
        with patch('hkjc_scrapers.horse_info_scraper.requests.Session.get') as mock_get:
            mock_response = Mock()
            mock_response.text = "<html><body>Test</body></html>"
            mock_response.encoding = 'utf-8'
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response
            
            result = scraper.scrape_horse_info(url)
            
            assert result is not None
            assert result.get('horse_id') == 'HK_2020_E436'
    
    def test_extract_basic_info(self, scraper, sample_html):
        """测试基本信息提取"""
        soup = BeautifulSoup(sample_html, 'html.parser')
        basic_info = scraper._extract_basic_info(soup)
        
        assert isinstance(basic_info, dict)
        assert basic_info.get('horse_name') == '遨遊氣泡'
        assert basic_info.get('horse_code') == 'E436'
        assert basic_info.get('sex') == '閹'
        assert basic_info.get('age') == '7'
        assert basic_info.get('colour') == '棗'
        assert basic_info.get('sire') == 'Starspangledbanner'
        assert basic_info.get('dam') == 'Red Pixie'
        assert basic_info.get('maternal_grandsire') == 'Red Ransom'
    
    def test_extract_race_records(self, scraper, sample_html):
        """测试赛绩记录提取"""
        soup = BeautifulSoup(sample_html, 'html.parser')
        race_records = scraper._extract_race_records(soup)
        
        assert isinstance(race_records, list)
        assert len(race_records) == 2
        
        if len(race_records) > 0:
            first_record = race_records[0]
            assert 'date' in first_record
            assert 'venue' in first_record
            assert 'distance' in first_record
            assert first_record.get('date') == '02/06/24'
            assert first_record.get('venue') == '東京/草地'
            assert first_record.get('distance') == '1600'
            assert first_record.get('class') == 'G1'
            assert first_record.get('position') == '15'
            assert first_record.get('jockey') == '潘頓'
            assert first_record.get('trainer') == '姚本輝'
            assert first_record.get('jockey_id') == 'PZ'
            assert first_record.get('trainer_id') == 'YPF'
    
    def test_extract_equipment_legend(self, scraper, sample_html):
        """测试装备图例提取"""
        soup = BeautifulSoup(sample_html, 'html.parser')
        equipment_legend = scraper._extract_equipment_legend(soup)
        
        assert isinstance(equipment_legend, dict)
        assert 'B' in equipment_legend
        assert equipment_legend.get('B') == '戴眼罩'
        assert 'BO' in equipment_legend
        assert equipment_legend.get('BO') == '只戴單邊眼罩'
        assert 'CP' in equipment_legend
        assert equipment_legend.get('CP') == '羊毛面箍'
    
    def test_scrape_horse_info_integration(self, scraper, sample_html):
        """测试完整爬取流程"""
        url = "https://racing.hkjc.com/zh-hk/local/information/horse?horseid=HK_2020_E436&Option=1"
        
        with patch('hkjc_scrapers.horse_info_scraper.requests.Session.get') as mock_get:
            mock_response = Mock()
            mock_response.text = sample_html
            mock_response.encoding = 'utf-8'
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response
            
            result = scraper.scrape_horse_info(url)
            
            assert result is not None
            assert result.get('horse_id') == 'HK_2020_E436'
            assert 'basic_info' in result
            assert 'race_records' in result
            assert 'equipment_legend' in result
            assert 'scraped_at' in result
            assert 'source_url' in result
    
    def test_empty_result_on_error(self, scraper):
        """测试错误时返回空字典"""
        url = "https://racing.hkjc.com/zh-hk/local/information/horse?horseid=INVALID"
        
        with patch('hkjc_scrapers.horse_info_scraper.requests.Session.get') as mock_get:
            mock_get.side_effect = Exception("Network error")
            
            result = scraper.scrape_horse_info(url)
            
            assert result == {}

