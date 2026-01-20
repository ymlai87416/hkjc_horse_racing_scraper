# 香港赛马会爬虫使用说明

## 功能说明

这个爬虫工具包包含三个独立的爬虫模块，可以提取香港赛马会的各类信息：

### 1. 比赛结果爬虫 (RaceResultScraper)

提取单场比赛的详细信息，包括：

- **比赛基本信息**
  - 比赛日期、场地、场次
  - 距离、班次、时间
  - 赛道信息

- **参赛马匹信息**
  - 马匹名称和ID
  - 编号、档位
  - 骑师、练马师
  - 体重、评分类信息

- **比赛结果**
  - 完成名次
  - 完成时间
  - 赔率信息

- **比赛事件报告**
  - 每匹马在比赛中的表现
  - 意外事件描述

- **血统信息**
  - 胜出马匹的父系和母系信息

### 2. 赛程表爬虫 (RaceScheduleScraper)

提取赛程表信息，包括：

- **月份列表** - 可查询的月份范围
- **赛马日信息**
  - 日期、场地（沙田/跑马地）
  - 赛马类型（日赛/夜赛）
  - 赛道类型
  - 赛事级别
  - 特殊标记
- **重要通知** - 页面上的通知信息
- **图例说明** - 各种标记的说明

### 3. 马匹信息爬虫 (HorseInfoScraper)

提取马匹详细信息，包括：

- **基本信息**
  - 马匹名称、编号、ID
  - 性别、年龄、毛色
  - 练马师、马主
  - 血统信息（父系、母系、外祖父）

- **赛绩记录**
  - 历史比赛记录
  - 日期、场地、距离、班次
  - 名次、骑师、练马师
  - 完成时间、赔率等

- **装备图例** - 马匹装备代码说明

## 环境设置

### 创建虚拟环境（推荐）

**macOS/Linux:**
```bash
# 使用提供的脚本自动设置
bash setup_venv.sh

# 或手动创建
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

**Windows:**
```bash
# 使用提供的脚本自动设置
setup_venv.bat

# 或手动创建
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 激活虚拟环境

**macOS/Linux:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

### 安装依赖

如果已经激活虚拟环境，直接运行：

```bash
pip install -r requirements.txt
```

或者手动安装：

```bash
pip install requests beautifulsoup4 lxml pytest pytest-cov
```

### 退出虚拟环境

```bash
deactivate
```

## 使用方法

### 安装包（可选）

```bash
# 开发模式安装
pip install -e .

# 或直接使用（无需安装）
# 确保 src 目录在 Python 路径中
```

### 基本使用

#### 比赛结果爬虫

```python
from hkjc_scrapers import RaceResultScraper

# 创建爬虫实例
scraper = RaceResultScraper()

# 爬取指定URL
url = "https://racing.hkjc.com/zh-hk/local/information/localresults?racedate=2026/01/18&Racecourse=ST&RaceNo=3"
result = scraper.scrape_race_result(url)

# 保存为JSON
scraper.save_to_json(result, 'race_result.json')

# 保存马匹数据为CSV
scraper.save_to_csv(result, 'race_horses.csv')
```

#### 赛程表爬虫

```python
from hkjc_scrapers import RaceScheduleScraper

# 创建爬虫实例
scraper = RaceScheduleScraper()

# 爬取赛程表（可指定URL或使用默认）
url = "https://racing.hkjc.com/zh-hk/local/information/fixture?calyear=2026&calmonth=01"
result = scraper.scrape_schedule(url)

# 保存为JSON
scraper.save_to_json(result, 'race_schedule.json')

# 保存为CSV
scraper.save_to_csv(result, 'race_schedule.csv')

# 筛选功能
# 按月份筛选
january_days = scraper.get_race_days_by_month(result, '一月')

# 按场地筛选
st_days = scraper.get_race_days_by_venue(result, '沙田')
hv_days = scraper.get_race_days_by_venue(result, '跑马地')
```

#### 马匹信息爬虫

```python
from hkjc_scrapers import HorseInfoScraper

# 创建爬虫实例
scraper = HorseInfoScraper()

# 爬取马匹信息
url = "https://racing.hkjc.com/zh-hk/local/information/horse?horseid=HK_2020_E436&Option=1"
result = scraper.scrape_horse_info(url)

# 保存为JSON
scraper.save_to_json(result, 'horse_info.json')

# 保存赛绩记录为CSV
scraper.save_to_csv(result, 'horse_race_records.csv')
```

### 命令行使用

项目提供了三个示例脚本：

```bash
# 比赛结果示例
python example_race_result.py

# 赛程表示例
python example_schedule.py

# 马匹信息示例
python example_horse_info.py
```

### 项目结构

