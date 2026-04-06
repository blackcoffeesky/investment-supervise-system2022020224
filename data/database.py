"""
数据库管理器 - 统一数据库访问接口
负责所有SQLite数据库的读写操作
"""

import sqlite3
from typing import List, Dict, Optional, Tuple, Any
import pandas as pd
from datetime import date, datetime


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, db_path: str = "stockdata.db"):
        """
        初始化数据库连接
        
        Args:
            db_path: 数据库文件路径
        """
        pass
    
    def get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        pass
    
    # ==================== 股票相关 ====================
    
    def get_stock_finance(
        self, 
        symbol: Optional[str] = None, 
        symbols: Optional[List[str]] = None,
        fiscal_year: Optional[int] = None,
        latest_only: bool = True
    ) -> pd.DataFrame:
        """
        获取股票财务数据
        
        Args:
            symbol: 单个股票代码
            symbols: 多个股票代码列表
            fiscal_year: 财报年份
            latest_only: 是否只返回最新财报
            
        Returns:
            财务数据DataFrame
        """
        pass
    
    def get_stock_dynamic(
        self,
        symbol: Optional[str] = None,
        symbols: Optional[List[str]] = None,
        date: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        latest_only: bool = True
    ) -> pd.DataFrame:
        """
        获取股票动态行情数据（PE/PB/股价等）
        
        Args:
            symbol: 单个股票代码
            symbols: 多个股票代码列表
            date: 具体日期
            start_date: 开始日期
            end_date: 结束日期
            latest_only: 是否只返回最新数据
            
        Returns:
            动态行情DataFrame
        """
        pass
    
    def get_stock_position(self, symbol: Optional[str] = None) -> pd.DataFrame:
        """
        获取当前持仓信息
        
        Args:
            symbol: 单个股票代码，为None时返回全部持仓
            
        Returns:
            持仓数据DataFrame
        """
        pass
    
    def get_stock_static(self, symbol: Optional[str] = None) -> pd.DataFrame:
        """
        获取股票静态信息（名称、主营业务等）
        
        Args:
            symbol: 股票代码，为None时返回全部
            
        Returns:
            静态信息DataFrame
        """
        pass
    
    # ==================== 行业相关 ====================
    
    def get_industry_level1(self) -> pd.DataFrame:
        """
        获取一级行业分类
        
        Returns:
            一级行业DataFrame，包含id, name, expected_position, buy_reason
        """
        pass
    
    def get_industry_level2(self, level1_id: Optional[int] = None) -> pd.DataFrame:
        """
        获取二级行业分类
        
        Args:
            level1_id: 一级行业ID，为None时返回全部
            
        Returns:
            二级行业DataFrame
        """
        pass
    
    def get_stock_industry(self, symbol: str) -> Dict[str, Any]:
        """
        获取股票所属行业
        
        Args:
            symbol: 股票代码
            
        Returns:
            包含level1_id, level2_id, weight的字典
        """
        pass
    
    # ==================== 风格相关 ====================
    
    def get_style_category(self, style_id: Optional[int] = None) -> pd.DataFrame:
        """
        获取风格分类配置
        
        Args:
            style_id: 风格ID，为None时返回全部
            
        Returns:
            风格配置DataFrame
        """
        pass
    
    # ==================== 宏观数据相关 ====================
    
    def get_macro_policy(
        self,
        category: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 50
    ) -> pd.DataFrame:
        """
        获取宏观政策数据
        
        Args:
            category: 政策类型（industry_policy/market_policy/monetary_policy）
            start_date: 开始日期
            end_date: 结束日期
            limit: 返回记录数限制
            
        Returns:
            政策数据DataFrame
        """
        pass
    
    def get_macro_economy(
        self,
        indicator_name: Optional[str] = None,
        country: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        获取宏观经济指标数据
        
        Args:
            indicator_name: 指标名称（CPI/PPI/GDP/GDP_growth等）
            country: 国家/地区
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            经济指标DataFrame
        """
        pass
    
    def get_macro_financial(
        self,
        country: Optional[str] = None,
        policy_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        获取金融政策数据（利率、准备金率等）
        
        Args:
            country: 国家
            policy_type: 政策类型
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            金融政策DataFrame
        """
        pass
    
    def get_macro_summary(self, summary_date: Optional[str] = None) -> pd.DataFrame:
        """
        获取宏观分析汇总
        
        Args:
            summary_date: 汇总日期，为None时返回最新
            
        Returns:
            宏观汇总DataFrame
        """
        pass
    
    # ==================== AI报告相关 ====================
    
    def save_ai_analysis_report(self, report: Dict[str, Any]) -> int:
        """
        保存AI分析报告
        
        Args:
            report: 报告字典，包含report_date, overall_score, summary等
            
        Returns:
            插入的记录ID
        """
        pass
    
    def get_ai_analysis_report(
        self, 
        report_date: Optional[str] = None,
        limit: int = 10
    ) -> pd.DataFrame:
        """
        获取历史AI分析报告
        
        Args:
            report_date: 报告日期
            limit: 返回记录数限制
            
        Returns:
            报告DataFrame
        """
        pass
    
    # ==================== 账户相关 ====================
    
    def get_account_cash(self, date: Optional[str] = None) -> pd.DataFrame:
        """
        获取账户资金记录
        
        Args:
            date: 具体日期，为None时返回全部
            
        Returns:
            账户资金DataFrame
        """
        pass
    
    def update_expected_position(
        self,
        table: str,
        id_value: int,
        expected_position: float
    ) -> bool:
        """
        更新预期仓位配置
        
        Args:
            table: 表名（industry_level1/industry_level2/stock_position）
            id_value: 记录ID或symbol
            expected_position: 新的预期仓位
            
        Returns:
            是否更新成功
        """
        pass