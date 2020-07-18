from jqdatasdk import *
from datetime import datetime, timedelta

auth('13959248595','air10150619870')
dates = get_trade_days(start_date='2017-06-01', end_date='2020-06-01', count=None)
for date in dates:
    df_all = get_all_securities(types=['stock'], date=date)
    df_all = df_all[df_all['display_name'].str.find('ST') < 0]
    code_list = df_all.index.tolist()
    df_basic = get_fundamentals(query(
         valuation.code, valuation.circulating_market_cap, finance.STK_LIST
      ).filter(
          valuation.code.in_(code_list),
          valuation.circulating_market_cap < 120
      ), date=date)
    code_list = df_basic['code'].tolist()
    df_d = get_price(code_list, start_date=date, end_date=date, frequency='daily', fields=['pre_close','open','close'], fq=None, panel=False)
    df_d['open_percent'] = (df_d['open'] - df_d['pre_close']) / df_d['pre_close'] * 100
    df_d = df_d[(df_d['open_percent'] > -1.0) & (df_d['open_percent'] < 2.0) & (~df_d['code'].str.startswith('688'))]
    code_list = df_d['code'].tolist()
    df_m = get_price(code_list, start_date=f'{date} 09:30:00', end_date=f'{date} 15:00:00', frequency='1m', fields=['pre_close','open','close', 'money'], fq=None, panel=False)
    df_m = df_m.merge(df_d,on='code',how='left')
    df_m['pre_percent'] = (df_m['open_x'] - df_m['pre_close_y']) / df_m['pre_close_y'] * 100
    df_m['cur_percent'] = (df_m['close_x'] - df_m['pre_close_y']) / df_m['pre_close_y'] * 100
    df_m['diff_percent'] = df_m['cur_percent'] - df_m['pre_percent']
    df_a = df_m[(df_m['diff_percent'] > 2.50) & (df_m['cur_percent'] > 1.50) & (df_m['cur_percent'] < 3.0) & (df_m['money'] >= 3000000)]
    df_b = df_m[(df_m['cur_percent'] < -2.0) & (df_m['cur_percent'] - df_m['open_percent'] < -2.0) & (df_m['cur_percent'] - df_m['pre_percent'] < -2.0)]
    df_c = df_a.merge(df_b,on='code',how='left')
    df_c = df_c[(df_c['time_x_y'] <= df_c['time_x_x'])]
    code_list_a = df_a['code'].tolist()
    code_list_c = df_c['code'].tolist()
    codes = [code for code in code_list_a if code not in code_list_c]
    df_a = df_a[df_a['code'].isin(codes)]
    for index, row in df_a.iterrows():
        print({"code" : row['code'], "time" : str(row['time_x']), "price" : row['close_x']})