```
hkjc_horse_racing_scraper/
├── src/
│   └── hkjc_scrapers/          # 爬虫包
│       ├── __init__.py
│       ├── race_result_scraper.py      # 比赛结果爬虫
│       ├── race_schedule_scraper.py    # 赛程表爬虫
│       └── horse_info_scraper.py       # 马匹信息爬虫
├── test/                        # 测试目录
│   ├── __init__.py
│   ├── test_race_result_scraper.py
│   ├── test_race_schedule_scraper.py
│   └── test_horse_info_scraper.py
├── example_race_result.py       # 比赛结果使用示例
├── example_schedule.py          # 赛程表使用示例
├── example_horse_info.py        # 马匹信息使用示例
├── setup.py                     # 包安装配置
├── pytest.ini                   # pytest 配置
├── requirements.txt             # 依赖列表
└── TESTING.md                   # 测试说明文档
```

## URL格式说明

### 1. 比赛结果URL

```
https://racing.hkjc.com/zh-hk/local/information/localresults?racedate=YYYY/MM/DD&Racecourse=XX&RaceNo=N
```

参数说明：
- `racedate`: 比赛日期，格式为 YYYY/MM/DD
- `Racecourse`: 场地代码
  - `ST`: 沙田
  - `HV`: 跑马地
- `RaceNo`: 场次编号（1-12）

示例：
```
https://racing.hkjc.com/zh-hk/local/information/localresults?racedate=2026/01/18&Racecourse=ST&RaceNo=3
```

### 2. 赛程表URL

```
https://racing.hkjc.com/zh-hk/local/information/fixture?calyear=YYYY&calmonth=MM
```

参数说明：
- `calyear`: 年份，格式为 YYYY
- `calmonth`: 月份，格式为 MM（01-12）

也可以使用默认URL（显示当前可查询的所有月份）：
```
https://racing.hkjc.com/zh-hk/local/information/fixture?b_cid=SPLDSPA_hkjc-home_MegaMenu
```

示例：
```
https://racing.hkjc.com/zh-hk/local/information/fixture?calyear=2026&calmonth=01
```

### 3. 马匹信息URL

```
https://racing.hkjc.com/zh-hk/local/information/horse?horseid=XXXXX&Option=1
```

参数说明：
- `horseid`: 马匹ID，格式如 `HK_2020_E436`
- `Option`: 选项，通常为 `1`

示例：
```
https://racing.hkjc.com/zh-hk/local/information/horse?horseid=HK_2020_E436&Option=1
```

## 输出格式

### 1. 比赛结果JSON结构

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

### 2. 赛程表JSON结构

```json
{
  "source_url": "...",
  "scraped_at": "2026-01-18T12:00:00",
  "months": ["一月", "二月", ...],
  "race_days": [
    {
      "date": "2026-01-18",
      "year": "2026",
      "month": "一月",
      "day": "18",
      "venues": ["沙田"],
      "race_types": ["日赛"],
      "track_types": ["草地"],
      "race_classes": ["第一班", "第二班"],
      "special_marks": []
    },
    ...
  ],
  "legend": {
    "venues": {...},
    "race_types": {...},
    "track_types": {...},
    "race_classes": {...},
    "special_marks": [...]
  },
  "notices": ["通知1", "通知2", ...]
}
```

### 3. 马匹信息JSON结构

```json
{
  "horse_id": "HK_2020_E436",
  "source_url": "...",
  "scraped_at": "2026-01-18T12:00:00",
  "basic_info": {
    "horse_name": "马名",
    "horse_code": "E436",
    "sex": "阉",
    "age": "5",
    "colour": "栗",
    "trainer": "练马师名",
    "owner": "马主名",
    "sire": "父系名",
    "dam": "母系名",
    "maternal_grandsire": "外祖父名",
    ...
  },
  "race_records": [
    {
      "date": "2026/01/18",
      "venue": "沙田",
      "distance": "1200米",
      "class": "第五班",
      "position": "1",
      "jockey": "骑师名",
      "trainer": "练马师名",
      ...
    },
    ...
  ],
  "equipment_legend": {
    "B": "绑舌带",
    "V": "眼罩",
    ...
  }
}
```

### CSV输出

所有爬虫都支持将数据保存为CSV格式：
- **比赛结果爬虫**: 保存马匹信息为CSV
- **赛程表爬虫**: 保存赛马日信息为CSV
- **马匹信息爬虫**: 保存赛绩记录为CSV

## 注意事项

1. 请遵守网站的robots.txt和使用条款
2. 建议在请求之间添加适当的延迟，避免对服务器造成压力
3. 网站结构可能会变化，如果爬虫失效，需要更新解析逻辑
4. 某些信息可能需要登录才能访问

## 测试

项目包含完整的测试套件，使用 pytest 运行测试：

```bash
# 运行所有测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=src/hkjc_scrapers --cov-report=html

# 运行特定测试文件
pytest test/test_race_result_scraper.py
pytest test/test_race_schedule_scraper.py
pytest test/test_horse_info_scraper.py
```

详细测试说明请参考 [TESTING.md](TESTING.md)

## 扩展功能

已实现的功能：
- ✅ 比赛结果爬取
- ✅ 赛程表爬取（支持筛选）
- ✅ 马匹信息爬取
- ✅ JSON和CSV格式导出
- ✅ 完整的测试覆盖

可以进一步扩展的功能：
- 批量爬取多场比赛
- 爬取历史比赛数据
- 爬取骑师和练马师信息
- 数据清洗和验证
- 数据库存储
- 数据分析和可视化

