from jqdata import *
from sqlalchemy import or_, and_
from datetime import datetime, timedelta

def initialize(context):
    init_config()
    set_benchmark({'000001.XSHG':0.5,'399006.XSHE':0.5})
    set_option('use_real_price', True)
    set_order_cost(OrderCost(close_tax=0.001, open_commission=0.0003, close_commission=0.0003, min_commission=5), type='stock')
    run_daily(before_market_open, time='before_open', reference_security='000001.XSHG')
    run_daily(market_open, time='every_bar', reference_security='000001.XSHG')
    run_daily(market_open_sell, time='every_bar', reference_security='000001.XSHG')
    run_daily(after_market_close, time='after_close', reference_security='000001.XSHG')


def init_config():
    g.config = {
        'drop_percent' : -2.0,
        'diff_percent' : 3.5,
        'open_percent' : {
            'min' : -1.0,
            'max' : 5.0
        },
        'cur_percent' : {
            'min' : 2.0,
            'max' : 8.0
        },
        'min_money' : 6000000,
        'buyed_day' : {},
        'buyed_list' : [],
        'max_cc' : 6,
        'single_buy_cash' : 60000,
        'force_sell_percent' : -8.0,
        'force_sell_day' : 9,
        'start_sell_percent' : 4.0,
        'stop_win_delta' : 1 / 3,
        'percent_limit_days' : '5d',
        'percent_limit' : {
            'min' : 25,
            'max' : 45
        },
        'index_trend' : {
            'days' : '5d',
            'min_percent' : 0.5
        },
        'super_buy' : {
          'days' : '40d',
          'ratio' : 3
       },
       'force_sell_percent_day' : -8.0,
       'force_sell_percent_n_days' : 25.0
    }

def before_market_open(context):
    init_buy_list(context)
    init_target_codes(context)
    calculate_sell(context)
    calculate_buy(context)
    
    
def init_buy_list(context):
    g.config['buyed_list'] = []
    for user_stock_account in context.subportfolios:
        for key, stock in user_stock_account.long_positions.items():
            if key not in g.config['buyed_list']:
                g.config['buyed_list'].append(key)
    for key, value in g.config['buyed_day'].items():
        g.config['buyed_day'][key] = value + 1
    

def market_open(context):
    try:
        str_time = str(context.current_dt)
        if str_time in g.config['gonna_buy']:
            for code in g.config['gonna_buy'][str_time]:
                if order_value(code, g.config['single_buy_cash']) is not None:
                    g.config['buyed_day'][code] = 0
                    g.config['buyed_list'].append(code)
    except Exception as e:
        log.error(e)

def market_open_sell(context):
    try:
        str_time = str(context.current_dt)
        if str_time in g.config['gonna_sell']:
            for user_stock_account in context.subportfolios:
                for key, stock in user_stock_account.long_positions.items():
                    if stock.closeable_amount > 0 and key in g.config['gonna_sell'][str_time]:
                        order(key, stock.closeable_amount * -1)
                        g.config['buyed_list'].remove(key)
    except Exception as e:
        log.error(e)

