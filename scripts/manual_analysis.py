#!/usr/bin/env python
"""
手动触发分析脚本
用于按需分析特定股票或行业
"""

import sys
import os
import argparse
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.database import DatabaseManager
from orchestrator.agent_orchestrator import AgentOrchestrator
from orchestrator.report_generator import ReportGenerator
from utils.llm_client import LLMClient


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="手动触发AI分析")
    parser.add_argument(
        "--symbols", 
        nargs="+",
        help="指定分析的股票代码，如: 600036.SH 000001.SZ"
    )
    parser.add_argument(
        "--industry", 
        type=int,
        help="指定分析的行业ID"
    )
    parser.add_argument(
        "--output", 
        default="console",
        choices=["console", "file", "both"],
        help="输出方式"
    )
    parser.add_argument(
        "--detail", 
        action="store_true",
        help="输出详细报告"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    
    db_manager = DatabaseManager()
    llm_client = LLMClient()
    orchestrator = AgentOrchestrator(db_manager, llm_client)
    
    # 获取持仓（如果指定了symbols则过滤）
    if args.symbols:
        holdings = [{"symbol": s} for s in args.symbols]
        result = orchestrator.run_analysis(holdings=holdings)
    else:
        result = orchestrator.run_analysis()
    
    # 输出报告
    generator = ReportGenerator()
    
    if args.detail:
        report = generator.generate_detailed_report(result)
    else:
        report = generator.generate_summary_report(result)
    
    if args.output in ["console", "both"]:
        print("\n" + "=" * 60)
        print(report)
        print("=" * 60)
    
    if args.output in ["file", "both"]:
        filename = f"manual_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(f"reports/{filename}", "w") as f:
            f.write(report)
        print(f"\n报告已保存到: reports/{filename}")


if __name__ == "__main__":
    main()