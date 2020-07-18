# 导入函数库
from jqdata import *
from sqlalchemy import or_, and_
from datetime import datetime, timedelta

# 初始化函数，设定基准等等
def initialize(context):
    # 设定上证指数作为基准
    set_benchmark('000001.XSHG')
    # 开启动态复权模式(真实价格)
    set_option('use_real_price', True)
    
    set_order_cost(OrderCost(close_tax=0.001, open_commission=0.0003, close_commission=0.0003, min_commission=5), type='stock')
    
    run_daily(before_market_open, time='before_open', reference_security='000001.XSHG')
    
    run_daily(market_open, time='every_bar', reference_security='000001.XSHG')
    
    # run_daily(sell, time='every_bar', reference_security='000001.XSHG')
    
    run_daily(clear, time='15:00', reference_security='000001.XSHG')
    
    run_daily(after_market_close, time='after_close', reference_security='000001.XSHG')
    
    g.buy_time = {}
    
    g.params = {
      'period' : 9,
      'stop_loss' : -8.0,
      'start_stop_win' : 4.0,
      'start_win_delta' : 3.0,
      'stop_win_delta' : 1/3
    }
    
    g.config = {
       'open_percent' : {
           'min' : 0.0,
           'max' : 5.0
       },
       'cur_percent' : {
           'min' : 3.0,
           'max' : 8.0
       },
       'diff_percent' : {
           'min' : 3.0
       },
       'index_trend' : {
           'days' : '5d',
           'min_percent' : 0.5
       }, 
       'reach_high_limit_days' : 30,
       'drop_percent' : -2.0, 
       'min_money' : 6000000, 
       'super_buy' : {
          'days' : '40d',
          'ratio' : 3
       }
    }
    
    g.stop_win = {}
    
    g.start_stop_win = {}
    
    
def init_buy_list(context):
    g.buy_list = []
    for user_stock_account in context.subportfolios:
        for key, stock in user_stock_account.long_positions.items():
            if key not in g.buy_list:
                g.buy_list.append(key)
                
def filter_only_zt_in_30_days(code_list, date):
    df = get_price(code_list, count=60, end_date=date, skip_paused=True, frequency='1d', fields=['pre_close','open','close'], fq='pre', panel=False)
    df['percent'] = (df['close'] - df['pre_close']) / df['pre_close'] * 100
    df_matched = df[df['percent'] >= 9.90]
    return list(set(df_matched['code'].tolist()))
    
#initialize the hot concepts
def get_basic_codes(date):
    df_all = get_all_securities(types=['stock'], date=date)
    df_all = df_all[(df_all['display_name'].str.find('ST') < 0) & (df_all['start_date'] < date - timedelta(days=30))]
    code_list = df_all.index.tolist()
    df_basic = get_fundamentals(query(
         valuation.code
      ).filter(
          valuation.code.in_(code_list),
          valuation.circulating_market_cap <= 150
      ), date=date)
    return df_basic['code'].tolist()
    
def get_reach_high_limit_codes(code_list, date):
    df_price = get_price(code_list, start_date=date, end_date=date, frequency='daily', fields=['paused','close','high_limit'], fq=None, panel=False)
    df_price = df_price[(df_price['close'] == df_price['high_limit']) & (df_price['paused'] == 0.0)]
    code_list = df_price['code'].tolist()
    return code_list
    
def get_reach_high_limit_in_n_days(cur_date, days=30):
    code_list = get_basic_codes(cur_date)
    dates = get_trade_days(end_date=cur_date - timedelta(days=1), count=days)
    all_codes = []
    for history_date in dates:
        high_limit_codes = get_reach_high_limit_codes(code_list, history_date)
        all_codes.extend(high_limit_codes)
    all_codes = list(set(all_codes))
    return all_codes

def get_percents_before_20_days(cur_date, code_list):
    end_date = cur_date - timedelta(days=1)
    df_index = get_price(['000001.XSHG', '399006.XSHE'], end_date=end_date, count=1, frequency=g.config['super_buy']['days'], fields=['low','close'], skip_paused=True, fq=None, panel=False)
    df_index['percent'] = (df_index['close'] - df_index['low']) / df_index['low'] * 100 * g.config['super_buy']['ratio']
    df = get_price(code_list, end_date=end_date, count=1, frequency=g.config['super_buy']['days'], fields=['low','close'], skip_paused=True, fq=None, panel=False)
    df['percent'] = (df['close'] - df['low']) / df['low'] * 100
    cyb_df = df[df['code'].str.startswith('3')]
    limit_percent = df_index[df_index['code'] == '399006.XSHE']['percent'].iloc[0]
    limit_percent = 25 if limit_percent < 25 else (45 if limit_percent > 45 else limit_percent)
    cyb_df = cyb_df[cyb_df['percent'] <= limit_percent]
    sz_df = df[~df['code'].str.startswith('3')]
    limit_percent = df_index[df_index['code'] == '000001.XSHG']['percent'].iloc[0]
    limit_percent = 25 if limit_percent < 25 else (45 if limit_percent > 45 else limit_percent)
    sz_df = sz_df[sz_df['percent'] <= limit_percent]
    codes = []
    codes.extend(cyb_df['code'].tolist())
    codes.extend(sz_df['code'].tolist())
    return list(set(codes))