def calculate_sell(context):
    g.config['gonna_sell'] = {}
    date = context.current_dt.date()
    for user_stock_account in context.subportfolios:
        for key, stock in user_stock_account.long_positions.items():
            if stock.closeable_amount > 0:
                df = get_price(key, start_date=f'{date}', end_date=f'{date}', frequency='1d', fields=['pre_close','close'], skip_paused=True, fq=None, panel=False)
                if len(df) == 0:
                    continue
                df = get_price(key, count=1, end_date=date - timedelta(days=1), frequency='4d', fields=['low','high'], skip_paused=True, fq=None, panel=False)
                df['percent'] = (df['high'] - df['low']) / df['low'] * 100
                percent_n_days = df.iloc[0]['percent']
                df = get_price(key, start_date=f'{date} 09:30:00', end_date=f'{date} 15:00:00', frequency='1m', fields=['pre_close','open','close', 'high_limit', 'money'], skip_paused=True, fq=None, panel=False)
                pre_close = df.iloc[0]['pre_close']
                stop_win_percent = None
                for index,row in df.iterrows():
                    percent_day = (row['close'] - pre_close) / pre_close * 100
                    percent = (row['close'] - stock.acc_avg_cost) / stock.acc_avg_cost * 100
                    sell_time = None
                    if percent_day < g.config['force_sell_percent_day'] and percent_n_days >= g.config['force_sell_percent_n_days']:
                        sell_time = str(index)
                        break
                    if percent < g.config['force_sell_percent'] or g.config['buyed_day'][key] > g.config['force_sell_day']:
                        sell_time = str(index)
                        break
                    if (stop_win_percent is not None and percent < stop_win_percent and percent > 0):
                        sell_time = str(index)
                        break
                    if (stop_win_percent is None and percent >= g.config['start_sell_percent']) or (stop_win_percent is not None and percent - percent * g.config['stop_win_delta'] > stop_win_percent):
                        stop_win_percent = percent - percent * g.config['stop_win_delta']
                if sell_time is not None:
                    if sell_time in g.config['gonna_sell']:
                        g.config['gonna_sell'][sell_time].append(key)
                    else:
                        g.config['gonna_sell'][sell_time] = [key]
                    log.info(f'sell at {sell_time}, key={key}')
                        

def calculate_buy(context):
    g.config['gonna_buy'] = {}
    date = context.current_dt.date()
    if len(context.universe) == 0:
        return
    for code in context.universe:
        df = get_price(code, start_date=f'{date} 09:30:00', end_date=f'{date} 14:56:00', frequency='1m', fields=['pre_close','high_limit','open','close', 'money'], skip_paused=True, fq=None, panel=False)
        pre_close = df.iloc[0]['pre_close']
        open_percent = (df.iloc[0]['open'] - pre_close) / pre_close * 100
        for index,row in df.iterrows():
            pre_percent = (row['open'] - pre_close) / pre_close * 100
            cur_percent = (row['close'] - pre_close) / pre_close * 100
            if cur_percent < g.config['drop_percent'] or cur_percent - open_percent < g.config['drop_percent'] or cur_percent - pre_percent < g.config['drop_percent']:
                break
            diff_percent = cur_percent - pre_percent
            if diff_percent > g.config['diff_percent'] and cur_percent > g.config['cur_percent']['min'] and cur_percent < g.config['cur_percent']['max'] and row['money'] >= g.config['min_money']:
                if code not in g.config['buyed_list'] and code not in g.config['gonna_buy'] and (len(g.config['buyed_list']) - get_gonna_buy_sell_count('gonna_sell') + get_gonna_buy_sell_count('gonna_buy') <= g.config['max_cc']):
                    log.info(f'code = {code}, open_percent = {open_percent}, cur_percent = {cur_percent}, diff_percent = {diff_percent}, money = {row["money"]}, time = {index}')
                    buy_time = str(index)
                    if buy_time in g.config['gonna_buy']:
                        g.config['gonna_buy'][buy_time].append(code)
                    else:
                        g.config['gonna_buy'][buy_time] = [code]
                        
def get_gonna_buy_sell_count(buy_sell_key):
    count = 0
    for time in g.config[buy_sell_key]:
        count += len(g.config[buy_sell_key][time])
    return count


def init_target_codes(context):
    cur_date = context.current_dt.date()
    code_list = get_basic_codes(cur_date)
    code_list = get_reach_high_limit_in_past_n_days(code_list, cur_date, 30)
    code_list = remove_lock_share(code_list, cur_date)
    code_list = filter_open_percent(code_list, cur_date)
    code_list = filter_percent_risk_in_n_days(code_list, cur_date)
    code_list = filter_index_trend(code_list, cur_date)
    context.universe = list(set(code_list))
    log.info(f'target_codes length = {len(context.universe)}')
    # log.info(context.universe)
    
