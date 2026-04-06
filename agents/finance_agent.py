"""
财务分析Agent
分析持仓股票的财务质量，识别强弱标的
"""

from typing import Dict, Any, List, Optional
from agents.base_agent import BaseAgent
from analysis.financial_analyzer import FinancialAnalyzer


class FinancialAgent(BaseAgent):
    """财务分析Agent"""
    
    def __init__(self, llm_client, db_manager):
        """
        初始化财务分析Agent
        
        Args:
            llm_client: LLM客户端
            db_manager: 数据库管理器
        """
        super().__init__(llm_client, "FinancialAgent", "prompts/financial_prompt.txt")
        self.db = db_manager
        self.financial_analyzer = FinancialAnalyzer()
        self.stock_analysis_cache: Dict[str, Dict] = {}
    
    def get_focus_areas(self) -> List[str]:
        """返回关注领域：盈利能力、成长性、财务健康、运营效率"""
        return ["profitability", "growth", "financial_health", "operational_efficiency"]
    
    def analyze_single_stock(
        self, 
        symbol: str, 
        financial_data: Dict[str, float],
        eps: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        分析单只股票财务数据
        
        Args:
            symbol: 股票代码
            financial_data: 财务指标字典
            eps: 每股收益（可选）
            
        Returns:
            股票财务分析结果，包含:
            - scores: 各指标评分
            - details: 各指标评级
            - total_score: 综合评分
            - health_level: 健康度（优秀/良好/一般/较差）
            - summary: 简要摘要
        """
        pass
    
    def analyze_portfolio_quality(
        self, 
        holdings: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        分析持仓组合的财务质量
        
        Args:
            holdings: 持仓列表，每个包含symbol, amount, weight
            
        Returns:
            组合财务质量分析，包含:
            - weighted_avg_roe: 加权平均ROE评分
            - weighted_avg_score: 加权平均综合评分
            - quality_distribution: 质量分布（优秀/良好/一般/较差占比）
            - weak_stocks: 质量较差的股票列表
            - strong_stocks: 质量优秀的股票列表
            - portfolio_grade: 组合整体评级（A/B/C/D）
            - recommendations: 改进建议
        """
        pass
    
    def identify_weak_stocks(self, threshold: int = 60) -> List[Dict]:
        """
        识别质量较差的股票
        
        Args:
            threshold: 评分阈值（低于此值视为较弱）
            
        Returns:
            较弱股票列表，按评分升序排列
        """
        pass
    
    def identify_strong_stocks(self, threshold: int = 80) -> List[Dict]:
        """
        识别质量优秀的股票
        
        Args:
            threshold: 评分阈值（高于此值视为优秀）
            
        Returns:
            优秀股票列表，按评分降序排列
        """
        pass
    
    def get_weighted_avg_quality_score(self) -> float:
        """
        获取组合加权平均质量评分
        
        Returns:
            加权平均评分（0-100）
        """
        pass
    
    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行财务分析
        
        Args:
            context: 上下文数据，包含holdings和financial_data
            
        Returns:
            财务分析结果字典，包含:
            - portfolio_quality: 组合质量分析
            - weak_stocks: 弱势股票列表
            - strong_stocks: 强势股票列表
            - quality_trend: 质量趋势（如有历史数据）
            - detailed_analysis: 详细分析文本
        """
        pass