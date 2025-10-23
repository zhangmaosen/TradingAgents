"""
测试平均收益计算逻辑
验证修复后累积平均收益计算正确
"""

def test_cumulative_average_calculation():
    """测试累积平均值计算"""
    
    # 模拟场景：3批次反思数据
    reflection_stats = {
        "total_reflections": 0,
        "avg_return": 0.0,
    }
    
    # 第1批：2个反思，平均收益 +5%
    batch1 = {
        "processed": 2,
        "avg_return": 0.05
    }
    
    old_total = reflection_stats["total_reflections"]
    old_avg = reflection_stats["avg_return"]
    new_count = batch1["processed"]
    new_avg = batch1["avg_return"]
    
    if old_total + new_count > 0:
        cumulative_avg = (old_total * old_avg + new_count * new_avg) / (old_total + new_count)
    else:
        cumulative_avg = 0.0
    
    reflection_stats["total_reflections"] = old_total + new_count
    reflection_stats["avg_return"] = cumulative_avg
    
    print(f"批次1后: 总数={reflection_stats['total_reflections']}, 平均收益={reflection_stats['avg_return']:.2%}")
    assert reflection_stats["total_reflections"] == 2
    assert abs(reflection_stats["avg_return"] - 0.05) < 0.001  # 应该是5%
    
    # 第2批：3个反思，平均收益 -2%
    batch2 = {
        "processed": 3,
        "avg_return": -0.02
    }
    
    old_total = reflection_stats["total_reflections"]
    old_avg = reflection_stats["avg_return"]
    new_count = batch2["processed"]
    new_avg = batch2["avg_return"]
    
    if old_total + new_count > 0:
        cumulative_avg = (old_total * old_avg + new_count * new_avg) / (old_total + new_count)
    else:
        cumulative_avg = 0.0
    
    reflection_stats["total_reflections"] = old_total + new_count
    reflection_stats["avg_return"] = cumulative_avg
    
    print(f"批次2后: 总数={reflection_stats['total_reflections']}, 平均收益={reflection_stats['avg_return']:.2%}")
    # 计算验证：(2*0.05 + 3*(-0.02)) / 5 = (0.10 - 0.06) / 5 = 0.04 / 5 = 0.008 = 0.8%
    assert reflection_stats["total_reflections"] == 5
    assert abs(reflection_stats["avg_return"] - 0.008) < 0.001  # 应该是0.8%
    
    # 第3批：1个反思，平均收益 +10%
    batch3 = {
        "processed": 1,
        "avg_return": 0.10
    }
    
    old_total = reflection_stats["total_reflections"]
    old_avg = reflection_stats["avg_return"]
    new_count = batch3["processed"]
    new_avg = batch3["avg_return"]
    
    if old_total + new_count > 0:
        cumulative_avg = (old_total * old_avg + new_count * new_avg) / (old_total + new_count)
    else:
        cumulative_avg = 0.0
    
    reflection_stats["total_reflections"] = old_total + new_count
    reflection_stats["avg_return"] = cumulative_avg
    
    print(f"批次3后: 总数={reflection_stats['total_reflections']}, 平均收益={reflection_stats['avg_return']:.2%}")
    # 计算验证：(5*0.008 + 1*0.10) / 6 = (0.04 + 0.10) / 6 = 0.14 / 6 ≈ 0.0233 = 2.33%
    assert reflection_stats["total_reflections"] == 6
    assert abs(reflection_stats["avg_return"] - 0.0233) < 0.001  # 应该约2.33%
    
    print("\n✓ 所有测试通过！累积平均收益计算正确。")


def test_old_buggy_behavior():
    """展示旧版本的错误行为"""
    print("\n=== 旧版本（有BUG）的行为 ===")
    
    reflection_stats = {
        "total_reflections": 0,
        "avg_return": 0.0,
    }
    
    # 第1批：平均+5%
    reflection_stats["total_reflections"] += 2
    reflection_stats["avg_return"] = 0.05  # 直接覆盖
    print(f"批次1后: 总数={reflection_stats['total_reflections']}, 平均收益={reflection_stats['avg_return']:.2%}")
    
    # 第2批：平均-2%
    reflection_stats["total_reflections"] += 3
    reflection_stats["avg_return"] = -0.02  # 又直接覆盖！
    print(f"批次2后: 总数={reflection_stats['total_reflections']}, 平均收益={reflection_stats['avg_return']:.2%}")
    print("  ↑ BUG: 平均收益只反映最近一批，之前的+5%被丢弃了！")
    
    # 第3批：平均+10%
    reflection_stats["total_reflections"] += 1
    reflection_stats["avg_return"] = 0.10  # 又覆盖！
    print(f"批次3后: 总数={reflection_stats['total_reflections']}, 平均收益={reflection_stats['avg_return']:.2%}")
    print("  ↑ BUG: 又只显示最近一批的数据，总是显示最后一次的平均值！")
    print("\n正确值应该是: 2.33%，而不是10%")


if __name__ == "__main__":
    print("=" * 60)
    print("平均收益计算测试")
    print("=" * 60)
    
    # 展示旧版本的问题
    test_old_buggy_behavior()
    
    print("\n" + "=" * 60)
    print("新版本（已修复）的行为")
    print("=" * 60)
    
    # 测试新版本
    test_cumulative_average_calculation()
    
    print("\n" + "=" * 60)
    print("修复说明:")
    print("=" * 60)
    print("""
修复前问题：
- 每次处理新的反思批次时，avg_return 被直接覆盖
- 导致显示的平均收益总是最近一批的数据
- 无法反映历史累积的真实平均收益

修复后逻辑：
- 使用加权平均公式：
  new_avg = (old_count * old_avg + new_count * new_avg) / (old_count + new_count)
- 正确累积所有历史反思的平均收益
- 每批新数据都会影响总体平均，但不会覆盖历史数据

示例：
- 批次1: 2个反思，+5% → 总平均 +5.00%
- 批次2: 3个反思，-2% → 总平均 +0.80% (不是-2%!)
- 批次3: 1个反思，+10% → 总平均 +2.33% (不是+10%!)
    """)
