"""
对话历史分隔符定义
用于分隔Bull/Bear Analyst的多个回复

使用ASCII 30 (Record Separator - RS) 作为分隔符，好处：
- 不会在正常文本中出现
- 不会与换行符冲突
- 在JSON中可以正确保存和恢复
- 易于在UI中分割显示
"""

# ASCII 30 - Record Separator (不可见字符)
DEBATE_RESPONSE_SEPARATOR = '\x1e'

def join_debate_responses(responses):
    """使用不可见字符连接多个回复"""
    return DEBATE_RESPONSE_SEPARATOR.join(responses)

def split_debate_responses(history):
    """使用不可见字符分割回复"""
    if not history:
        return []
    return history.split(DEBATE_RESPONSE_SEPARATOR)

# 备选方案（如果需要可见的分隔符）
# 使用特殊标记 || 或 ||| 等，但容易冲突
# DEBATE_RESPONSE_SEPARATOR_FALLBACK = ' ||| '