def filter_index_trend(code_list, cur_date):
    df = get_price(['000001.XSHG', '399006.XSHE'], count=1, end_date=cur_date - timedelta(days=1), frequency=g.config['index_trend']['days'], fields=['open','close'], fq=None, panel=False)
    df['percent'] = (df['close'] - df['open']) / df['open'] * 100
    df = df[df['percent'] >= g.config['index_trend']['min_percent']]
    index_code_list = df['code'].tolist()
    code_list = [code for code in code_list if ((code.startswith('3') and '399006.XSHE' in index_code_list) or (not code.startswith('3') and '000001.XSHG' in index_code_list)) ]
    return code_list    
    
    
def filter_percent_risk_in_n_days(code_list, cur_date):
    end_date = cur_date - timedelta(days=1)
    df_index = get_price(['000001.XSHG', '399006.XSHE'], end_date=end_date, count=1, frequency=g.config['super_buy']['days'], fields=['low','close'], skip_paused=True, fq=None, panel=False)
    df_index['percent'] = (df_index['close'] - df_index['low']) / df_index['low'] * 100 * g.config['super_buy']['ratio']
    df = get_price(code_list, end_date=end_date, count=1, frequency=g.config['super_buy']['days'], fields=['low','close'], skip_paused=True, fq=None, panel=False)
    df['percent'] = (df['close'] - df['low']) / df['low'] * 100
    cyb_df = df[df['code'].str.startswith('3')]
    limit_percent = df_index[df_index['code'] == '399006.XSHE']['percent'].iloc[0]
    limit_percent = g.config['percent_limit']['min'] if limit_percent < g.config['percent_limit']['min'] else (g.config['percent_limit']['max'] if limit_percent > g.config['percent_limit']['max'] else limit_percent)
    cyb_df = cyb_df[cyb_df['percent'] <= limit_percent]
    sz_df = df[~df['code'].str.startswith('3')]
    limit_percent = df_index[df_index['code'] == '000001.XSHG']['percent'].iloc[0]
    limit_percent = g.config['percent_limit']['min'] if limit_percent < g.config['percent_limit']['min'] else (g.config['percent_limit']['max'] if limit_percent > g.config['percent_limit']['max'] else limit_percent)
    sz_df = sz_df[sz_df['percent'] <= limit_percent]
    codes = []
    codes.extend(cyb_df['code'].tolist())
    codes.extend(sz_df['code'].tolist())
    return list(set(codes))
    
def filter_open_percent(code_list, cur_date):
    df = get_price(code_list, start_date=f'{cur_date}', end_date=f'{cur_date}', frequency='1d', fields=['pre_close','open'], skip_paused=True, fq=None, panel=False)
    df['open_percent'] = (df['open'] - df['pre_close']) / df['pre_close'] * 100
    df = df[(df['open_percent'] > g.config['open_percent']['min']) & (df['open_percent'] < g.config['open_percent']['max'])]
    return df['code'].tolist()
    
def remove_lock_share(code_list, cur_date):
    df = get_locked_shares(code_list, start_date=cur_date, forward_count=30)
    lock_code_list = df['code'].tolist()
    return [code for code in code_list if code not in lock_code_list]
    
def get_reach_high_limit_in_past_n_days(code_list, cur_date, n):
    dates = get_trade_days(end_date=cur_date - timedelta(days=1), count=n)
    target_codes = []
    for date in dates:
        df_price = get_price(code_list, start_date=date, end_date=date, frequency='daily', fields=['paused','close','high_limit'], fq=None, panel=False)
        df_price = df_price[(df_price['close'] == df_price['high_limit']) & (df_price['paused'] == 0.0)]
        target_codes.extend(df_price['code'].tolist())
    return target_codes
    
def get_basic_codes(cur_date):
    df_all = get_all_securities(types=['stock'], date=cur_date)
    df_all = df_all[(df_all['display_name'].str.find('ST') < 0) & (df_all['start_date'] < cur_date - timedelta(days=30))]
    df_basic = get_fundamentals(query(
         valuation.code
      ).filter(
          valuation.code.in_(df_all.index.tolist()),
          valuation.circulating_market_cap <= 150
      ), date=cur_date)
    df_basic = df_basic[~df_basic['code'].str.startswith('688')]
    return df_basic['code'].tolist()
    
def after_market_close(context):
    trades = get_trades()
    for _trade in trades.values():
        log.info('成交记录：'+str(_trade))