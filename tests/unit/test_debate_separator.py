#!/usr/bin/env python3
"""
测试辩论历史分隔符修复
验证不可见字符作为分隔符比换行符更可靠
"""

from tradingagents.agents.utils.debate_separator import (
    DEBATE_RESPONSE_SEPARATOR,
    split_debate_responses,
    join_debate_responses
)

def test_separator_with_newlines():
    """测试分隔符处理包含换行符的文本"""
    
    print("=" * 70)
    print("测试1: 处理包含换行符的argument")
    print("=" * 70)
    
    # 模拟包含换行符的argument
    bull_arg_1 = """Bull Analyst: 我们看好这只股票的理由是：
1. 收益增长强劲
   - Q3增长 +15%
   - Q4预计 +20%
2. 市场前景广阔"""
    
    bull_arg_2 = """Bull Analyst: 对Bear的回应：
- 我们的估值合理
- 竞争优势明显
  - 技术领先
  - 品牌强势"""
    
    # 使用不可见字符连接
    combined = bull_arg_1 + DEBATE_RESPONSE_SEPARATOR + bull_arg_2
    
    print("\n原始argument 1:")
    print(repr(bull_arg_1[:50]))
    print("...")
    
    print("\n原始argument 2:")
    print(repr(bull_arg_2[:50]))
    print("...")
    
    print(f"\n连接符: {repr(DEBATE_RESPONSE_SEPARATOR)}")
    print(f"连接符是否为换行符: {DEBATE_RESPONSE_SEPARATOR == chr(10)}")
    
    # 分割
    separated = split_debate_responses(combined)
    
    print(f"\n分割后得到 {len(separated)} 条回复")
    
    # 验证
    assert len(separated) == 2, f"应该得到2条回复，实际得到{len(separated)}"
    assert separated[0] == bull_arg_1, "第1条回复不匹配"
    assert separated[1] == bull_arg_2, "第2条回复不匹配"
    
    print("✓ 分割正确！")
    print("\n第1条回复恢复正确:")
    print(repr(separated[0][:50]))
    print(f"... (共 {len(separated[0])} 字符)")
    
    print("\n第2条回复恢复正确:")
    print(repr(separated[1][:50]))
    print(f"... (共 {len(separated[1])} 字符)")


def test_compare_with_newline():
    """对比新分隔符与旧的换行符方案"""
    
    print("\n" + "=" * 70)
    print("测试2: 与旧方案（换行符）对比")
    print("=" * 70)
    
    bear_arg_1 = """Bear Analyst: 风险分析：
- 高估值问题
  * P/E 比率过高
  * 相对同行溢价30%
- 宏观环境恶化"""
    
    bear_arg_2 = """Bear Analyst: 反驳Bull的理由：
- 收益增长难以持续
- 竞争对手在追赶"""
    
    # 旧方案：使用换行符
    print("\n【旧方案】使用换行符 '\\n' 连接:")
    old_combined = bear_arg_1 + "\n" + bear_arg_2
    old_separated = old_combined.split("\n")
    
    print(f"  分割后得到 {len(old_separated)} 条项目")
    print(f"  问题：argument内部的换行符被当作分隔符了！")
    for i, item in enumerate(old_separated, 1):
        if item:  # 跳过空行
            print(f"    第{i}项: {repr(item[:30])}... ({len(item)} 字符)")
    
    # 新方案：使用不可见字符
    print("\n【新方案】使用不可见字符 '\\x1e' 连接:")
    new_combined = bear_arg_1 + DEBATE_RESPONSE_SEPARATOR + bear_arg_2
    new_separated = split_debate_responses(new_combined)
    
    print(f"  分割后得到 {len(new_separated)} 条回复")
    print(f"  ✓ 正确！argument内部的换行符被保留了")
    for i, item in enumerate(new_separated, 1):
        print(f"    第{i}条: {repr(item[:30])}... ({len(item)} 字符)")
    
    assert len(new_separated) == 2, f"新方案应得2条，实际{len(new_separated)}"
    assert "\n" in new_separated[0], "第1条应保留内部换行符"
    assert "\n" in new_separated[1], "第2条应保留内部换行符"
    
    print("\n✓ 新方案完全正确！")


