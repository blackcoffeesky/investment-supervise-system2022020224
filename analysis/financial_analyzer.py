import pandas as pd
from typing import Dict, Tuple, Optional
import sqlite3

class FinancialAnalyzer:
    """
    财务指标分析器
    输入：包含12个核心指标的DataFrame（每行代表一个公司的财务数据）
    输出：评分、评级、自然语言摘要
    """
    
    def __init__(self):
        # 盈利能力评分标准
        self.roe_threshold = {
            '优秀': 20, '良好': 15, '一般': 8, '较差': 0, '数据缺失':-1
        }
        self.gpm_threshold = {
            '优秀': 40, '良好': 30, '一般': 20, '较差': 0, '数据缺失':-1
        }
        self.npm_threshold = {
            '优秀': 20, '良好': 10, '一般': 5, '较差': 0, '数据缺失':-1
        }
        
        # 成长性评分标准
        self.revenue_growth_threshold = {
            '高速': 20, '稳健': 10, '缓慢': 0, '负增长': -float('inf'), '数据缺失':-1
        }
        self.profit_growth_threshold = {
            '高速': 20, '稳健': 10, '缓慢': 0, '负增长': -float('inf'), '数据缺失':-1
        }
        
        # 财务健康度评分标准
        self.debt_ratio_threshold = {
            '安全': 40, '正常': 60, '警惕': 70, '危险': 100, '数据缺失':-1
        }
        self.current_ratio_threshold = {
            '安全': 2.0, '正常': 1.5, '警惕': 1.0, '危险': 0, '数据缺失':-1
        }
        self.cashflow_to_profit_threshold = {
            '优秀': 1.2, '良好': 0.8, '一般': 0.5, '较差': 0, '数据缺失':-1
        }
        
        # 运营效率评分标准
        self.asset_turnover_threshold = {
            '优秀': 1.0, '良好': 0.5, '一般': 0.3, '较差': 0, '数据缺失':-1
        }
        self.receivable_days_threshold = {
            '优秀': 30, '良好': 60, '一般': 90, '较差': 180, '数据缺失':-1
        }
        
        # 每股指标评分标准
        self.cf_ps_threshold = {
            '优秀': 2.0, '良好': 1.0, '一般': 0.5, '较差': 0, '数据缺失':-1
        }
        self.retain_eps_threshold = {
            '高': 5.0, '中': 2.0, '低': 0, '数据缺失':-1
        }

    
    def score_roe(self, value: float) -> Tuple[int, str]:
        """ROE评分"""
        if value != value:  # 检查是否为NaN
            return -1, '数据缺失'
        elif value >= self.roe_threshold['优秀']:
            return 100, '优秀'
        elif value >= self.roe_threshold['良好']:
            return 80, '良好'
        elif value >= self.roe_threshold['一般']:
            return 60, '一般'
        else:
            return 30, '较差'
    
    def score_gpm(self, value: float) -> Tuple[int, str]:
        """毛利率评分"""
        if value != value:  # 检查是否为NaN
            return -1, '数据缺失'
        elif value >= self.gpm_threshold['优秀']:
            return 100, '优秀'
        elif value >= self.gpm_threshold['良好']:
            return 80, '良好'
        elif value >= self.gpm_threshold['一般']:
            return 60, '一般'
        else:
            return 30, '较差'
    
    def score_npm(self, value: float) -> Tuple[int, str]:
        """净利率评分"""
        if value != value:  # 检查是否为NaN
            return -1, '数据缺失'
        if value >= self.npm_threshold['优秀']:
            return 100, '优秀'
        elif value >= self.npm_threshold['良好']:
            return 80, '良好'
        elif value >= self.npm_threshold['一般']:
            return 60, '一般'
        else:
            return 30, '较差'
    
    def score_revenue_growth(self, value: float) -> Tuple[int, str]:
        """营收增速评分"""
        if value != value:  # 检查是否为NaN
            return -1, '数据缺失'
        if value >= self.revenue_growth_threshold['高速']:
            return 100, '高速增长'
        elif value >= self.revenue_growth_threshold['稳健']:
            return 80, '稳健增长'
        elif value >= self.revenue_growth_threshold['缓慢']:
            return 60, '缓慢增长'
        else:
            return 20, '负增长'
    
    def score_profit_growth(self, value: float) -> Tuple[int, str]:
        """扣非利润增速评分"""
        if value != value:  # 检查是否为NaN
            return -1, '数据缺失'
        if value >= self.profit_growth_threshold['高速']:
            return 100, '高速增长'
        elif value >= self.profit_growth_threshold['稳健']:
            return 80, '稳健增长'
        elif value >= self.profit_growth_threshold['缓慢']:
            return 60, '缓慢增长'
        else:
            return 20, '负增长'
    
    def score_debt_ratio(self, value: float) -> Tuple[int, str]:
        """资产负债率评分（越低越好，但需反向）"""
        if value != value:  # 检查是否为NaN
            return -1, '数据缺失'
        if value < self.debt_ratio_threshold['安全']:
            return 100, '安全'
        elif value < self.debt_ratio_threshold['正常']:
            return 80, '正常'
        elif value < self.debt_ratio_threshold['警惕']:
            return 60, '偏高'
        else:
            return 30, '危险'
    
    def score_current_ratio(self, value: float) -> Tuple[int, str]:
        """流动比率评分"""
        if value != value:  # 检查是否为NaN
            return -1, '数据缺失'
        if value >= self.current_ratio_threshold['安全']:
            return 100, '充足'
        elif value >= self.current_ratio_threshold['正常']:
            return 80, '正常'
        elif value >= self.current_ratio_threshold['警惕']:
            return 60, '偏低'
        else:
            return 30, '危险'
    
    def score_cashflow_to_profit(self, value: float) -> Tuple[int, str]:
        """现金流/净利润评分"""
        if value != value:  # 检查是否为NaN
            return -1, '数据缺失'
        if value >= self.cashflow_to_profit_threshold['优秀']:
            return 100, '优秀'
        elif value >= self.cashflow_to_profit_threshold['良好']:
            return 80, '良好'
        elif value >= self.cashflow_to_profit_threshold['一般']:
            return 60, '一般'
        else:
            return 30, '较差'
    
    def score_asset_turnover(self, value: float) -> Tuple[int, str]:
        """总资产周转率评分"""
        if value != value:  # 检查是否为NaN
            return -1, '数据缺失'
        if value >= self.asset_turnover_threshold['优秀']:
            return 100, '优秀'
        elif value >= self.asset_turnover_threshold['良好']:
            return 80, '良好'
        elif value >= self.asset_turnover_threshold['一般']:
            return 60, '一般'
        else:
            return 30, '较低'
    
    def score_receivable_days(self, value: float) -> Tuple[int, str]:
        """应收周转天数评分（越低越好）"""
        if value != value:  # 检查是否为NaN
            return -1, '数据缺失'
        if value < self.receivable_days_threshold['优秀']:
            return 100, '优秀'
        elif value < self.receivable_days_threshold['良好']:
            return 80, '良好'
        elif value < self.receivable_days_threshold['一般']:
            return 60, '一般'
        else:
            return 30, '较差'
    
    def score_cf_ps(self, value: float, eps: Optional[float] = None) -> Tuple[int, str]:
        """每股现金流评分"""
        if value != value:  # 检查是否为NaN
            return -1, '数据缺失'
        base_score, desc = 60, '一般'
        if value >= self.cf_ps_threshold['优秀']:
            base_score, desc = 100, '充足'
        elif value >= self.cf_ps_threshold['良好']:
            base_score, desc = 80, '良好'
        elif value >= self.cf_ps_threshold['一般']:
            base_score, desc = 60, '一般'
        else:
            base_score, desc = 30, '紧张'
        
        # 如果能提供EPS，增加对比评价
        if eps is not None and eps > 0:
            if value > eps * 1.2:
                desc += '且覆盖利润'
            elif value > eps:
                desc += '且基本覆盖'
            else:
                desc += '但低于EPS'
        
        return base_score, desc
    
    def score_retain_eps(self, value: float) -> Tuple[int, str]:
        """每股留存收益评分"""
        if value != value:  # 检查是否为NaN
            return -1, '数据缺失'
        if value >= self.retain_eps_threshold['高']:
            return 80, '高'
        elif value >= self.retain_eps_threshold['中']:
            return 60, '中'
        else:
            return 40, '低'
    
    def analyze_company(self, data: Dict, eps: Optional[float] = None) -> Dict:
        """
        分析单个公司的财务数据
        data: 包含12个指标的字典
        eps: 每股收益（可选，用于现金流对比）
        """
        scores = {}
        details = {}
        
        # 盈利能力评分
        scores['roe'], details['roe'] = self.score_roe(data['roe_weight'])
        scores['gpm'], details['gpm'] = self.score_gpm(data['sale_gpm'])
        scores['npm'], details['npm'] = self.score_npm(data['sale_npm'])
        
        # 成长性评分
        scores['revenue_growth'], details['revenue_growth'] = self.score_revenue_growth(data['inc_oper_yoy'])
        scores['profit_growth'], details['profit_growth'] = self.score_profit_growth(data['net_prof_pcom_cut_yoy'])
        
        # 财务健康度评分
        scores['debt'], details['debt'] = self.score_debt_ratio(data['ast_liab_rate'])
        scores['current'], details['current'] = self.score_current_ratio(data['curr_rate'])
        scores['cashflow'], details['cashflow'] = self.score_cashflow_to_profit(data['net_cf_oper_np'])
        
        # 运营效率评分
        scores['asset_turnover'], details['asset_turnover'] = self.score_asset_turnover(data['ttl_ast_turnover_rate'])
        scores['receivable'], details['receivable'] = self.score_receivable_days(data['acct_rcv_turnover_days'])
        
        # 每股指标评分
        scores['cf_ps'], details['cf_ps'] = self.score_cf_ps(data['net_cf_oper_ps'], eps)
        scores['retain_eps'], details['retain_eps'] = self.score_retain_eps(data['retain_inc_ps'])
        
        return {
            'details': details,
            'scores': scores
        }
    
    def generate_summary(self, data: Dict, analysis_result: Dict, 
                        valuation: Optional[Dict] = None) -> str:
        """
        生成自然语言摘要
        data: 原始数据
        analysis_result: analyze_company的返回结果
        valuation: 估值数据
        """
        details = analysis_result['details']
        # 构建摘要
        summary_parts = []
        
        # 盈利能力
        profit_parts = []
        profit_parts.append(f"ROE={data.get('roe_weight', 0):.1f}%，评价：({details['roe']})")
        profit_parts.append(f"毛利率={data.get('sale_gpm', 0):.1f}%，评价：({details['gpm']})")
        profit_parts.append(f"净利率={data.get('sale_npm', 0):.1f}%，评价：({details['npm']})")
        summary_parts.append("盈利能力：" + "，".join(profit_parts))
        
        # 成长性
        growth_parts = []
        growth_parts.append(f"营收+{data.get('inc_oper_yoy', 0):.1f}%，评价：({details['revenue_growth']})")
        growth_parts.append(f"扣非利润+{data.get('net_prof_pcom_cut_yoy', 0):.1f}%，评价：({details['profit_growth']})")
        summary_parts.append("成长性：" + "，".join(growth_parts))
        
        # 财务健康度
        health_parts = []
        health_parts.append(f"负债率{data.get('ast_liab_rate', 0):.1f}%，评价：({details['debt']})")
        health_parts.append(f"流动比率{data.get('curr_rate', 0):.2f}，评价：({details['current']})")
        health_parts.append(f"现金流/利润={data.get('net_cf_oper_np', 0):.2f}，评价：({details['cashflow']})")
        summary_parts.append("财务健康：" + "，".join(health_parts))
        
        # 运营效率
        efficiency_parts = []
        efficiency_parts.append(f"总资产周转率{data.get('ttl_ast_turnover_rate', 0):.2f}，评价：({details['asset_turnover']})")
        efficiency_parts.append(f"应收周转{data.get('acct_rcv_turnover_days', 0):.0f}天，评价：({details['receivable']})")
        summary_parts.append("运营效率：" + "，".join(efficiency_parts))
        
        # 每股指标
        per_share_parts = []
        per_share_parts.append(f"每股经营现金流={data.get('net_cf_oper_ps', 0):.2f}元，评价：({details['cf_ps']})")
        per_share_parts.append(f"每股留存收益={data.get('retain_inc_ps', 0):.2f}元，评价：({details['retain_eps']})")
        summary_parts.append("每股指标：" + "，".join(per_share_parts))
        
        # 估值信息
        if valuation:
            val_parts = []
            if 'pe' in valuation:
                val_parts.append(f"PE={valuation['pe']:.1f}")
            if 'pb' in valuation:
                val_parts.append(f"PB={valuation['pb']:.2f}")
            if 'peg' in valuation:
                val_parts.append(f"PEG={valuation['peg']:.2f}")
            if 'div' in valuation:
                val_parts.append(f"股息率={valuation['div']:.1f}%")
            if val_parts:
                summary_parts.append("估值：" + " ".join(val_parts))
        
        return "\n".join(summary_parts)

