#!/usr/bin/env python3
"""
可视化展示平均收益计算BUG修复前后的差异
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch

def plot_bug_fix_comparison():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # 数据
    batches = [1, 2, 3]
    batch_returns = [5.0, -2.0, 10.0]  # 每批次的平均收益
    batch_counts = [2, 3, 1]
    
    # 修复前（错误）：直接覆盖
    wrong_cumulative = [5.0, -2.0, 10.0]
    
    # 修复后（正确）：加权平均
    correct_cumulative = []
    total_count = 0
    total_sum = 0.0
    for i, (count, ret) in enumerate(zip(batch_counts, batch_returns)):
        total_sum += count * ret
        total_count += count
        correct_cumulative.append(total_sum / total_count)
    
    # === 左图：修复前（错误） ===
    ax1.set_title('修复前 - 错误行为\n(每次直接覆盖)', fontsize=14, fontweight='bold', color='red')
    ax1.set_xlabel('批次', fontsize=12)
    ax1.set_ylabel('显示的平均收益 (%)', fontsize=12)
    ax1.grid(True, alpha=0.3)
    
    # 批次平均（灰色虚线）
    ax1.plot(batches, batch_returns, 'o--', color='gray', alpha=0.5, 
             label='各批次平均', linewidth=2, markersize=8)
    
    # 错误的累积（红色实线）
    ax1.plot(batches, wrong_cumulative, 'o-', color='red', 
             label='显示值（错误）', linewidth=3, markersize=10)
    
    # 正确的累积（绿色虚线作为对比）
    ax1.plot(batches, correct_cumulative, 's--', color='green', alpha=0.5,
             label='正确值（被忽略）', linewidth=2, markersize=8)
    
    # 标注差异
    for i, (wrong, correct) in enumerate(zip(wrong_cumulative, correct_cumulative)):
        if i > 0:  # 从第2批开始有差异
            diff = wrong - correct
            ax1.annotate(f'误差: {diff:+.1f}%', 
                        xy=(batches[i], wrong),
                        xytext=(batches[i] + 0.15, wrong + 1.5),
                        fontsize=10, color='red',
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7),
                        arrowprops=dict(arrowstyle='->', color='red', lw=1.5))
    
    ax1.legend(loc='upper left', fontsize=10)
    ax1.set_xticks(batches)
    ax1.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    
    # === 右图：修复后（正确） ===
    ax2.set_title('修复后 - 正确行为\n(加权平均累积)', fontsize=14, fontweight='bold', color='green')
    ax2.set_xlabel('批次', fontsize=12)
    ax2.set_ylabel('显示的平均收益 (%)', fontsize=12)
    ax2.grid(True, alpha=0.3)
    
    # 批次平均（灰色虚线）
    ax2.plot(batches, batch_returns, 'o--', color='gray', alpha=0.5,
             label='各批次平均', linewidth=2, markersize=8)
    
    # 正确的累积（绿色实线）
    ax2.plot(batches, correct_cumulative, 'o-', color='green',
             label='显示值（正确）', linewidth=3, markersize=10)
    
    # 标注计算过程
    annotations = [
        (1, correct_cumulative[0], f'{correct_cumulative[0]:.1f}%\n(2个反思)'),
        (2, correct_cumulative[1], f'{correct_cumulative[1]:.1f}%\n(2+3=5个反思)'),
        (3, correct_cumulative[2], f'{correct_cumulative[2]:.1f}%\n(5+1=6个反思)')
    ]
    
    for batch, value, text in annotations:
        ax2.annotate(text,
                    xy=(batch, value),
                    xytext=(batch + 0.15, value - 1.5),
                    fontsize=9, color='darkgreen',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgreen', alpha=0.7),
                    arrowprops=dict(arrowstyle='->', color='green', lw=1.5))
    
    ax2.legend(loc='upper left', fontsize=10)
    ax2.set_xticks(batches)
    ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    
    # 整体标题
    fig.suptitle('平均收益计算BUG修复对比\n' + 
                 '批次1: 2个反思(+5%) | 批次2: 3个反思(-2%) | 批次3: 1个反思(+10%)',
                 fontsize=16, fontweight='bold', y=0.98)
    
    plt.tight_layout()
    
    # 保存图表
    output_path = '/home/maosen/dev/TradingAgents/docs/avg_return_fix_comparison.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"✓ 图表已保存到: {output_path}")
    
    # 显示图表（如果在图形环境中）
    try:
        plt.show()
    except:
        pass


def plot_formula_explanation():
    """绘制加权平均公式说明图"""
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.axis('off')
    
    # 标题
    title_text = "加权平均公式详解"
    ax.text(0.5, 0.95, title_text, ha='center', va='top', 
            fontsize=20, fontweight='bold', transform=ax.transAxes)
    
    # 公式
    formula_text = r'$\bar{x}_{累积} = \frac{n_1 \cdot \bar{x}_1 + n_2 \cdot \bar{x}_2}{n_1 + n_2}$'
    ax.text(0.5, 0.85, formula_text, ha='center', va='top',
            fontsize=24, transform=ax.transAxes,
            bbox=dict(boxstyle='round,pad=1', facecolor='lightblue', alpha=0.8))
    
    # 说明
    explanation = """
    其中：
    • n₁ = 已有反思数量
    • x̄₁ = 已有平均收益
    • n₂ = 新增反思数量
    • x̄₂ = 新增平均收益
    """
    ax.text(0.5, 0.70, explanation, ha='center', va='top',
            fontsize=14, transform=ax.transAxes, family='monospace',
            bbox=dict(boxstyle='round,pad=0.8', facecolor='lightyellow', alpha=0.7))
    
    # 示例计算
    example_title = "示例：批次2后的计算"
    ax.text(0.5, 0.48, example_title, ha='center', va='top',
            fontsize=16, fontweight='bold', transform=ax.transAxes)
    
    steps = [
        "已有：n₁ = 2个反思，x̄₁ = +5.00%",
        "新增：n₂ = 3个反思，x̄₂ = -2.00%",
        "",
        "计算：x̄累积 = (2 × 5.00 + 3 × (-2.00)) / (2 + 3)",
        "           = (10.00 - 6.00) / 5",
        "           = 4.00 / 5",
        "           = 0.80%  ✓",
        "",
        "如果直接覆盖：x̄ = -2.00%  ✗（错误！）"
    ]
    
    step_y = 0.40
    for step in steps:
        color = 'green' if '✓' in step else 'red' if '✗' in step else 'black'
        weight = 'bold' if '✓' in step or '✗' in step else 'normal'
        ax.text(0.5, step_y, step, ha='center', va='top',
                fontsize=12, transform=ax.transAxes, family='monospace',
                color=color, weight=weight)
        step_y -= 0.05
    
    # 结论框
    conclusion = "结论：必须使用加权平均，不能直接覆盖！"
    ax.text(0.5, 0.05, conclusion, ha='center', va='bottom',
            fontsize=14, fontweight='bold', color='darkgreen',
            transform=ax.transAxes,
            bbox=dict(boxstyle='round,pad=0.8', facecolor='lightgreen', 
                     edgecolor='darkgreen', linewidth=2))
    
    plt.tight_layout()
    
    # 保存
    output_path = '/home/maosen/dev/TradingAgents/docs/avg_return_formula.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"✓ 公式说明图已保存到: {output_path}")
    
    try:
        plt.show()
    except:
        pass


if __name__ == "__main__":
    print("=" * 60)
    print("生成平均收益计算BUG修复可视化")
    print("=" * 60)
    
    # 设置中文字体
    plt.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    
    print("\n生成对比图...")
    plot_bug_fix_comparison()
    
    print("\n生成公式说明图...")
    plot_formula_explanation()
    
    print("\n" + "=" * 60)
    print("完成！生成的图表：")
    print("  1. docs/avg_return_fix_comparison.png  (修复前后对比)")
    print("  2. docs/avg_return_formula.png         (加权平均公式)")
    print("=" * 60)