def test_empty_and_edge_cases():
    """测试边界情况"""
    
    print("\n" + "=" * 70)
    print("测试3: 边界情况")
    print("=" * 70)
    
    # 测试1：空字符串
    print("\n【空字符串】")
    result = split_debate_responses("")
    print(f"  split_debate_responses('') = {result}")
    assert result == [], "空字符串应返回空列表"
    print("  ✓ 正确")
    
    # 测试2：单条回复（无分隔符）
    print("\n【单条回复】")
    single = "Bull Analyst: 第一条意见"
    result = split_debate_responses(single)
    print(f"  分割结果: {len(result)} 条")
    assert len(result) == 1, "单条应返回1条"
    assert result[0] == single, "内容应完全保留"
    print("  ✓ 正确")
    
    # 测试3：多条回复
    print("\n【多条回复】")
    responses = [
        "Bull Analyst: 第一条",
        "Bear Analyst: 第二条",
        "Bull Analyst: 第三条",
        "Bear Analyst: 第四条"
    ]
    combined = join_debate_responses(responses)
    result = split_debate_responses(combined)
    print(f"  输入: {len(responses)} 条")
    print(f"  输出: {len(result)} 条")
    assert len(result) == len(responses), "条数应相同"
    for i, (orig, rec) in enumerate(zip(responses, result), 1):
        assert orig == rec, f"第{i}条不匹配"
    print("  ✓ 正确")
    
    # 测试4：包含特殊字符
    print("\n【特殊字符】")
    special = "Bull Analyst: 价格 $100, 收益 +50%, 评分 ★★★★★"
    result = split_debate_responses(special)
    assert result[0] == special, "特殊字符应正确保留"
    print(f"  {repr(special)}")
    print("  ✓ 特殊字符正确")


def demo_real_world_scenario():
    """展示真实场景的改进"""
    
    print("\n" + "=" * 70)
    print("演示: 真实交易场景")
    print("=" * 70)
    
    # 模拟真实的debate历史
    debate_history = ""
    
    # Bull第一轮
    bull_1 = """Bull Analyst: AAPL看涨的主要原因：
1. 服务业务强劲增长
   - App Store 交易额增加
   - iCloud 订阅用户增长
2. iPhone 销量稳定
3. 估值合理"""
    
    debate_history += bull_1 + DEBATE_RESPONSE_SEPARATOR
    
    # Bear第一轮
    bear_1 = """Bear Analyst: 但是存在以下风险：
1. 中国市场风险
   - 监管压力增加
   - 本地竞争加剧
2. 利润率压力
   - 竞争压低价格
   - 成本上升
3. 宏观经济衰退风险"""
    
    debate_history += bear_1 + DEBATE_RESPONSE_SEPARATOR
    
    # Bull第二轮
    bull_2 = """Bull Analyst: 对Bear观点的回应：
- 中国问题已反映在估值中
- 服务业务利润率更高（70%）
- 现金充足，能渡过经济周期"""
    
    debate_history += bull_2
    
    # 分割
    print("\n完整辩论历史（分隔符为 \\x1e）:")
    print(f"总长度: {len(debate_history)} 字符")
    
    responses = split_debate_responses(debate_history)
    
    print(f"\n分割结果: {len(responses)} 条回复")
    for i, resp in enumerate(responses, 1):
        lines = resp.count('\n') + 1
        print(f"\n【回复 {i}】({len(resp)} 字符, {lines} 行)")
        print(resp[:100] + ("..." if len(resp) > 100 else ""))
    
    # 验证
    assert len(responses) == 3, "应有3条回复"
    assert "服务业务" in responses[0], "第1条Bull应包含'服务业务'"
    assert "中国市场风险" in responses[1], "第1条Bear应包含'中国市场风险'"
    assert "现金充足" in responses[2], "第2条Bull应包含'现金充足'"
    
    print("\n✓ 真实场景测试通过！")


if __name__ == "__main__":
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "辩论历史分隔符修复 - 测试套件" + " " * 20 + "║")
    print("╚" + "═" * 68 + "╝")
    
    try:
        test_separator_with_newlines()
        test_compare_with_newline()
        test_empty_and_edge_cases()
        demo_real_world_scenario()
        
        print("\n" + "=" * 70)
        print("✓ 所有测试通过！")
        print("=" * 70)
        print("\n修复总结:")
        print("- ✅ 使用ASCII 30 (\\x1e) 不可见字符作为分隔符")
        print("- ✅ 保留argument内部的所有换行符和特殊字符")
        print("- ✅ 不会与正常文本冲突")
        print("- ✅ JSON序列化/反序列化完全兼容")
        print("\n文件修改:")
        print("- tradingagents/agents/utils/debate_separator.py (新建)")
        print("- tradingagents/agents/researchers/bull_researcher.py")
        print("- tradingagents/agents/researchers/bear_researcher.py")
        print("- cli/main.py")
        print("\n" + "=" * 70 + "\n")
        
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
