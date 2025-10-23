# Earnings Call Transcripts Integration

## 概述

已成功将 Alpha Vantage 的 **Earnings Call Transcript API** 集成到 TradingAgents 系统中。该工具允许获取公司的财报电话会议完整文本记录，包括LLM情感分析。

## 实现细节

### 1. 新增函数

**文件**: `tradingagents/dataflows/alpha_vantage_fundamentals.py`

```python
def get_earning_call_transcripts(ticker: str, quarter: str = None, curr_date: str = None) -> str:
    """
    Retrieve earnings call transcripts for a given ticker symbol using Alpha Vantage.

    Args:
        ticker (str): Ticker symbol of the company (e.g., "IBM", "TSLA")
        quarter (str): Fiscal quarter in YYYYQM format (e.g., "2024Q1", "2024Q2")
                      REQUIRED - no default value
        curr_date (str): Current date you are trading at, yyyy-mm-dd (not used for Alpha Vantage)

    Returns:
        str: Earnings call transcript data with sentiment analysis

    Raises:
        ValueError: If quarter parameter is not provided
    """
```

### 2. 集成点

#### 在 `interface.py` 中的配置:

1. **导入**: 在第 9-18 行导入了 `get_alpha_vantage_earning_call_transcripts`

2. **TOOLS_CATEGORIES**: 添加到 `fundamental_data` 类别
   ```python
   "fundamental_data": {
       "tools": [
           "get_fundamentals",
           "get_balance_sheet",
           "get_cashflow",
           "get_income_statement",
           "get_earning_call_transcripts"  # ← 新增
       ]
   }
   ```

3. **VENDOR_METHODS**: 配置 Alpha Vantage 实现
   ```python
   "get_earning_call_transcripts": {
       "alpha_vantage": get_alpha_vantage_earning_call_transcripts,
   }
   ```

## API 参数

### Alpha Vantage EARNINGS_CALL_TRANSCRIPT API

| 参数 | 类型 | 必需 | 说明 | 示例 |
|------|------|------|------|------|
| `symbol` | String | ✓ | 股票代码 | IBM, TSLA |
| `quarter` | String | ✓ | 财政季度（YYYYQM格式） | 2024Q1, 2024Q2 |

### 历史支持

- 支持自 2010Q1 以来的所有季度

## 使用示例

### 方式 1: 直接调用 (底层)

```python
from tradingagents.dataflows.alpha_vantage_fundamentals import get_earning_call_transcripts

# 获取 IBM 2024年第一季度的财报电话会议
transcript = get_earning_call_transcripts("IBM", "2024Q1")
print(transcript)
```

### 方式 2: 通过 route_to_vendor (推荐)

```python
from tradingagents.dataflows.interface import route_to_vendor

# 通过路由系统获取（支持 fallback 和日志记录）
transcript = route_to_vendor("get_earning_call_transcripts", "TSLA", "2024Q2")
```

### 方式 3: 在 Agent 中集成

在 agent tools 中注册并使用：

```python
from tradingagents.dataflows.interface import route_to_vendor

# 作为 tool 提供给 LLM
tools_list = [
    {
        "name": "get_earning_call_transcripts",
        "description": "Get earnings call transcript with sentiment analysis",
        "function": lambda ticker, quarter: route_to_vendor(
            "get_earning_call_transcripts", ticker, quarter
        )
    }
]
```

## 返回数据格式

API 返回包含以下关键信息的 JSON 结构：

```json
{
    "symbol": "IBM",
    "quarter": "2024Q1",
    "title": "Q1 2024 Earnings Call",
    "date": "2024-04-15",
    "url": "https://...",
    "transcript": "full transcript text...",
    "sentiment": {
        "overall": "positive",
        "score": 0.75
    }
}
```

## 错误处理

### 必需参数错误

```python
try:
    # 缺少必需的 quarter 参数
    transcript = get_earning_call_transcripts("IBM")
except ValueError as e:
    print(f"Error: {e}")
    # Output: quarter parameter is required for earning call transcripts. Format: YYYYQM (e.g., 2024Q1)
```

### API 限制错误

Alpha Vantage 有 API 配额限制。使用 `route_to_vendor` 时，系统会自动处理速率限制：

```python
from tradingagents.dataflows.interface import route_to_vendor
from tradingagents.dataflows.alpha_vantage_common import AlphaVantageRateLimitError

try:
    transcript = route_to_vendor("get_earning_call_transcripts", "IBM", "2024Q1")
except AlphaVantageRateLimitError as e:
    print("Rate limit exceeded, try again later")
```

## 测试结果

所有集成测试通过 ✓

- ✓ 函数实现
- ✓ 模块重新导出
- ✓ 接口配置
- ✓ TOOLS_CATEGORIES 更新
- ✓ VENDOR_METHODS 映射
- ✓ 分类路由

## 相关文件修改

1. `tradingagents/dataflows/alpha_vantage_fundamentals.py` - 新增函数
2. `tradingagents/dataflows/alpha_vantage.py` - 添加导出
3. `tradingagents/dataflows/interface.py` - 配置集成

## 后续扩展建议

1. **多源支持**: 可在未来添加其他数据源的 earnings transcript 实现
2. **缓存机制**: 实现本地缓存以减少 API 调用
3. **处理工具**: 添加 transcript 文本处理和摘要功能
4. **情感分析**: 增强情感分析功能，提取关键指标

