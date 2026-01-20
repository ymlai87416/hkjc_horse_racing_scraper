#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
香港赛马会比赛结果爬虫
用于提取比赛详细信息，包括马匹信息、比赛结果、事件报告等
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from typing import Dict, List, Optional
from urllib.parse import urlparse, parse_qs


class RaceResultScraper:
    """香港赛马会爬虫类"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-HK,zh;q=0.9,en;q=0.8',
        })
    
    def scrape_race_result(self, url: str) -> Dict:
        """
        爬取比赛结果页面
        
        Args:
            url: 比赛结果页面URL
            
        Returns:
            包含所有提取信息的字典
        """
        try:
            response = self.session.get(url, timeout=30)
            response.encoding = 'utf-8'
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 解析URL参数
            parsed_url = urlparse(url)
            params = parse_qs(parsed_url.query)
            
            result = {
                'race_date': params.get('racedate', [''])[0],
                'racecourse': params.get('Racecourse', [''])[0],
                'race_no': params.get('RaceNo', [''])[0],
                'race_info': self._extract_race_info(soup),
                'horses': self._extract_horse_info(soup),
                'race_result': self._extract_race_result(soup),
                'incident_reports': self._extract_incident_reports(soup),
                'pedigree': self._extract_pedigree(soup),
                'raw_html': response.text  # 保存原始HTML以备后续分析
            }
            
            return result
            
        except requests.RequestException as e:
            print(f"请求错误: {e}")
            return {}
        except Exception as e:
            print(f"解析错误: {e}")
            return {}
    
    def _extract_race_info(self, soup: BeautifulSoup) -> Dict:
        """提取比赛基本信息"""
        race_info = {}
        
        # 提取比赛标题和基本信息
        title_elements = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        for title in title_elements:
            text = title.get_text(strip=True)
            if '沙田' in text or '跑馬地' in text:
                race_info['venue'] = text.split(':')[0] if ':' in text else text
        
        # 查找包含比赛信息的表格
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    key = cells[0].get_text(strip=True)
                    value = cells[1].get_text(strip=True)
                    
                    # 提取关键信息
                    if '距離' in key or 'Distance' in key:
                        race_info['distance'] = value
                    elif '班次' in key or 'Class' in key:
                        race_info['class'] = value
                    elif '時間' in key or 'Time' in key:
                        race_info['time'] = value
                    elif '賽道' in key or 'Track' in key:
                        race_info['track'] = value
        
        # 尝试从页面文本中提取信息
        page_text = soup.get_text()
        
        # 提取距离信息（如：1200米）
        distance_match = re.search(r'(\d+)\s*米', page_text)
        if distance_match:
            race_info['distance_meters'] = distance_match.group(1)
        
        # 提取班次信息（如：第五班）
        class_match = re.search(r'第([一二三四五六七八九十]+)班', page_text)
        if class_match:
            race_info['class_chinese'] = class_match.group(0)
        
        # 提取时间信息
        time_match = re.search(r'(\d{1,2}):(\d{2})\s*(AM|PM)', page_text, re.IGNORECASE)
        if time_match:
            race_info['race_time'] = time_match.group(0)
        
        return race_info
    
    def _extract_horse_info(self, soup: BeautifulSoup) -> List[Dict]:
        """提取参赛马匹信息"""
        horses = []
        
        # 查找包含马匹信息的表格
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            headers = []
            header_row = None
            
            # 查找表头
            for row in rows:
                cells = row.find_all(['th', 'td'])
                if len(cells) > 5:  # 可能是表头行
                    headers = [cell.get_text(strip=True) for cell in cells]
                    header_row = row
                    break
            
            if not headers:
                continue
            
            # 提取数据行
            data_rows = rows[rows.index(header_row) + 1:] if header_row else rows
            
            for row in data_rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) < 3:
                    continue
                
                horse_data = {}
                
                # 提取链接中的马匹ID
                links = row.find_all('a', href=True)
                for link in links:
                    href = link.get('href', '')
                    if 'horseid=' in href:
                        horse_id_match = re.search(r'horseid=([^&]+)', href)
                        if horse_id_match:
                            horse_data['horse_id'] = horse_id_match.group(1)
                            horse_data['horse_name'] = link.get_text(strip=True)
                            horse_data['horse_url'] = link.get('href')
                
                # 提取表格单元格数据
                for i, cell in enumerate(cells):
                    if i < len(headers):
                        header = headers[i]
                        value = cell.get_text(strip=True)
                        
                        # 根据表头名称提取相应信息
                        if '馬名' in header or 'Horse' in header:
                            if 'horse_name' not in horse_data:
                                horse_data['horse_name'] = value
                        elif '編號' in header or 'No' in header or 'No.' in header:
                            horse_data['number'] = value
                        elif '騎師' in header or 'Jockey' in header:
                            horse_data['jockey'] = value
                        elif '練馬師' in header or 'Trainer' in header:
                            horse_data['trainer'] = value
                        elif '檔位' in header or 'Draw' in header:
                            horse_data['draw'] = value
                        elif '體重' in header or 'Weight' in header:
                            horse_data['weight'] = value
                        elif '評分' in header or 'Rating' in header:
                            horse_data['rating'] = value
                        elif '賠率' in header or 'Odds' in header:
                            horse_data['odds'] = value
                        elif '名次' in header or 'Position' in header or 'Placing' in header:
                            horse_data['position'] = value
                        else:
                            # 保存其他列的数据
                            if header:
                                horse_data[header] = value
                
                if horse_data:
                    horses.append(horse_data)
        
        return horses
    
    def _extract_race_result(self, soup: BeautifulSoup) -> Dict:
        """提取比赛结果信息"""
        result = {}
        
        # 查找结果表格
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            
            # 查找包含"名次"、"完成時間"等关键词的表格
            table_text = table.get_text()
            if '名次' in table_text or '完成時間' in table_text or 'Position' in table_text:
                headers = []
                data_rows = []
                
                for row in rows:
                    cells = row.find_all(['th', 'td'])
                    if len(cells) > 3:
                        if not headers:
                            headers = [cell.get_text(strip=True) for cell in cells]
                        else:
                            row_data = {}
                            for i, cell in enumerate(cells):
                                if i < len(headers):
                                    row_data[headers[i]] = cell.get_text(strip=True)
                            
                            # 提取链接
                            links = row.find_all('a', href=True)
                            for link in links:
                                href = link.get('href', '')
                                if 'horseid=' in href:
                                    horse_id_match = re.search(r'horseid=([^&]+)', href)
                                    if horse_id_match:
                                        row_data['horse_id'] = horse_id_match.group(1)
                                        row_data['horse_name'] = link.get_text(strip=True)
                            
                            if row_data:
                                data_rows.append(row_data)
                
                if data_rows:
                    result['finishing_order'] = data_rows
        
        return result
    
    def _extract_incident_reports(self, soup: BeautifulSoup) -> List[Dict]:
        """提取比赛事件报告"""
        incidents = []
        
        # 查找包含"競賽事件報告"或"Incident"的部分
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            table_text = table.get_text()
            
            if '競賽事件報告' in table_text or 'Incident' in table_text or '報告' in table_text:
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 3:
                        incident = {}
                        
                        # 提取位置/名次
                        if cells[0].get_text(strip=True).isdigit():
                            incident['position'] = cells[0].get_text(strip=True)
                        
                        # 提取马匹编号
                        if cells[1].get_text(strip=True).isdigit():
                            incident['horse_number'] = cells[1].get_text(strip=True)
                        
                        # 提取马匹名称和链接
                        links = row.find_all('a', href=True)
                        for link in links:
                            href = link.get('href', '')
                            if 'horseid=' in href:
                                horse_id_match = re.search(r'horseid=([^&]+)', href)
                                if horse_id_match:
                                    incident['horse_id'] = horse_id_match.group(1)
                                    incident['horse_name'] = link.get_text(strip=True)
                        
                        # 提取事件描述（通常在最后一列）
                        if len(cells) >= 3:
                            incident['description'] = cells[-1].get_text(strip=True)
                        
                        if incident:
                            incidents.append(incident)
        
        return incidents
    
    def _extract_pedigree(self, soup: BeautifulSoup) -> Dict:
        """提取胜出马匹血统信息"""
        pedigree = {}
        
        # 查找包含"血統"或"Pedigree"的部分
        tables = soup.find_all('table')
        
        for table in tables:
            table_text = table.get_text()
            if '血統' in table_text or 'Pedigree' in table_text or '父系' in table_text:
                rows = table.find_all('tr')
                
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    text = row.get_text()
                    
                    # 提取马匹名称
                    links = row.find_all('a', href=True)
                    for link in links:
                        href = link.get('href', '')
                        if 'horseid=' in href:
                            horse_id_match = re.search(r'horseid=([^&]+)', href)
                            if horse_id_match:
                                pedigree['horse_id'] = horse_id_match.group(1)
                                pedigree['horse_name'] = link.get_text(strip=True)
                    
                    # 提取父系信息
                    if '父系' in text or 'Sire' in text or '父系:' in text:
                        sire_match = re.search(r'父系[：:]\s*([^\n]+)', text)
                        if sire_match:
                            pedigree['sire'] = sire_match.group(1).strip()
                        else:
                            # 尝试从单元格中提取
                            for cell in cells:
                                cell_text = cell.get_text(strip=True)
                                if '父系' in cell_text or 'Sire' in cell_text:
                                    continue
                                if cell_text and '父系' not in cell_text:
                                    if 'sire' not in pedigree:
                                        pedigree['sire'] = cell_text
                    
                    # 提取母系信息
                    if '母系' in text or 'Dam' in text or '母系:' in text:
                        dam_match = re.search(r'母系[：:]\s*([^\n]+)', text)
                        if dam_match:
                            pedigree['dam'] = dam_match.group(1).strip()
                        else:
                            # 尝试从单元格中提取
                            for cell in cells:
                                cell_text = cell.get_text(strip=True)
                                if '母系' in cell_text or 'Dam' in cell_text:
                                    continue
                                if cell_text and '母系' not in cell_text:
                                    if 'dam' not in pedigree:
                                        pedigree['dam'] = cell_text
                
                # 如果找到了父系和母系，跳出循环
                if 'sire' in pedigree or 'dam' in pedigree:
                    break
        
        return pedigree
    
    def save_to_json(self, data: Dict, filename: str):
        """保存数据到JSON文件"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"数据已保存到: {filename}")
    
    def save_to_csv(self, data: Dict, filename: str):
        """保存马匹数据到CSV文件"""
        import csv
        
        if 'horses' not in data or not data['horses']:
            print("没有马匹数据可保存")
            return
        
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            if data['horses']:
                fieldnames = list(data['horses'][0].keys())
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data['horses'])
        
        print(f"马匹数据已保存到: {filename}")


def main():
    """主函数"""
    scraper = RaceResultScraper()
    
    # 测试URL
    url = "https://racing.hkjc.com/zh-hk/local/information/localresults?racedate=2026/01/18&Racecourse=ST&RaceNo=3"
    
    print(f"正在爬取: {url}")
    result = scraper.scrape_race_result(url)
    
    if result:
        # 保存为JSON
        scraper.save_to_json(result, 'race_result.json')
        
        # 如果有马匹数据，也保存为CSV
        if result.get('horses'):
            scraper.save_to_csv(result, 'race_horses.csv')
        
        # 打印摘要信息
        print("\n=== 爬取摘要 ===")
        print(f"比赛日期: {result.get('race_date')}")
        print(f"场地: {result.get('racecourse')}")
        print(f"场次: {result.get('race_no')}")
        print(f"比赛信息: {result.get('race_info')}")
        print(f"马匹数量: {len(result.get('horses', []))}")
        print(f"事件报告数量: {len(result.get('incident_reports', []))}")
        print(f"血统信息: {result.get('pedigree')}")
    else:
        print("爬取失败")


if __name__ == '__main__':
    main()

