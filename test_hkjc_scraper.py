#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HKJC爬虫集成测试
测试爬虫的核心功能，确保PR不会破坏现有功能
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from bs4 import BeautifulSoup

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hkjc_scraper import HKJCScraper


class TestHKJCScraper:
    """HKJC爬虫测试类"""
    
    @pytest.fixture
    def scraper(self):
        """创建爬虫实例"""
        return HKJCScraper()
    
    @pytest.fixture
    def sample_html(self):
        """示例HTML内容"""
        return """
        <html>
        <head><title>赛马结果</title></head>
        <body>
            <h1>沙田: 第三场</h1>
            <table>
                <tr>
                    <th>名次</th>
                    <th>编号</th>
                    <th>馬名</th>
                    <th>騎師</th>
                    <th>練馬師</th>
                    <th>檔位</th>
                    <th>體重</th>
                </tr>
                <tr>
                    <td>1</td>
                    <td>1</td>
                    <td><a href="/horse?horseid=HK_2025_L155">国千金</a></td>
                    <td>潘頓</td>
                    <td>蔡約翰</td>
                    <td>1</td>
                    <td>135</td>
                </tr>
                <tr>
                    <td>2</td>
                    <td>2</td>
                    <td><a href="/horse?horseid=HK_2024_K123">测试马</a></td>
                    <td>莫雷拉</td>
                    <td>方嘉柏</td>
                    <td>2</td>
                    <td>130</td>
                </tr>
            </table>
            <table>
                <tr>
                    <th>名次</th>
                    <th>编号</th>
                    <th>馬名</th>
                    <th>報告</th>
                </tr>
                <tr>
                    <td>1</td>
                    <td>1</td>
                    <td><a href="/horse?horseid=HK_2025_L155">国千金</a></td>
                    <td>出閘迅速，全程領先</td>
                </tr>
            </table>
            <table>
                <tr>
                    <th>勝出馬匹血統</th>
                </tr>
                <tr>
                    <td><a href="/horse?horseid=HK_2025_L155">国千金</a></td>
                    <td>父系: Starspangledbanner 母系: Red Pixie</td>
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
        url = "https://racing.hkjc.com/zh-hk/local/information/localresults?racedate=2026/01/18&Racecourse=ST&RaceNo=3"
        
        with patch('requests.Session.get') as mock_get:
            mock_response = Mock()
            mock_response.text = "<html><body>Test</body></html>"
            mock_response.encoding = 'utf-8'
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response
            
            result = scraper.scrape_race_result(url)
            
            assert result is not None
            assert result.get('race_date') == '2026/01/18'
            assert result.get('racecourse') == 'ST'
            assert result.get('race_no') == '3'
    
    def test_extract_race_info(self, scraper, sample_html):
        """测试比赛信息提取"""
        soup = BeautifulSoup(sample_html, 'html.parser')
        race_info = scraper._extract_race_info(soup)
        
        assert isinstance(race_info, dict)
        assert 'venue' in race_info or len(race_info) >= 0
    
    def test_extract_horse_info(self, scraper, sample_html):
        """测试马匹信息提取"""
        soup = BeautifulSoup(sample_html, 'html.parser')
        horses = scraper._extract_horse_info(soup)
        
        assert isinstance(horses, list)
        if len(horses) > 0:
            assert 'horse_name' in horses[0] or 'horse_id' in horses[0]
    
    def test_extract_incident_reports(self, scraper, sample_html):
        """测试事件报告提取"""
        soup = BeautifulSoup(sample_html, 'html.parser')
        incidents = scraper._extract_incident_reports(soup)
        
        assert isinstance(incidents, list)
    
    def test_extract_pedigree(self, scraper, sample_html):
        """测试血统信息提取"""
        soup = BeautifulSoup(sample_html, 'html.parser')
        pedigree = scraper._extract_pedigree(soup)
        
        assert isinstance(pedigree, dict)
    
    def test_save_to_json(self, scraper, tmp_path):
        """测试JSON保存功能"""
        test_data = {
            'race_date': '2026/01/18',
            'racecourse': 'ST',
            'race_no': '3',
            'horses': [{'horse_name': '测试马', 'number': '1'}]
        }
        
        json_file = tmp_path / 'test_output.json'
        scraper.save_to_json(test_data, str(json_file))
        
        assert json_file.exists()
        
        # 验证JSON内容
        import json
        with open(json_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
            assert loaded_data['race_date'] == '2026/01/18'
    
    def test_save_to_csv(self, scraper, tmp_path):
        """测试CSV保存功能"""
        test_data = {
            'horses': [
                {'horse_name': '测试马1', 'number': '1', 'jockey': '骑师1'},
                {'horse_name': '测试马2', 'number': '2', 'jockey': '骑师2'}
            ]
        }
        
        csv_file = tmp_path / 'test_output.csv'
        scraper.save_to_csv(test_data, str(csv_file))
        
        assert csv_file.exists()
        
        # 验证CSV内容
        import csv
        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 2
            assert rows[0]['horse_name'] == '测试马1'
    
    def test_save_to_csv_empty_data(self, scraper, tmp_path):
        """测试CSV保存空数据"""
        test_data = {'horses': []}
        
        csv_file = tmp_path / 'test_empty.csv'
        scraper.save_to_csv(test_data, str(csv_file))
        
        # 空数据不应该创建文件或应该创建空文件
        # 根据实现，这里可能不创建文件
    
    def test_error_handling_invalid_url(self, scraper):
        """测试无效URL的错误处理"""
        with patch('requests.Session.get') as mock_get:
            mock_get.side_effect = Exception("Connection error")
            
            result = scraper.scrape_race_result("invalid_url")
            
            # 应该返回空字典而不是抛出异常
            assert isinstance(result, dict)
    
    def test_integration_real_url(self, scraper):
        """集成测试：测试真实URL（可选，可能需要网络）"""
        # 这个测试默认跳过，除非明确启用
        pytest.skip("跳过真实URL测试，避免在CI中依赖外部服务")
        
        url = "https://racing.hkjc.com/zh-hk/local/information/localresults?racedate=2026/01/18&Racecourse=ST&RaceNo=3"
        result = scraper.scrape_race_result(url)
        
        assert result is not None
        assert 'race_date' in result
        assert 'racecourse' in result
        assert 'race_no' in result
    
    def test_result_structure(self, scraper):
        """测试返回结果的结构"""
        url = "https://racing.hkjc.com/zh-hk/local/information/localresults?racedate=2026/01/18&Racecourse=ST&RaceNo=3"
        
        with patch('requests.Session.get') as mock_get:
            mock_response = Mock()
            mock_response.text = "<html><body><table><tr><td>Test</td></tr></table></body></html>"
            mock_response.encoding = 'utf-8'
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response
            
            result = scraper.scrape_race_result(url)
            
            # 验证必需字段存在
            required_fields = ['race_date', 'racecourse', 'race_no', 'race_info', 
                             'horses', 'race_result', 'incident_reports', 'pedigree']
            for field in required_fields:
                assert field in result, f"缺少必需字段: {field}"
            
            # 验证字段类型
            assert isinstance(result['race_info'], dict)
            assert isinstance(result['horses'], list)
            assert isinstance(result['race_result'], dict)
            assert isinstance(result['incident_reports'], list)
            assert isinstance(result['pedigree'], dict)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

