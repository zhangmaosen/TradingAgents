#!/usr/bin/env python3
"""
TradingAgents 测试运行器

快速运行各类测试的便捷脚本。
"""
import sys
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """运行命令并显示结果"""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}\n")
    result = subprocess.run(cmd, shell=True)
    return result.returncode

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法：")
        print("  python run_tests.py all          # 运行所有测试")
        print("  python run_tests.py unit         # 运行单元测试")
        print("  python run_tests.py integration  # 运行集成测试")
        print("  python run_tests.py ui           # 运行UI测试")
        print("  python run_tests.py <file>       # 运行特定测试文件")
        sys.exit(1)
    
    test_type = sys.argv[1]
    
    # 切换到项目根目录
    project_root = Path(__file__).parent
    
    if test_type == "all":
        # 运行所有测试
        exit_code = 0
        exit_code |= run_command("python -m pytest tests/unit/ -v", "单元测试")
        exit_code |= run_command("python -m pytest tests/integration/ -v", "集成测试")
        print(f"\n{'='*60}")
        print("📊 UI测试需要手动运行（涉及终端显示）")
        print("   python tests/ui/test_reflection_static.py")
        print("   timeout 10 python tests/ui/test_reflection_layout.py")
        print(f"{'='*60}\n")
        sys.exit(exit_code)
        
    elif test_type == "unit":
        exit_code = run_command("python -m pytest tests/unit/ -v", "单元测试")
        sys.exit(exit_code)
        
    elif test_type == "integration":
        exit_code = run_command("python -m pytest tests/integration/ -v", "集成测试")
        sys.exit(exit_code)
        
    elif test_type == "ui":
        print("\n" + "="*60)
        print("📺 UI测试")
        print("="*60)
        print("\n请手动运行以下命令：")
        print("  python tests/ui/test_reflection_static.py")
        print("  timeout 10 python tests/ui/test_reflection_layout.py")
        print()
        
    else:
        # 运行特定文件
        if Path(test_type).exists():
            exit_code = run_command(f"python {test_type}", f"运行 {test_type}")
            sys.exit(exit_code)
        elif Path(f"tests/{test_type}").exists():
            exit_code = run_command(f"python tests/{test_type}", f"运行 tests/{test_type}")
            sys.exit(exit_code)
        else:
            print(f"❌ 错误：找不到测试文件 '{test_type}'")
            sys.exit(1)

if __name__ == "__main__":
    main()
