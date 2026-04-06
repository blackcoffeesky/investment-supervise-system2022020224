#!/usr/bin/env python
"""
每日定时任务脚本
执行数据更新和AI分析
"""

import sys
import os
import logging
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.database import DatabaseManager
from data.stock_updater import StockDataUpdater
from data.macro_collector import MacroDataCollector
from orchestrator.agent_orchestrator import AgentOrchestrator
from orchestrator.report_generator import ReportGenerator
from utils.llm_client import LLMClient
from utils.logger import setup_logger


def setup_logging():
    """设置日志"""
    logger = setup_logger(
        name="daily_job",
        log_file=f"logs/daily_{datetime.now().strftime('%Y%m%d')}.log"
    )
    return logger


def update_data(db_manager: DatabaseManager, logger) -> None:
    """
    更新所有数据
    
    Args:
        db_manager: 数据库管理器
        logger: 日志记录器
    """
    logger.info("开始更新数据...")
    
    # 1. 更新股票行情和估值
    updater = StockDataUpdater(db_manager)
    updater.update_all_stocks()
    logger.info("股票数据更新完成")
    
    # 2. 更新宏观数据
    macro_collector = MacroDataCollector(db_manager)
    macro_collector.update_all_macro_data()
    logger.info("宏观数据更新完成")


def run_analysis(db_manager: DatabaseManager, llm_client, logger) -> dict:
    """
    运行AI分析
    
    Args:
        db_manager: 数据库管理器
        llm_client: LLM客户端
        logger: 日志记录器
        
    Returns:
        分析结果
    """
    logger.info("开始AI分析...")
    
    orchestrator = AgentOrchestrator(db_manager, llm_client)
    result = orchestrator.run_analysis()
    
    logger.info(f"分析完成，综合评分: {result.get('overall_score', 'N/A')}")
    return result


def generate_reports(result: dict, logger) -> None:
    """
    生成报告
    
    Args:
        result: 分析结果
        logger: 日志记录器
    """
    logger.info("开始生成报告...")
    
    generator = ReportGenerator()
    
    # 生成摘要报告
    summary = generator.generate_summary_report(result)
    with open(f"reports/summary_{datetime.now().strftime('%Y%m%d')}.txt", "w") as f:
        f.write(summary)
    
    # 生成Markdown报告
    markdown = generator.generate_markdown_report(result)
    with open(f"reports/report_{datetime.now().strftime('%Y%m%d')}.md", "w") as f:
        f.write(markdown)
    
    # 生成操作指令表
    operations = result.get('stock_operations', [])
    if operations:
        df = generator.generate_operation_sheet(operations)
        df.to_excel(f"reports/operations_{datetime.now().strftime('%Y%m%d')}.xlsx", index=False)
    
    logger.info("报告生成完成")


def main():
    """主函数"""
    logger = setup_logging()
    logger.info("=" * 50)
    logger.info(f"开始执行每日任务 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 初始化
        db_manager = DatabaseManager()
        llm_client = LLMClient()
        
        # 1. 更新数据
        update_data(db_manager, logger)
        
        # 2. 运行分析
        result = run_analysis(db_manager, llm_client, logger)
        
        # 3. 生成报告
        generate_reports(result, logger)
        
        # 4. 保存结果
        db_manager.save_ai_analysis_report(result)
        
        logger.info("每日任务执行成功")
        
    except Exception as e:
        logger.error(f"每日任务执行失败: {e}", exc_info=True)
        sys.exit(1)
    
    logger.info("=" * 50)


if __name__ == "__main__":
    main()