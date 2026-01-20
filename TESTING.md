# 测试说明

## 运行测试

### 环境准备

**首次设置（推荐使用虚拟环境）：**

**macOS/Linux:**
```bash
# 使用提供的脚本自动设置
bash setup_venv.sh

# 或手动创建虚拟环境
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

**Windows:**
```bash
# 使用提供的脚本自动设置
setup_venv.bat

# 或手动创建虚拟环境
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**如果虚拟环境已存在，只需激活：**

**macOS/Linux:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

### 本地运行

1. 确保已激活虚拟环境并安装测试依赖：
```bash
pip install -r requirements.txt
```

2. 运行所有测试：
```bash
# 运行所有测试文件
pytest test/ -v

# 或使用相对路径
pytest test/test_race_result_scraper.py test/test_race_schedule_scraper.py -v
```

3. 运行特定爬虫的测试：
```bash
# 运行比赛结果爬虫测试
pytest test/test_race_result_scraper.py -v

# 运行赛程表爬虫测试
pytest test/test_race_schedule_scraper.py -v
```

4. 运行特定测试方法：
```bash
# 比赛结果爬虫测试
pytest test/test_race_result_scraper.py::TestRaceResultScraper::test_scraper_initialization -v

# 赛程表爬虫测试
pytest test/test_race_schedule_scraper.py::TestRaceScheduleScraper::test_scraper_initialization -v
```

5. 运行测试并生成覆盖率报告：
```bash
# 单个爬虫的覆盖率
pytest test/test_race_result_scraper.py --cov=src/hkjc_scrapers/race_result_scraper --cov-report=html
pytest test/test_race_schedule_scraper.py --cov=src/hkjc_scrapers/race_schedule_scraper --cov-report=html

# 整个包的覆盖率
pytest test/ --cov=src/hkjc_scrapers --cov-report=html
```

6. 运行测试并显示详细输出：
```bash
# 显示打印输出
pytest test/ -v -s

# 显示更详细的输出
pytest test/ -vv
```

### CI/CD

测试会在以下情况自动运行：
- 提交PR到 main/master/develop 分支
- 推送到 main/master/develop 分支

GitHub Actions 会在多个Python版本（3.9, 3.10, 3.11, 3.12）上运行测试。

## 测试覆盖

### 比赛结果爬虫 (RaceResultScraper)

当前测试覆盖以下功能：

- ✅ 爬虫初始化
- ✅ URL解析
- ✅ 比赛信息提取
- ✅ 马匹信息提取
- ✅ 事件报告提取
- ✅ 血统信息提取
- ✅ JSON保存功能
- ✅ CSV保存功能
- ✅ 错误处理
- ✅ 返回结果结构验证

### 赛程表爬虫 (RaceScheduleScraper)

当前测试覆盖以下功能：

- ✅ 爬虫初始化
- ✅ URL解析（包括默认URL）
- ✅ 月份提取
- ✅ 图例提取（场地、赛马类型、赛道类型、赛事级别、特殊标记）
- ✅ 通知提取
- ✅ 赛马日提取
- ✅ 日期单元格解析
- ✅ 中文月份转换
- ✅ 中文年份转换
- ✅ 按月份筛选赛马日
- ✅ 按场地筛选赛马日
- ✅ JSON保存功能
- ✅ CSV保存功能
- ✅ 错误处理
- ✅ 返回结果结构验证

## 添加新测试

添加新测试时，请遵循以下规范：

1. 测试类名以 `Test` 开头
2. 测试方法名以 `test_` 开头
3. 使用 `pytest.fixture` 创建测试数据
4. 使用 `unittest.mock` 模拟网络请求
5. 为集成测试添加 `@pytest.mark.integration` 标记

示例：
```python
def test_new_feature(self, scraper):
    """测试新功能"""
    # 测试代码
    assert result is not None
```

## 快速参考

### 常用测试命令

```bash
# 运行所有测试
pytest test/ -v

# 运行特定测试文件
pytest test/test_race_result_scraper.py -v
pytest test/test_race_schedule_scraper.py -v

# 运行特定测试类
pytest test/test_race_result_scraper.py::TestRaceResultScraper -v
pytest test/test_race_schedule_scraper.py::TestRaceScheduleScraper -v

# 运行特定测试方法
pytest test/test_race_schedule_scraper.py::TestRaceScheduleScraper::test_extract_race_days -v

# 只运行失败的测试
pytest test/ --lf

# 运行上次失败的测试并显示详细输出
pytest test/ --lf -vv

# 生成覆盖率报告（HTML格式）
pytest test/ --cov=src/hkjc_scrapers --cov-report=html
# 报告会生成在 htmlcov/ 目录中
```

