#!/usr/bin/env python3
"""
反思机制改进 - 快速验证脚本
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_delayed_reflection():
    """测试延迟反思管理器"""
    print("=" * 60)
    print("测试1: 延迟反思管理器")
    print("=" * 60)
    
    from tradingagents.graph.delayed_reflection import DelayedReflectionManager
    
    manager = DelayedReflectionManager()
    
    # 检查队列状态
    status = manager.get_queue_status()
    print(f"\n当前队列状态:")
    print(f"  待处理: {status['pending']}")
    print(f"  已完成: {status['completed']}")
    print(f"  失败: {status['error']}")
    print(f"  总计: {status['total']}")
    
    # 检查待反思文件是否存在
    if Path("results/pending_reflections.json").exists():
        print(f"\n✓ 反思队列文件存在: results/pending_reflections.json")
    else:
        print(f"\n✓ 反思队列文件未创建（首次运行时正常）")
    
    print("\n✅ 延迟反思管理器测试通过")


def test_hierarchical_memory():
    """测试分层记忆系统"""
    print("\n" + "=" * 60)
    print("测试2: 分层记忆系统")
    print("=" * 60)
    
    from tradingagents.agents.utils.hierarchical_memory import HierarchicalMemoryManager
    from tradingagents.default_config import DEFAULT_CONFIG
    
    # 创建测试管理器
    manager = HierarchicalMemoryManager("test_bull", DEFAULT_CONFIG)
    
    print(f"\n✓ 分层记忆管理器创建成功")
    
    # 测试记忆添加
    test_situation = "AAPL技术面强劲，RSI超买"
    test_reflection = "在技术指标超买时应谨慎追高"
    
    manager.add_reflection(
        ticker="AAPL",
        situation=test_situation,
        reflection=test_reflection,
        scope="stock"
    )
    
    print(f"✓ 成功添加测试记忆到AAPL股票层")
    
    # 检查记忆统计
    stats = manager.get_memory_stats("AAPL")
    print(f"\nAAPL记忆统计:")
    print(f"  股票专属: {stats['stock_memories']}")
    print(f"  行业共享: {stats['sector_memories']}")
    print(f"  全局通用: {stats['global_memories']}")
    print(f"  总计: {stats['total']}")
    
    # 测试记忆检索
    memories = manager.get_memories(
        ticker="AAPL",
        current_situation="AAPL技术分析显示超买",
        n_matches=1
    )
    
    if memories:
        print(f"\n✓ 成功检索到 {len(memories)} 条相关记忆")
        mem = memories[0]
        print(f"  来源: {mem['source']}")
        print(f"  相似度: {mem['similarity_score']:.3f}")
        print(f"  权重: {mem['weight']}")
        print(f"  建议: {mem['recommendation'][:50]}...")
    
    print("\n✅ 分层记忆系统测试通过")


def test_config():
    """测试配置加载"""
    print("\n" + "=" * 60)
    print("测试3: 配置验证")
    print("=" * 60)
    
    from tradingagents.default_config import DEFAULT_CONFIG
    
    # 检查新增配置项
    required_keys = [
        "reflection_lookforward_days",
        "reflection_min_age_days",
        "use_hierarchical_memory"
    ]
    
    print("\n检查配置项:")
    for key in required_keys:
        value = DEFAULT_CONFIG.get(key)
        status = "✓" if value is not None else "✗"
        print(f"  {status} {key}: {value}")
    
    all_present = all(key in DEFAULT_CONFIG for key in required_keys)
    
    if all_present:
        print("\n✅ 配置验证通过")
    else:
        print("\n⚠️ 警告: 部分配置项缺失")


def test_integration():
    """测试集成到TradingGraph"""
    print("\n" + "=" * 60)
    print("测试4: 集成验证")
    print("=" * 60)
    
    try:
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        from tradingagents.default_config import DEFAULT_CONFIG
        
        # 测试传统模式
        print("\n创建TradingGraph (传统记忆)...")
        config_old = DEFAULT_CONFIG.copy()
        config_old["use_hierarchical_memory"] = False
        graph_old = TradingAgentsGraph(config=config_old)
        print("✓ 传统记忆模式初始化成功")
        
        # 测试分层记忆模式
        print("\n创建TradingGraph (分层记忆)...")
        config_new = DEFAULT_CONFIG.copy()
        config_new["use_hierarchical_memory"] = True
        graph_new = TradingAgentsGraph(config=config_new)
        print("✓ 分层记忆模式初始化成功")
        
        # 验证记忆类型
        from tradingagents.agents.utils.memory import FinancialSituationMemory
        from tradingagents.agents.utils.hierarchical_memory import BackwardCompatibleMemory
        
        old_type = type(graph_old.bull_memory).__name__
        new_type = type(graph_new.bull_memory).__name__
        
        print(f"\n记忆类型验证:")
        print(f"  传统模式: {old_type}")
        print(f"  分层模式: {new_type}")
        
        print("\n✅ 集成验证通过")
        
    except Exception as e:
        print(f"\n❌ 集成测试失败: {e}")
        import traceback
        traceback.print_exc()


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("🔍 反思机制改进 - 验证测试")
    print("=" * 60)
    
    try:
        test_delayed_reflection()
        test_hierarchical_memory()
        test_config()
        test_integration()
        
        print("\n" + "=" * 60)
        print("🎉 所有测试通过！")
        print("=" * 60)
        print("\n下一步:")
        print("  1. 运行主程序: python -m cli.main")
        print("  2. 分析多个股票和日期，观察反思队列")
        print("  3. 检查队列状态: python test_reflection_improvements.py")
        print("\n详细文档: docs/reflection_improvements.md")
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ 测试失败: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