def get_target_codes(cur_date):
    code_list = get_reach_high_limit_in_n_days(cur_date)
    lock_code_list = get_lock_share(code_list, cur_date)
    code_list = [code for code in code_list if code not in lock_code_list]
    index_code_list = get_index_trend(cur_date)
    code_list = get_percents_before_20_days(cur_date, code_list)
    code_list = [code for code in code_list if ((code.startswith('3') and '399006.XSHE' in index_code_list) or (not code.startswith('3') and '000001.XSHG' in index_code_list)) ]
    return code_list
    
def get_lock_share(code_list, cur_date):
    df = get_locked_shares(code_list, start_date=cur_date, forward_count=30)
    return list(set(df['code'].tolist()))
    
def get_index_trend(cur_date):
    df_d = get_price(['000001.XSHG', '399006.XSHE'], count=1, end_date=cur_date - timedelta(days=1), frequency=g.config['index_trend']['days'], fields=['open','close'], fq=None, panel=False)
    df_d['percent'] = (df_d['close'] - df_d['open']) / df_d['open'] * 100
    df_temp = df_d[df_d['percent'] >= g.config['index_trend']['min_percent']]
    return df_temp['code'].tolist()
    
    
## 开盘前运行函数
def before_market_open(context):
    date = context.current_dt.date()
    init_buy_list(context)
    add_day_for_buy_list()
    calculate_sell(context)
    code_list = get_target_codes(date)
    if len(code_list) == 0:
        return
    df = get_price(code_list, start_date=date, end_date=date, frequency='daily', fields=['pre_close','open','close'], fq='pre', panel=False)
    # df_1 = get_price(code_list, count=1, end_date=date - timedelta(days = 1), frequency='5d', fields=['open','close', 'high', 'low'], fq='pre', panel=False)
    # df_2 = get_price(code_list, count=1, end_date=date - timedelta(days = 1), frequency='15d', fields=['open','close', 'high', 'low'], fq='pre', panel=False)
    df['open_percent'] = (df['open'] - df['pre_close']) / df['pre_close'] * 100
    # df_1['percent'] = (df_1['close'] - df_1['low']) / df_1['low'] * 100
    # df_2['percent'] = (df_2['close'] - df_2['low']) / df_2['low'] * 100
    df = df[(df['open_percent'] > g.config['open_percent']['min']) & (df['open_percent'] < g.config['open_percent']['max']) & (~df['code'].str.startswith('688'))]
    # df_1 = df_1[(df_1['percent'] < 20) & (~df_1['code'].str.startswith('688'))]
    # df_2 = df_2[(df_2['percent'] < 30) & (~df_2['code'].str.startswith('688'))]
    # tmp_codes = set(df['code'].tolist()).intersection(set(df_1['code'].tolist()))
    # context.universe = list(set(tmp_codes).intersection(set(df_2['code'].tolist())))
    context.universe = set(df['code'].tolist())
    log.info(f'stock_size = {len(context.universe)}')
    calculate(context)
    
    
def add_day_for_buy_list():
    for key, value in g.buy_time.items():
        g.buy_time[key] = value + 1
    
def init_start_stop_win(context, key, stock):
    date = context.current_dt.date()
    df = get_price(key, count=1, end_date=date - timedelta(days = 1), frequency='1d', fields=['open','close', 'high', 'low'], panel=False)
    t_0_percent = (df.iloc[-1]['close'] - stock.acc_avg_cost) / stock.acc_avg_cost * 100
    if t_0_percent >= g.params['start_stop_win']:
        g.start_stop_win[key] = t_0_percent
        g.stop_win[key] = t_0_percent - t_0_percent * g.params['stop_win_delta']
    else:
        g.start_stop_win[key] = t_0_percent + g.params['start_win_delta']
    
