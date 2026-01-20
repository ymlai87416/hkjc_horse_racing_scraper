# 香港赛马会爬虫使用说明

## 功能说明

这个爬虫可以提取香港赛马会比赛结果页面的所有信息，包括：

1. **比赛基本信息**
   - 比赛日期、场地、场次
   - 距离、班次、时间
   - 赛道信息

2. **参赛马匹信息**
   - 马匹名称和ID
   - 编号、档位
   - 骑师、练马师
   - 体重、评分类信息

3. **比赛结果**
   - 完成名次
   - 完成时间
   - 赔率信息

4. **比赛事件报告**
   - 每匹马在比赛中的表现
   - 意外事件描述

5. **血统信息**
   - 胜出马匹的父系和母系信息

## 安装依赖

```bash
pip install -r requirements.txt
```

或者手动安装：

```bash
pip install requests beautifulsoup4 lxml
```

## 使用方法

### 基本使用

```python
from hkjc_scraper import HKJCScraper

# 创建爬虫实例
scraper = HKJCScraper()

# 爬取指定URL
url = "https://racing.hkjc.com/zh-hk/local/information/localresults?racedate=2026/01/18&Racecourse=ST&RaceNo=3"
result = scraper.scrape_race_result(url)

# 保存为JSON
scraper.save_to_json(result, 'race_result.json')

# 保存马匹数据为CSV
scraper.save_to_csv(result, 'race_horses.csv')
```

### 命令行使用

```bash
python hkjc_scraper.py
```

## URL格式说明

URL格式：
```
https://racing.hkjc.com/zh-hk/local/information/localresults?racedate=YYYY/MM/DD&Racecourse=XX&RaceNo=N
```

参数说明：
- `racedate`: 比赛日期，格式为 YYYY/MM/DD
- `Racecourse`: 场地代码
  - `ST`: 沙田
  - `HV`: 跑马地
- `RaceNo`: 场次编号（1-12）

## 输出格式

### JSON输出结构

```json
{
  "race_date": "2026/01/18",
  "racecourse": "ST",
  "race_no": "3",
  "race_info": {
    "venue": "沙田",
    "distance": "1200米",
    "class": "第五班",
    ...
  },
  "horses": [
    {
      "horse_id": "HK_2025_L155",
      "horse_name": "国千金",
      "number": "1",
      "jockey": "骑师名",
      "trainer": "练马师名",
      ...
    },
    ...
  ],
  "race_result": {
    "finishing_order": [...]
  },
  "incident_reports": [
    {
      "position": "1",
      "horse_number": "1",
      "horse_name": "马名",
      "description": "事件描述"
    },
    ...
  ],
  "pedigree": {
    "horse_id": "...",
    "horse_name": "...",
    "sire": "父系名",
    "dam": "母系名"
  }
}
```

## 注意事项

1. 请遵守网站的robots.txt和使用条款
2. 建议在请求之间添加适当的延迟，避免对服务器造成压力
3. 网站结构可能会变化，如果爬虫失效，需要更新解析逻辑
4. 某些信息可能需要登录才能访问

## 扩展功能

可以根据需要扩展以下功能：

- 批量爬取多场比赛
- 爬取历史比赛数据
- 爬取马匹详细信息页面
- 爬取骑师和练马师信息
- 数据清洗和验证
- 数据库存储

