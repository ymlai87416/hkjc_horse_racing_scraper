# 测试说明

## 运行测试

### 本地运行

1. 安装测试依赖：
```bash
pip install -r requirements.txt
```

2. 运行所有测试：
```bash
pytest test_hkjc_scraper.py -v
```

3. 运行特定测试：
```bash
pytest test_hkjc_scraper.py::TestHKJCScraper::test_scraper_initialization -v
```

4. 运行测试并生成覆盖率报告：
```bash
pytest test_hkjc_scraper.py --cov=hkjc_scraper --cov-report=html
```

### CI/CD

测试会在以下情况自动运行：
- 提交PR到 main/master/develop 分支
- 推送到 main/master/develop 分支

GitHub Actions 会在多个Python版本（3.9, 3.10, 3.11, 3.12）上运行测试。

## 测试覆盖

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