def calculate_sell(context):
    g.gonna_sell = {} 
    date = context.current_dt.date()
    for user_stock_account in context.subportfolios:
        for key, stock in user_stock_account.long_positions.items():
            if stock.closeable_amount > 0:
                panel = get_price(key, start_date=f'{date}', end_date=f'{date}', frequency='1d', fields=['pre_close','close'], skip_paused=True, fq=None, panel=False)
                pre_close = panel['pre_close'][0]
                panel = get_price(key, start_date=f'{date} 09:30:00', end_date=f'{date} 15:00:00', frequency='1m', fields=['pre_close','open','close', 'high_limit', 'money'], skip_paused=True, fq=None, panel=False)
                for index,row in panel.iterrows():
                    cur_percent = (row['close'] - pre_close) / pre_close * 100
                    if cur_percent < -8.0:
                        sell_time = str(index)
                        if sell_time in g.gonna_sell:
                            g.gonna_sell[sell_time].append(key)
                        else:
                            g.gonna_sell[sell_time] = [key]
                        log.info(f'sell, key={key}')
                        break
                    percent = (row['close'] - stock.acc_avg_cost) / stock.acc_avg_cost * 100
                    if key not in g.start_stop_win:
                        init_start_stop_win(context, key, stock)
                    log.info(f'calc sell, key={key}, percent={percent}, close={row["close"]}, acc_avg_cost={stock.acc_avg_cost}, stop_win={g.stop_win}, start_stop_win={g.start_stop_win[key]}')
                    if percent < g.params['stop_loss'] or (key in g.stop_win and percent < g.stop_win[key]) or (key in g.buy_time and g.buy_time[key] >= g.params['period']):
                        log.info(f'sell, key={key}, stop_win={g.stop_win}, start_stop_win={g.start_stop_win[key]},  buy_time={g.buy_time}')
                        sell_time = str(index)
                        if sell_time in g.gonna_sell:
                            g.gonna_sell[sell_time].append(key)
                        else:
                            g.gonna_sell[sell_time] = [key]
                        break    
                    elif (key not in g.stop_win and percent >= g.start_stop_win[key]) or (key in g.stop_win and percent - percent * g.params['stop_win_delta'] > g.stop_win[key]):
                        g.stop_win[key] = percent - percent * g.params['stop_win_delta']
                        log.info(f'update stop_win, key={key}, stop_win={g.stop_win[key]}, start_stop_win={g.start_stop_win[key]}')
                    if key not in g.stop_win:
                        g.start_stop_win[key] = percent + g.params['start_win_delta']
                        
                        
        
    
def calculate(context):
    g.gonna_buy = {}
    date = context.current_dt.date()
    for code in context.universe:
        panel = get_price(code, start_date=f'{date} 09:30:00', end_date=f'{date} 15:00:00', frequency='1m', fields=['pre_close','open','close', 'money'], skip_paused=False, fq='pre', panel=False)
        # print(panel)
        pre_close = panel.iloc[0]['pre_close']
        open_percent = (panel.iloc[0]['open'] - pre_close) / pre_close * 100
        for index,row in panel.iterrows():
            pre_percent = (row['open'] - pre_close) / pre_close * 100
            cur_percent = (row['close'] - pre_close) / pre_close * 100
            if cur_percent < g.config['drop_percent'] or cur_percent - open_percent < g.config['drop_percent'] or cur_percent - pre_percent < g.config['drop_percent']:
                break
            diff_percent = cur_percent - pre_percent
            if diff_percent > g.config['diff_percent']['min'] and cur_percent > g.config['cur_percent']['min'] and cur_percent < g.config['cur_percent']['max'] and row['money'] >= g.config['min_money']:
                log.info(f'code = {code}, open_percent = {open_percent}, cur_percent = {cur_percent}, diff_percent = {diff_percent}, money = {row["money"]}, time = {index}')
                buy_time = str(index)
                if code not in g.buy_list and len(g.gonna_buy) <= 10:
                    if buy_time in g.gonna_buy:
                        g.gonna_buy[buy_time].append(code)
                    else:
                        g.gonna_buy[buy_time] = [code]
    log.info(f'gonna_buy_list = {g.gonna_buy}')
                    

    
    
    
def sell(context):
    try:
        for user_stock_account in context.subportfolios:
            for key, stock in user_stock_account.long_positions.items():
                if stock.closeable_amount > 0:
                    bar = get_bars(key, 1, unit='1m',fields=['date', 'open','high','low','close', 'money'], include_now=True, df=False)
                    if (bar[0][4] - stock.acc_avg_cost) / stock.acc_avg_cost * 100 >= 30.0:
                        order(key, stock.closeable_amount * -1)
    except Exception as e:
        log.error(e)
                    
                    
def clear(context):
    try:
        str_time = str(context.current_dt)
        if str_time in g.gonna_sell:
            for user_stock_account in context.subportfolios:
                for key, stock in user_stock_account.long_positions.items():
                    if stock.closeable_amount > 0 and key in g.gonna_sell[str_time]:
                        order(key, stock.closeable_amount * -1)
                        g.buy_list.remove(key)
    except Exception as e:
        log.error(e)
    
                
    
## 开盘时运行函数
def market_open(context):
    try:
        str_time = str(context.current_dt)
        if str_time in g.gonna_buy:
            for code in g.gonna_buy[str_time]:
                if order_value(code, 60000) is not None:
                    g.buy_time[code] = 0
                    g.buy_list.append(code)
    except Exception as e:
        log.error(e)
        
        
        
def after_market_close(context):
    # log.info(context.universe)
    #得到当天所有成交记录
    trades = get_trades()
    for _trade in trades.values():
        log.info('成交记录：'+str(_trade))