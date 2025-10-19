# TradingAgents 测试套件

本目录包含 TradingAgents 项目的所有测试文件。

## 目录结构

```
tests/
├── __init__.py           # 测试套件入口
├── README.md             # 本文件
├── unit/                 # 单元测试
│   ├── test_fundamentals.py      # 基本面数据测试
│   ├── test_glm_embedding.py     # GLM嵌入模型测试
│   └── test_chromadb.py          # ChromaDB向量数据库测试
├── integration/          # 集成测试
│   ├── test_backtesting.py              # 回测功能测试
│   ├── test_backtest_fix.py             # 回测修复验证测试
│   └── test_reflection_improvements.py  # 反思机制改进测试
└── ui/                   # UI/界面测试
    ├── test_reflection_layout.py   # 反思布局动态测试
    └── test_reflection_static.py   # 反思布局静态测试
```

## 测试分类

### 单元测试 (`unit/`)
测试单个模块、类或函数的功能，不依赖外部系统。

**文件说明：**
- `test_fundamentals.py`: 测试基本面数据获取和处理功能
- `test_glm_embedding.py`: 测试GLM嵌入模型的初始化和向量化功能
- `test_chromadb.py`: 测试ChromaDB向量数据库的存储和检索功能

**运行方式：**
```bash
# 运行所有单元测试
python -m pytest tests/unit/

# 运行特定测试
python -m pytest tests/unit/test_fundamentals.py
```

### 集成测试 (`integration/`)
测试多个组件的交互和整体功能，可能涉及数据流和状态管理。

**文件说明：**
- `test_backtesting.py`: 测试完整的回测流程
- `test_backtest_fix.py`: 验证回测PnL计算修复（包含6个测试用例）
  - 测试买入成本跟踪
  - 测试卖出盈亏计算
  - 测试多次交易的平均成本
  - 测试未实现盈亏
  - 测试完整交易序列
  - 测试最大回撤计算
- `test_reflection_improvements.py`: 测试反思机制的改进（包含4个测试用例）
  - 测试延迟反思队列管理
  - 测试基于未来数据的反思
  - 测试分层记忆系统
  - 测试HOLD决策的反思

**运行方式：**
```bash
# 运行所有集成测试
python -m pytest tests/integration/

# 运行特定测试文件
python tests/integration/test_backtest_fix.py
```

### UI测试 (`ui/`)
测试用户界面的显示和交互功能。

**文件说明：**
- `test_reflection_layout.py`: 动态测试反思布局（运行30秒，每5秒添加新反思）
- `test_reflection_static.py`: 静态快照测试反思布局（显示单次渲染）

**运行方式：**
```bash
# 运行静态UI测试
python tests/ui/test_reflection_static.py

# 运行动态UI测试（10秒超时）
timeout 10 python tests/ui/test_reflection_layout.py
```

## 运行所有测试

```bash
# 使用pytest运行所有测试
python -m pytest tests/

# 运行并显示详细输出
python -m pytest tests/ -v

# 运行并显示覆盖率
python -m pytest tests/ --cov=tradingagents --cov-report=html
```

## 单独运行测试文件

大多数测试文件可以直接运行：

```bash
# 单元测试
python tests/unit/test_fundamentals.py
python tests/unit/test_glm_embedding.py
python tests/unit/test_chromadb.py

# 集成测试
python tests/integration/test_backtesting.py
python tests/integration/test_backtest_fix.py
python tests/integration/test_reflection_improvements.py

# UI测试
python tests/ui/test_reflection_static.py
timeout 10 python tests/ui/test_reflection_layout.py
```

## 测试开发指南

### 添加新测试

1. **单元测试**：测试单个函数或类
   - 放在 `tests/unit/`
   - 文件命名：`test_<module_name>.py`
   - 不应该依赖外部API或数据库

2. **集成测试**：测试多个组件交互
   - 放在 `tests/integration/`
   - 可以使用mock数据或测试数据库
   - 测试完整的工作流程

3. **UI测试**：测试界面显示
   - 放在 `tests/ui/`
   - 使用Rich库验证布局和显示

### 测试命名规范

- 测试文件：`test_<feature>.py`
- 测试类：`Test<Feature>`
- 测试函数：`test_<specific_behavior>`

### 示例测试结构

```python
import pytest
from tradingagents.some_module import SomeClass

class TestSomeClass:
    """测试SomeClass的功能"""
    
    def setup_method(self):
        """每个测试前的准备"""
        self.instance = SomeClass()
    
    def test_basic_functionality(self):
        """测试基本功能"""
        result = self.instance.some_method()
        assert result == expected_value
    
    def test_edge_case(self):
        """测试边界情况"""
        with pytest.raises(ValueError):
            self.instance.some_method(invalid_input)
```

## 持续集成

测试应该在以下情况下运行：
- 每次提交代码前
- Pull Request 创建时
- 合并到主分支前

## 相关文档

- [反思流程分析](../docs/reflection_flow_analysis.md)
- [反思布局改进](../docs/reflection_layout_changes.md)
- [回测修复文档](../docs/backtest_fix.md)

## 贡献

添加新功能时，请确保：
1. ✅ 编写相应的测试
2. ✅ 所有现有测试通过
3. ✅ 测试覆盖率不降低
4. ✅ 更新本 README（如果添加新测试文件）

## 问题反馈

如果测试失败或有问题，请：
1. 检查测试日志输出
2. 确认依赖包已正确安装
3. 查看相关文档
4. 提交 Issue 并附上详细信息
