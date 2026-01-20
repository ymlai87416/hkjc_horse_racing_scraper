#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
香港赛马会赛程表爬虫
用于提取赛程表信息，包括所有赛马日期、场地、赛事类型等
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from typing import Dict, List, Optional
from datetime import datetime


class RaceScheduleScraper:
    """香港赛马会赛程表爬虫类"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-HK,zh;q=0.9,en;q=0.8',
        })
    
    def scrape_schedule(self, url: Optional[str] = None) -> Dict:
        """
        爬取赛程表页面
        
        Args:
            url: 赛程表页面URL，如果为None则使用默认URL
            
        Returns:
            包含所有提取信息的字典
        """
        if url is None:
            url = "https://racing.hkjc.com/zh-hk/local/information/fixture?b_cid=SPLDSPA_hkjc-home_MegaMenu"
        
        try:
            response = self.session.get(url, timeout=30)
            response.encoding = 'utf-8'
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            result = {
                'source_url': url,
                'scraped_at': datetime.now().isoformat(),
                'months': self._extract_months(soup),
                'race_days': self._extract_race_days(soup),
                'legend': self._extract_legend(soup),
                'notices': self._extract_notices(soup),
                'raw_html': response.text  # 保存原始HTML以备后续分析
            }
            
            return result
            
        except requests.RequestException as e:
            print(f"请求错误: {e}")
            return {}
        except Exception as e:
            print(f"解析错误: {e}")
            return {}
    
    def _extract_months(self, soup: BeautifulSoup) -> List[str]:
        """提取页面中显示的月份列表"""
        months = []
        
        # 查找月份选择器或月份标题
        month_elements = soup.find_all(['option', 'a', 'span', 'div'], 
                                      string=re.compile(r'[一二三四五六七八九十]+月|九月|十月|十一月|十二月|一月|二月|三月|四月|五月|六月|七月'))
        
        for element in month_elements:
            month_text = element.get_text(strip=True)
            if month_text and month_text not in months:
                months.append(month_text)
        
        # 如果没找到，尝试从表格标题中提取
        if not months:
            table_headers = soup.find_all(['th', 'td', 'caption'])
            for header in table_headers:
                text = header.get_text(strip=True)
                month_match = re.search(r'([一二三四五六七八九十]+年)?([一二三四五六七八九十]+月|九月|十月|十一月|十二月|一月|二月|三月|四月|五月|六月|七月)', text)
                if month_match:
                    month_text = month_match.group(2)
                    if month_text and month_text not in months:
                        months.append(month_text)
        
        return months
    
    def _extract_legend(self, soup: BeautifulSoup) -> Dict:
        """提取图例说明"""
        legend = {
            'venues': {},
            'race_types': {},
            'track_types': {},
            'race_classes': {},
            'special_marks': {}
        }
        
        # 查找图例部分
        page_text = soup.get_text()
        
        # 提取场地图例
        venue_patterns = {
            '跑马地': r'跑馬地|跑马地',
            '沙田': r'沙田'
        }
        for key, pattern in venue_patterns.items():
            if re.search(pattern, page_text):
                legend['venues'][key] = True
        
        # 提取赛马类型图例
        race_type_patterns = {
            '日赛': r'日賽|日赛',
            '黄昏赛': r'黄昏賽|黄昏赛',
            '夜赛': r'夜賽|夜赛'
        }
        for key, pattern in race_type_patterns.items():
            if re.search(pattern, page_text):
                legend['race_types'][key] = True
        
        # 提取赛道类型图例
        track_patterns = {
            '草地': r'草地',
            '混合赛道': r'混合賽道|混合赛道'
        }
        for key, pattern in track_patterns.items():
            if re.search(pattern, page_text):
                legend['track_types'][key] = True
        
        # 提取赛事级别图例
        class_patterns = {
            '一级赛': r'一級賽|一级赛',
            '二级赛': r'二級賽|二级赛',
            '三级赛': r'三級賽|三级赛',
            '四岁': r'四歲|四岁'
        }
        for key, pattern in class_patterns.items():
            if re.search(pattern, page_text):
                legend['race_classes'][key] = True
        
        # 提取特殊标记说明
        special_marks = {
            'C': '盃賽',
            'P': '獲得優先出賽權',
            'S': '特別參賽條件'
        }
        for mark, desc in special_marks.items():
            if mark in page_text or desc in page_text:
                legend['special_marks'][mark] = desc
        
        return legend
    
    def _extract_notices(self, soup: BeautifulSoup) -> List[str]:
        """提取页面中的通知信息"""
        notices = []
        
        # 查找通知文本（通常在页面底部或特定区域）
        page_text = soup.get_text()
        
        # 查找包含"取消"、"延期"等关键词的通知
        notice_patterns = [
            r'原定於.*?取消',
            r'原定于.*?取消',
            r'延期',
            r'改期',
            r'注意.*?事項',
            r'注意.*?事项'
        ]
        
        for pattern in notice_patterns:
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            for match in matches:
                if match and match not in notices:
                    notices.append(match.strip())
        
        return notices
    
    def _extract_race_days(self, soup: BeautifulSoup) -> List[Dict]:
        """提取所有赛马日信息"""
        race_days = []
        
        # 查找所有表格
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            
            # 查找表头，确定列的位置
            headers = []
            header_row = None
            
            for row in rows:
                cells = row.find_all(['th', 'td'])
                if len(cells) >= 7:  # 日历表格通常有7列（周日到周六）
                    headers = [cell.get_text(strip=True) for cell in cells]
                    header_row = row
                    break
            
            if not headers:
                continue
            
            # 提取数据行
            data_rows = rows[rows.index(header_row) + 1:] if header_row else rows
            
            current_month = None
            current_year = None
            
            for row in data_rows:
                cells = row.find_all(['td', 'th'])
                
                # 检查是否是月份/年份行
                row_text = row.get_text(strip=True)
                year_match = re.search(r'二[0-9一二三四五六七八九十]+年|(\d{4})年', row_text)
                if year_match:
                    year_str = year_match.group(0)
                    # 提取年份数字
                    year_num_match = re.search(r'(\d{4})', year_str)
                    if year_num_match:
                        current_year = year_num_match.group(1)
                    else:
                        # 处理中文年份
                        chinese_year = self._convert_chinese_year(year_str)
                        if chinese_year:
                            current_year = chinese_year
                
                month_match = re.search(r'([一二三四五六七八九十]+月|九月|十月|十一月|十二月|一月|二月|三月|四月|五月|六月|七月)', row_text)
                if month_match:
                    current_month = month_match.group(1)
                    continue
                
                # 处理日期单元格
                for i, cell in enumerate(cells):
                    cell_text = cell.get_text(strip=True)
                    
                    # 检查是否是日期数字
                    if cell_text.isdigit() and 1 <= int(cell_text) <= 31:
                        day = int(cell_text)
                        
                        # 提取该单元格中的所有信息
                        race_day_info = self._parse_race_day_cell(cell, day, current_month, current_year)
                        
                        if race_day_info:
                            race_days.append(race_day_info)
        
        return race_days
    
    def _parse_race_day_cell(self, cell, day: int, month: Optional[str], year: Optional[str]) -> Optional[Dict]:
        """解析单个日期单元格，提取赛马日信息"""
        race_day = {
            'day': day,
            'month': month,
            'year': year,
            'date': None,
            'venues': [],
            'race_types': [],
            'track_types': [],
            'race_classes': [],
            'special_marks': [],
            'prize_money': [],
            'notes': []
        }
        
        # 构建日期字符串
        if year and month:
            try:
                month_num = self._convert_chinese_month(month)
                if month_num:
                    date_str = f"{year}-{month_num:02d}-{day:02d}"
                    race_day['date'] = date_str
            except:
                pass
        
        # 查找图片标签（图标）
        images = cell.find_all('img')
        for img in images:
            src = img.get('src', '')
            alt = img.get('alt', '')
            title = img.get('title', '')
            
            # 解析场地图标
            if 'hv-ch' in src or '跑馬地' in alt or '跑马地' in alt:
                race_day['venues'].append('跑马地')
            elif 'st-ch' in src or '沙田' in alt:
                race_day['venues'].append('沙田')
            
            # 解析赛马类型图标
            if 'day' in src or '日賽' in alt or '日赛' in alt:
                race_day['race_types'].append('日赛')
            elif 'dusk' in src or '黄昏賽' in alt or '黄昏赛' in alt:
                race_day['race_types'].append('黄昏赛')
            elif 'night' in src or '夜賽' in alt or '夜赛' in alt:
                race_day['race_types'].append('夜赛')
            
            # 解析赛道类型图标
            if 'turf' in src or '草地' in alt:
                race_day['track_types'].append('草地')
            elif 'mixed' in src or '混合' in alt:
                race_day['track_types'].append('混合赛道')
            elif 'awt' in src or '全天候' in alt:
                race_day['track_types'].append('全天候跑道')
            
            # 解析赛事级别图标
            if 'class_g1' in src or '一級賽' in alt or '一级赛' in alt:
                race_day['race_classes'].append('一级赛')
            elif 'class_g2' in src or '二級賽' in alt or '二级赛' in alt:
                race_day['race_classes'].append('二级赛')
            elif 'class_g3' in src or '三級賽' in alt or '三级赛' in alt:
                race_day['race_classes'].append('三级赛')
            elif 'class_4YO' in src or '四歲' in alt or '四岁' in alt:
                race_day['race_classes'].append('四岁')
        
        # 提取文本内容
        cell_text = cell.get_text(strip=True)
        
        # 提取特殊标记（C, P, S）
        if 'C' in cell_text:
            race_day['special_marks'].append('C')
        if 'P' in cell_text:
            race_day['special_marks'].append('P')
        if 'S' in cell_text:
            race_day['special_marks'].append('S')
        
        # 提取奖金信息
        prize_patterns = [
            r'\$[\d,]+',
            r'[\d,]+元'
        ]
        for pattern in prize_patterns:
            matches = re.findall(pattern, cell_text)
            for match in matches:
                if match not in race_day['prize_money']:
                    race_day['prize_money'].append(match)
        
        # 提取班次信息
        class_match = re.search(r'第([一二三四五六七八九十]+)班', cell_text)
        if class_match:
            race_day['race_classes'].append(f"第{class_match.group(1)}班")
        
        # 提取距离信息
        distance_match = re.search(r'(\d+)\s*米', cell_text)
        if distance_match:
            race_day['notes'].append(f"{distance_match.group(1)}米")
        
        # 提取其他文本作为备注
        text_parts = cell_text.split()
        for part in text_parts:
            if part and part not in [str(day), 'C', 'P', 'S'] and not part.isdigit():
                if part not in race_day['notes']:
                    race_day['notes'].append(part)
        
        # 只有在有赛马相关信息时才返回
        if (race_day['venues'] or race_day['race_types'] or 
            race_day['track_types'] or race_day['race_classes'] or
            race_day['special_marks']):
            return race_day
        
        return None
    
    def _convert_chinese_month(self, month_str: str) -> Optional[int]:
        """将中文月份转换为数字"""
        month_map = {
            '一月': 1, '二月': 2, '三月': 3, '四月': 4,
            '五月': 5, '六月': 6, '七月': 7, '八月': 8,
            '九月': 9, '十月': 10, '十一月': 11, '十二月': 12
        }
        return month_map.get(month_str)
    
    def _convert_chinese_year(self, year_str: str) -> Optional[str]:
        """将中文年份转换为数字年份"""
        # 提取数字部分
        num_match = re.search(r'(\d{4})', year_str)
        if num_match:
            return num_match.group(1)
        
        # 处理中文数字年份（简化处理）
        # 例如：二0二六年 -> 2026
        chinese_digits = {
            '0': '0', '一': '1', '二': '2', '三': '3', '四': '4',
            '五': '5', '六': '6', '七': '7', '八': '8', '九': '9'
        }
        
        digits = []
        for char in year_str:
            if char in chinese_digits:
                digits.append(chinese_digits[char])
            elif char.isdigit():
                digits.append(char)
        
        if len(digits) >= 4:
            return ''.join(digits[:4])
        
        return None
    
    def get_race_days_by_month(self, schedule_data: Dict, month: str) -> List[Dict]:
        """
        根据月份筛选赛马日
        
        Args:
            schedule_data: scrape_schedule返回的数据
            month: 月份（如"一月"、"二月"等）
            
        Returns:
            该月的所有赛马日列表
        """
        race_days = schedule_data.get('race_days', [])
        return [day for day in race_days if day.get('month') == month]
    
    def get_race_days_by_venue(self, schedule_data: Dict, venue: str) -> List[Dict]:
        """
        根据场地筛选赛马日
        
        Args:
            schedule_data: scrape_schedule返回的数据
            venue: 场地（"跑马地"或"沙田"）
            
        Returns:
            该场地的所有赛马日列表
        """
        race_days = schedule_data.get('race_days', [])
        return [day for day in race_days if venue in day.get('venues', [])]
    
    def save_to_json(self, data: Dict, filename: str):
        """保存数据到JSON文件"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"数据已保存到: {filename}")
    
    def save_to_csv(self, data: Dict, filename: str):
        """保存赛程数据到CSV文件"""
        import csv
        
        race_days = data.get('race_days', [])
        if not race_days:
            print("没有赛程数据可保存")
            return
        
        # 确定所有可能的字段
        fieldnames = ['date', 'day', 'month', 'year', 'venues', 'race_types', 
                     'track_types', 'race_classes', 'special_marks', 'prize_money', 'notes']
        
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for day in race_days:
                row = {
                    'date': day.get('date', ''),
                    'day': day.get('day', ''),
                    'month': day.get('month', ''),
                    'year': day.get('year', ''),
                    'venues': ', '.join(day.get('venues', [])),
                    'race_types': ', '.join(day.get('race_types', [])),
                    'track_types': ', '.join(day.get('track_types', [])),
                    'race_classes': ', '.join(day.get('race_classes', [])),
                    'special_marks': ', '.join(day.get('special_marks', [])),
                    'prize_money': ', '.join(day.get('prize_money', [])),
                    'notes': ', '.join(day.get('notes', []))
                }
                writer.writerow(row)
        
        print(f"赛程数据已保存到: {filename}")


def main():
    """主函数"""
    scraper = RaceScheduleScraper()
    
    # 默认URL
    url = "https://racing.hkjc.com/zh-hk/local/information/fixture?b_cid=SPLDSPA_hkjc-home_MegaMenu"
    
    print(f"正在爬取赛程表: {url}")
    result = scraper.scrape_schedule(url)
    
    if result:
        # 保存为JSON
        scraper.save_to_json(result, 'race_schedule.json')
        
        # 保存为CSV
        scraper.save_to_csv(result, 'race_schedule.csv')
        
        # 打印摘要信息
        print("\n=== 爬取摘要 ===")
        print(f"月份数量: {len(result.get('months', []))}")
        print(f"赛马日数量: {len(result.get('race_days', []))}")
        print(f"通知数量: {len(result.get('notices', []))}")
        
        # 显示前几个赛马日
        race_days = result.get('race_days', [])
        if race_days:
            print("\n前5个赛马日:")
            for i, day in enumerate(race_days[:5], 1):
                print(f"  {i}. {day.get('date', 'N/A')} - {', '.join(day.get('venues', []))}")
    else:
        print("爬取失败")


if __name__ == '__main__':
    main()