def analyze_financial_data(df: pd.DataFrame, 
                          valuation_df: Optional[pd.DataFrame] = None,
                          eps_df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """
    批量分析财务数据
    df: 包含12个指标的DataFrame，每行一个公司，必须有'symbol'列
    valuation_df: 包含估值数据的DataFrame
    eps_df: 包含EPS的DataFrame（可选）
    """
    analyzer = FinancialAnalyzer()
    results = []
    
    for idx, row in df.iterrows():
        data = row.to_dict()
        symbol = data.get('symbol', f'公司_{idx}')
        
        # 获取EPS（如果有）
        eps = None
        if eps_df is not None and symbol in eps_df['symbol'].values:
            eps_row = eps_df[eps_df['symbol'] == symbol].iloc[0]
            eps = eps_row.get('eps_basic')
        
        # 分析
        analysis = analyzer.analyze_company(data, eps)
        
        # 获取估值信息
        valuation = None
        if valuation_df is not None and symbol in valuation_df['symbol'].values:
            val_row = valuation_df[valuation_df['symbol'] == symbol].iloc[0]
            valuation = {
                'pe': val_row.get('pe_ttm'),
                'pb': val_row.get('pb_mrq'),
                'peg': val_row.get('peg_np_cgr'),
                'div': val_row.get('dy_ttm')
            }
        
        # 生成摘要
        summary = analyzer.generate_summary(data, analysis, valuation)
        
        # 收集结果
        result = {
            'symbol': symbol,
            'name': data.get('name', ''),
            'summary': summary,
            'details': str(analysis['details']),  # 转为字符串存储
        }
        
        # 添加原始数据（可选）
        for key, value in data.items():
            if key not in ['symbol', 'name']:
                result[f'orig_{key}'] = value
        
        results.append(result)
    
    return pd.DataFrame(results)

# 使用示例
if __name__ == "__main__":
    conn = sqlite3.connect('stockdata.db')
    c = conn.cursor()
    with conn:
        c.execute("SELECT symbol FROM stock_static where is_index = 0")
        symbols = [row[0] for row in c.fetchall()]
        # 找出每个symbol对应的最新时间的财务数据，先找最新年，再找最新季度
        c.execute('''SELECT t1.*
            FROM stock_finance t1
            INNER JOIN (
                SELECT symbol, MAX(fiscal_year) as max_year
                FROM stock_finance
                WHERE symbol IN ({})
                GROUP BY symbol
            ) t2 ON t1.symbol = t2.symbol AND t1.fiscal_year = t2.max_year
            INNER JOIN (
                SELECT symbol, fiscal_year, MAX(rpt_type) as max_date
                FROM stock_finance
                GROUP BY symbol, fiscal_year
            ) t3 ON t1.symbol = t3.symbol AND t1.fiscal_year = t3.fiscal_year AND t1.rpt_type = t3.max_date'''.format(','.join('?' * len(symbols))), symbols)
        financial_data = c.fetchall()
        sample_data = pd.DataFrame(financial_data, columns=[desc[0] for desc in c.description])
        
        c.execute("SELECT * FROM stock_dynamic WHERE symbol IN ({}) AND date = (SELECT MAX(date) FROM stock_dynamic WHERE symbol = stock_dynamic.symbol)".format(','.join('?' * len(symbols))), symbols)
        valuation_data = c.fetchall()
        sample_valuation = pd.DataFrame(valuation_data, columns=[desc[0] for desc in c.description])
    
    # 执行分析
    results = analyze_financial_data(sample_data, sample_valuation, None)
    
    # 打印结果
    for idx, row in results.iterrows():
        print(f"\n{'='*50}")
        print(f"\n{row['summary']}")

