#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
香港赛马会马匹信息爬虫
用于提取马匹详细信息，包括基本信息、赛绩记录、血统信息等
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from typing import Dict, List, Optional
from urllib.parse import urlparse, parse_qs
from datetime import datetime


class HorseInfoScraper:
    """香港赛马会马匹信息爬虫类"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-HK,zh;q=0.9,en;q=0.8',
        })
    
    def scrape_horse_info(self, url: str) -> Dict:
        """
        爬取马匹信息页面
        
        Args:
            url: 马匹信息页面URL
            
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
            horse_id = params.get('horseid', [''])[0]
            
            result = {
                'horse_id': horse_id,
                'source_url': url,
                'scraped_at': datetime.now().isoformat(),
                'basic_info': self._extract_basic_info(soup),
                'race_records': self._extract_race_records(soup),
                'equipment_legend': self._extract_equipment_legend(soup),
                'raw_html': response.text  # 保存原始HTML以备后续分析
            }
            
            return result
            
        except requests.RequestException as e:
            print(f"请求错误: {e}")
            return {}
        except Exception as e:
            print(f"解析错误: {e}")
            return {}
    
    def _extract_basic_info(self, soup: BeautifulSoup) -> Dict:
        """提取马匹基本信息"""
        basic_info = {}
        
        # 提取马匹名称（通常在标题或h1-h6标签中）
        title_elements = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        for title in title_elements:
            text = title.get_text(strip=True)
            # 查找包含马匹名称的模式，如"遨遊氣泡 (E436)"
            horse_name_match = re.search(r'([^(]+)\s*\(([A-Z]\d+)\)', text)
            if horse_name_match:
                basic_info['horse_name'] = horse_name_match.group(1).strip()
                basic_info['horse_code'] = horse_name_match.group(2)
                break
        
        # 如果没有找到，尝试从页面文本中提取
        if 'horse_name' not in basic_info:
            page_text = soup.get_text()
            # 查找马匹名称模式
            name_patterns = [
                r'([^\n(]+)\s*\(([A-Z]\d+)\)',  # 名称 (代码)
                r'馬名[：:]\s*([^\n]+)',  # 馬名: 名称
            ]
            for pattern in name_patterns:
                match = re.search(pattern, page_text)
                if match:
                    if len(match.groups()) == 2:
                        basic_info['horse_name'] = match.group(1).strip()
                        basic_info['horse_code'] = match.group(2)
                    else:
                        basic_info['horse_name'] = match.group(1).strip()
                    break
        
        # 查找包含基本信息的表格
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            if not rows:
                continue
            
            # 检查是否是横向表格（表头在第一行，数据在第二行）
            first_row = rows[0]
            first_cells = first_row.find_all(['td', 'th'])
            
            # 如果第一行包含表头关键词，可能是横向表格
            first_row_text = first_row.get_text()
            is_horizontal_table = any(keyword in first_row_text for keyword in 
                                     ['馬名', '編號', '性別', '年齡', '毛色', '父系', '母系', 
                                      'Horse Name', 'Code', 'Sex', 'Age', 'Colour', 'Sire', 'Dam'])
            
            if is_horizontal_table and len(rows) >= 2:
                # 横向表格：第一行是表头，第二行是数据
                header_cells = first_row.find_all(['td', 'th'])
                data_row = rows[1]
                data_cells = data_row.find_all(['td', 'th'])
                
                for i, header_cell in enumerate(header_cells):
                    if i >= len(data_cells):
                        continue
                    
                    header = header_cell.get_text(strip=True)
                    data_cell = data_cells[i]
                    
                    # 优先从链接中提取文本，如果没有链接则使用单元格文本
                    link = data_cell.find('a')
                    if link:
                        value = link.get_text(strip=True)
                    else:
                        value = data_cell.get_text(strip=True)
                    
                    # 跳过空值或无效值
                    if not value or value == ':' or value == '--' or value == '-':
                        continue
                    
                    # 提取关键信息
                    self._extract_field_from_pair(basic_info, header, value)
            else:
                # 纵向表格：每行是键值对
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 3:
                        # 三列情况：第一列是键，第二列可能是":"，第三列是值
                        key = cells[0].get_text(strip=True)
                        middle_cell_text = cells[1].get_text(strip=True)
                        value_cell = cells[2]
                        
                        # 如果中间列是":"，跳过它，使用第三列作为值
                        if middle_cell_text == ':' or middle_cell_text == '：':
                            # 优先从链接中提取文本，如果没有链接则使用单元格文本
                            link = value_cell.find('a')
                            if link:
                                value = link.get_text(strip=True)
                            else:
                                value = value_cell.get_text(strip=True)
                            
                            # 跳过空值或无效值
                            if not value or value == ':' or value == '--' or value == '-':
                                continue
                            
                            # 处理键中包含 "/" 的情况，分别提取多个字段
                            if ' / ' in key or '/' in key:
                                keys = [k.strip() for k in key.split('/')]
                                values = [v.strip() for v in value.split('/')]
                                
                                # 如果值的数量与键的数量匹配，分别提取
                                if len(keys) == len(values):
                                    for k, v in zip(keys, values):
                                        if v and v != ':' and v != '--' and v != '-':
                                            self._extract_field_from_pair(basic_info, k, v)
                                else:
                                    # 如果不匹配，尝试按 "/" 分割值
                                    if '/' in value:
                                        value_parts = [v.strip() for v in value.split('/')]
                                        for i, k in enumerate(keys):
                                            if i < len(value_parts) and value_parts[i] and value_parts[i] != ':' and value_parts[i] != '--' and value_parts[i] != '-':
                                                self._extract_field_from_pair(basic_info, k, value_parts[i])
                                    else:
                                        # 如果只有一个值，尝试匹配第一个键
                                        if keys and value:
                                            self._extract_field_from_pair(basic_info, keys[0], value)
                            else:
                                # 单个键值对
                                self._extract_field_from_pair(basic_info, key, value)
                    elif len(cells) >= 2:
                        # 两列情况：第一列是键，第二列是值
                        key = cells[0].get_text(strip=True)
                        value_cell = cells[1]
                        
                        # 优先从链接中提取文本，如果没有链接则使用单元格文本
                        link = value_cell.find('a')
                        if link:
                            value = link.get_text(strip=True)
                        else:
                            value = value_cell.get_text(strip=True)
                        
                        # 跳过空值或无效值
                        if not value or value == ':' or value == '--' or value == '-':
                            continue
                        
                        # 处理键中包含 "/" 的情况
                        if ' / ' in key or '/' in key:
                            keys = [k.strip() for k in key.split('/')]
                            values = [v.strip() for v in value.split('/')]
                            
                            # 如果值的数量与键的数量匹配，分别提取
                            if len(keys) == len(values):
                                for k, v in zip(keys, values):
                                    if v and v != ':' and v != '--' and v != '-':
                                        self._extract_field_from_pair(basic_info, k, v)
                            else:
                                # 如果不匹配，尝试按 "/" 分割值
                                if '/' in value:
                                    value_parts = [v.strip() for v in value.split('/')]
                                    for i, k in enumerate(keys):
                                        if i < len(value_parts) and value_parts[i] and value_parts[i] != ':' and value_parts[i] != '--' and value_parts[i] != '-':
                                            self._extract_field_from_pair(basic_info, k, value_parts[i])
                                else:
                                    # 如果只有一个值，尝试匹配第一个键
                                    if keys and value:
                                        self._extract_field_from_pair(basic_info, keys[0], value)
                        else:
                            # 单个键值对
                            self._extract_field_from_pair(basic_info, key, value)
        
        return basic_info
    
    def _extract_field_from_pair(self, basic_info: Dict, key: str, value: str):
        """从键值对中提取字段"""
        # 再次检查值是否有效
        if not value or value == ':' or value == '--' or value == '-':
            return
        
        # 标准化键名（去除空格）
        key = key.strip()
        
        if '馬名' in key or 'Horse Name' in key:
            if 'horse_name' not in basic_info or not basic_info.get('horse_name'):
                basic_info['horse_name'] = value
        elif '編號' in key or 'Code' in key or 'Horse Code' in key:
            if 'horse_code' not in basic_info or not basic_info.get('horse_code'):
                basic_info['horse_code'] = value
        elif '性別' in key or 'Sex' in key or 'Gender' in key:
            if 'sex' not in basic_info or not basic_info.get('sex') or basic_info.get('sex') == ':':
                basic_info['sex'] = value
        elif '年齡' in key or 'Age' in key or '馬齡' in key:
            if 'age' not in basic_info or not basic_info.get('age') or basic_info.get('age') == ':':
                basic_info['age'] = value
        elif '毛色' in key or 'Colour' in key:
            if 'colour' not in basic_info or not basic_info.get('colour') or basic_info.get('colour') == ':':
                basic_info['colour'] = value
        elif '父系' in key or 'Sire' in key:
            if 'sire' not in basic_info or not basic_info.get('sire') or basic_info.get('sire') == ':':
                basic_info['sire'] = value
        elif '母系' in key or 'Dam' in key:
            if 'dam' not in basic_info or not basic_info.get('dam') or basic_info.get('dam') == ':':
                basic_info['dam'] = value
        elif '外祖父' in key or 'Maternal Grandsire' in key:
            if 'maternal_grandsire' not in basic_info or not basic_info.get('maternal_grandsire') or basic_info.get('maternal_grandsire') == ':':
                basic_info['maternal_grandsire'] = value
        elif '練馬師' in key or 'Trainer' in key:
            if 'trainer' not in basic_info or not basic_info.get('trainer') or basic_info.get('trainer') == ':':
                basic_info['trainer'] = value
        elif '馬主' in key or 'Owner' in key:
            if 'owner' not in basic_info or not basic_info.get('owner') or basic_info.get('owner') == ':':
                basic_info['owner'] = value
        elif '進口來源' in key or 'Import Source' in key:
            if 'import_source' not in basic_info or not basic_info.get('import_source') or basic_info.get('import_source') == ':':
                basic_info['import_source'] = value
        elif '出生地' in key or 'Birthplace' in key or 'Place of Birth' in key:
            if 'birthplace' not in basic_info or not basic_info.get('birthplace') or basic_info.get('birthplace') == ':':
                basic_info['birthplace'] = value
        elif '現時評分' in key or 'Current Rating' in key:
            if 'current_rating' not in basic_info or not basic_info.get('current_rating') or basic_info.get('current_rating') == ':':
                basic_info['current_rating'] = value
        elif '季初評分' in key or 'Season Start Rating' in key or 'Initial Rating' in key:
            if 'season_start_rating' not in basic_info or not basic_info.get('season_start_rating') or basic_info.get('season_start_rating') == ':':
                basic_info['season_start_rating'] = value
    
    def _extract_race_records(self, soup: BeautifulSoup) -> List[Dict]:
        """提取马匹赛绩记录"""
        race_records = []
        
        # 查找包含赛绩记录的表格
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            headers = []
            header_row = None
            
            # 查找表头（通常包含"日期"、"場地"、"距離"等）
            for row in rows:
                cells = row.find_all(['th', 'td'])
                if len(cells) > 5:  # 赛绩表格通常有很多列
                    row_text = row.get_text()
                    # 检查是否包含赛绩相关的关键词
                    if any(keyword in row_text for keyword in ['日期', '場地', '距離', '班次', '名次', 'Date', 'Venue', 'Distance', 'Class', 'Position']):
                        headers = [cell.get_text(strip=True) for cell in cells]
                        header_row = row
                        break
            
            if not headers:
                continue
            
            # 提取数据行
            data_rows = rows[rows.index(header_row) + 1:] if header_row else rows
            
            for row in data_rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) < 3:  # 跳过数据不足的行
                    continue
                
                # 跳过表头行
                row_text = row.get_text()
                if any(keyword in row_text for keyword in ['日期', '場地', '距離', 'Date', 'Venue', 'Distance']):
                    continue
                
                race_record = {}
                
                # 根据表头提取数据
                for i, cell in enumerate(cells):
                    if i < len(headers):
                        header = headers[i]
                        value = cell.get_text(strip=True)
                        
                        # 提取链接中的信息
                        links = cell.find_all('a', href=True)
                        for link in links:
                            href = link.get('href', '')
                            # 提取练马师ID
                            if 'trainerid=' in href:
                                trainer_id_match = re.search(r'trainerid=([^&]+)', href)
                                if trainer_id_match:
                                    race_record['trainer_id'] = trainer_id_match.group(1)
                            # 提取骑师ID
                            elif 'jockeyid=' in href:
                                jockey_id_match = re.search(r'jockeyid=([^&]+)', href)
                                if jockey_id_match:
                                    race_record['jockey_id'] = jockey_id_match.group(1)
                        
                        # 根据表头名称提取相应信息
                        if '日期' in header or 'Date' in header:
                            race_record['date'] = value
                        elif '場地' in header or 'Venue' in header:
                            race_record['venue'] = value
                        elif '距離' in header or 'Distance' in header:
                            race_record['distance'] = value
                        elif '班次' in header or 'Class' in header:
                            race_record['class'] = value
                        elif '名次' in header or 'Position' in header or 'Placing' in header:
                            race_record['position'] = value
                        elif '騎師' in header or 'Jockey' in header:
                            race_record['jockey'] = value
                        elif '練馬師' in header or 'Trainer' in header:
                            race_record['trainer'] = value
                        elif '檔位' in header or 'Draw' in header:
                            race_record['draw'] = value
                        elif '體重' in header or 'Weight' in header:
                            race_record['weight'] = value
                        elif '評分' in header or 'Rating' in header:
                            race_record['rating'] = value
                        elif '賠率' in header or 'Odds' in header:
                            race_record['odds'] = value
                        elif '完成時間' in header or 'Time' in header or 'Finish Time' in header:
                            race_record['finish_time'] = value
                        elif '跑道' in header or 'Track' in header or 'Course' in header:
                            race_record['track'] = value
                        elif '場地狀況' in header or 'Going' in header or 'Track Condition' in header:
                            race_record['track_condition'] = value
                        elif '裝備' in header or 'Equipment' in header:
                            race_record['equipment'] = value
                        else:
                            # 保存其他列的数据
                            if header and value:
                                race_record[header] = value
                
                # 只添加有足够数据的记录
                if race_record and ('date' in race_record or 'venue' in race_record):
                    race_records.append(race_record)
        
        return race_records
    
    def _extract_equipment_legend(self, soup: BeautifulSoup) -> Dict:
        """提取装备图例说明"""
        equipment_legend = {}
        
        # 查找包含装备图例的表格或文本
        tables = soup.find_all('table')
        
        for table in tables:
            table_text = table.get_text()
            # 查找包含装备说明的部分
            if '眼罩' in table_text or 'Equipment' in table_text or 'B :' in table_text or 'BO :' in table_text:
                rows = table.find_all('tr')
                
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    text = row.get_text()
                    
                    # 提取装备代码和说明
                    # 格式如: "B :  戴眼罩" 或 "BO :  只戴單邊眼罩"
                    equipment_patterns = [
                        r'([A-Z]+(?:\s+[A-Z]+)?)\s*:\s*([^\n]+)',
                        r'([A-Z]+(?:\s+[A-Z]+)?)\s*：\s*([^\n]+)',
                    ]
                    
                    for pattern in equipment_patterns:
                        matches = re.findall(pattern, text)
                        for code, description in matches:
                            code = code.strip()
                            description = description.strip()
                            if code and description:
                                equipment_legend[code] = description
                
                # 如果找到了装备图例，跳出循环
                if equipment_legend:
                    break
        
        return equipment_legend
    
    def save_to_json(self, data: Dict, filename: str):
        """保存数据到JSON文件"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"数据已保存到: {filename}")
    
    def save_to_csv(self, data: Dict, filename: str):
        """保存赛绩记录到CSV文件"""
        import csv
        
        if 'race_records' not in data or not data['race_records']:
            print("没有赛绩记录可保存")
            return
        
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            if data['race_records']:
                # 收集所有记录中的所有唯一字段名
                fieldnames_set = set()
                for record in data['race_records']:
                    fieldnames_set.update(record.keys())
                # 转换为列表并排序，确保字段顺序一致
                fieldnames = sorted(list(fieldnames_set))
                
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data['race_records'])
        
        print(f"赛绩记录已保存到: {filename}")


def main():
    """主函数"""
    scraper = HorseInfoScraper()
    
    # 测试URL
    url = "https://racing.hkjc.com/zh-hk/local/information/horse?horseid=HK_2020_E436&Option=1"
    
    print(f"正在爬取: {url}")
    result = scraper.scrape_horse_info(url)
    
    if result:
        # 保存为JSON
        scraper.save_to_json(result, 'horse_info.json')
        
        # 如果有赛绩记录，也保存为CSV
        if result.get('race_records'):
            scraper.save_to_csv(result, 'horse_race_records.csv')
        
        # 打印摘要信息
        print("\n=== 爬取摘要 ===")
        print(f"马匹ID: {result.get('horse_id')}")
        basic_info = result.get('basic_info', {})
        print(f"马匹名称: {basic_info.get('horse_name', 'N/A')}")
        print(f"马匹编号: {basic_info.get('horse_code', 'N/A')}")
        print(f"练马师: {basic_info.get('trainer', 'N/A')}")
        print(f"赛绩记录数量: {len(result.get('race_records', []))}")
        print(f"装备图例数量: {len(result.get('equipment_legend', {}))}")
    else:
        print("爬取失败")


if __name__ == '__main__':
    main()

