from gm.api import *
import sqlite3
import pandas as pd

conn = sqlite3.connect('stockdata.db')
c = conn.cursor()
token = "bda305b573432b1d8a918855d1b439c3d09671aa"
account = "2ac43580-715f-4cc5-93d7-83fccc7b7997"
set_token(token)


def add_history(symbol, start, end):
    """获取股票历史数据并存入数据库"""
    # 获取历史行情
    base = history(symbol=symbol,
                  frequency='1d',
                  start_time=start,
                  end_time=end,
                  fields='symbol,close,volume,eob',
                  adjust=1, df=True)
    
    if base.empty:
        print(f"无历史数据: {symbol}")
        return
    
    # 获取估值数据
    val = stk_get_daily_valuation(symbol=symbol, 
                                  fields='pe_ttm,pb_mrq,dy_ttm,peg_np_cgr', 
                                  start_date=start, 
                                  end_date=end, 
                                  df=True)
    # 处理日期
    base['date'] = base['eob'].apply(lambda x: x.strftime('%Y-%m-%d'))
    base['symbol'] = symbol  # 确保symbol列存在
    
    # 合并估值数据
    if val is not None and not val.empty:
        # 按日期合并
        base = pd.merge(base, val[[ 'trade_date', 'pe_ttm', 'pb_mrq', 'dy_ttm','peg_np_cgr']], left_on='date', right_on='trade_date', how='left')
    else:
        base['pe_ttm'] = None
        base['pb_mrq'] = None
        base['dy_ttm'] = None
        base['peg_np_cgr'] = None
    
    result = base[['symbol', 'date', 'close', 'volume', 'pe_ttm', 'pb_mrq', 'dy_ttm','peg_np_cgr']].copy()
    
    # 分批插入以避免重复
    for _, row in result.iterrows():
        try:
            # 检查是否已存在
            c.execute('''
                SELECT 1 FROM stock_dynamic
                WHERE symbol = ? AND date = ?
            ''', (row['symbol'], row['date']))
            
            if c.fetchone() is None:
                # 不存在则插入
                c.execute('''
                    INSERT INTO stock_dynamic
                    (symbol, date, close, volume, pe_ttm, pb_mrq, dy_ttm, peg_np_cgr) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (row['symbol'], row['date'], row['close'], row['volume'], 
                      row['pe_ttm'], row['pb_mrq'], row['dy_ttm'], row['peg_np_cgr']))
                conn.commit()
        except Exception as e:
            print(f"插入数据出错 {row['symbol']} {row['date']}: {e}")
    
    print(f"完成 {symbol} 历史数据更新, 共 {len(result)} 条")
    

def update(extra_pos=[{}],update_all=False):
    cash = get_cash(account)['available']
    position = get_position(account) if update_all else []

    for i in extra_pos:
        position.append(i)
    tot=cash
    for i in position:
        tot+=i['amount']
    
    for i in position:
        print(i['symbol'], i['amount'],i['vwap'])

    with conn:
        # udpate account table
        c.execute('''
            Select date from account where date=?''', (pd.Timestamp.now().strftime('%Y-%m-%d'),))
        if c.fetchone() is None:
            c.execute('''
                Insert into account (date,cash) values (?,?)''', 
                (pd.Timestamp.now().strftime('%Y-%m-%d'), cash))

        # update stock_position table
        if(update_all):
            c.execute('''delete from stock_position''')
        for i in position:
            c.execute('''
                Insert into stock_position (symbol,amount,vwap) values (?,?,?)''', 
                (i['symbol'], i['amount'], i['vwap']))
            c.execute('''
                select symbol from stock_static where symbol=?''', (i['symbol'],))
            if c.fetchone() is None:
                c.execute('''
                    Insert into stock_static (symbol,name) values (?,?)''', (i['symbol'], "Unknown"))

                
def update_finance(symbol, start=None, end=None):
    """start和end为None时表示更新最新数据"""
    result = stk_get_finance_deriv(symbol=symbol,
                                   fields='roe_weight,sale_gpm,sale_npm,inc_oper_yoy,net_prof_pcom_cut_yoy,ast_liab_rate,curr_rate,net_cf_oper_np,ttl_ast_turnover_rate,acct_rcv_turnover_days,net_cf_oper_ps,retain_inc_ps'
                                   ,start_date=start, end_date=end, df=True)
    if result.empty:
        print(f"无财务数据: {symbol}")
        return
    result['fiscal_year'] = result['rpt_date'].apply(lambda x: x[:4])
    for _, row in result.iterrows():
        try:
            # 检查是否已存在
            c.execute('''
                SELECT 1 FROM stock_finance 
                WHERE symbol = ? AND fiscal_year = ? AND rpt_type = ?
            ''', (row['symbol'], row['fiscal_year'], row['rpt_type']))
            if c.fetchone() is None:
                # 不存在则插入
                c.execute('''
                    INSERT INTO stock_finance
                    (symbol, fiscal_year, rpt_type, roe_weight, sale_gpm, sale_npm, inc_oper_yoy, net_prof_pcom_cut_yoy, ast_liab_rate, curr_rate, net_cf_oper_np, ttl_ast_turnover_rate, acct_rcv_turnover_days, net_cf_oper_ps, retain_inc_ps) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (row['symbol'], row['fiscal_year'], row['rpt_type'], row['roe_weight'], row['sale_gpm'], row['sale_npm'], row['inc_oper_yoy'], row['net_prof_pcom_cut_yoy'], row['ast_liab_rate'], row['curr_rate'], row['net_cf_oper_np'], row['ttl_ast_turnover_rate'], row['acct_rcv_turnover_days'], row['net_cf_oper_ps'], row['retain_inc_ps']))
                conn.commit()

        except Exception as e:
            print(f"插入财务数据出错 {row['symbol']}: {e}")
    
    print(f"完成 {symbol} 财务数据更新, 共 {len(result)} 条")


def check():
    with conn:
        c.execute('''
        select symbol from stock_static where name=? or style_id=?''', ("Unknown", None))
        res = c.fetchall()
        if(len(res) > 0):
            print("存在未更新完整股票，请更新股票静态数据:")
            for i in res:
                print(i[0])
        
        c.execute('''
        select symbol from stock_static where symbol not in (select symbol from industry_level)''')
        res = c.fetchall()
        if(len(res) > 0):
            print("存在未分类股票，请更新股票行业分类数据")
            for i in res:
                c.execute('''
                          select name from stock_static where symbol=?''', (i[0],))
                stock_name = c.fetchone()
                print(f"{i[0]} - {stock_name[0] if stock_name else 'Unknown'}")

if __name__ == "__main__":

    gold=[{'symbol': 'GOLD', 'amount': 25600, 'vwap': 1020}]
    update(extra_pos=gold)
    check()
    # with conn:
    #     c.execute('SELECT symbol FROM stock_position')
    #     symbols = [row[0] for row in c.fetchall()]
    #     for symbol in symbols:
    #         print(f"正在更新 {symbol} 的财务数据...")
    #         # c.execute('DELETE FROM stock_finance WHERE symbol = ?', (symbol,))
    #         update_finance(symbol, start='2020-01-01', end=pd.Timestamp.now().strftime('%Y-%m-%d'))
