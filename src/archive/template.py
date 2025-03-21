from jqdata import *
from sqlalchemy import or_, and_
from datetime import datetime, timedelta

def initialize(context):
    set_benchmark({'000001.XSHG':0.5,'399006.XSHE':0.5})
    set_option('use_real_price', True)
    set_order_cost(OrderCost(close_tax=0.001, open_commission=0.0003, close_commission=0.0003, min_commission=5), type='stock')
    run_daily(before_market_open, time='before_open', reference_security='000001.XSHG')
    run_daily(market_open, time='every_bar', reference_security='000001.XSHG')
    run_daily(market_open_sell, time='every_bar', reference_security='000001.XSHG')
    run_daily(after_market_close, time='after_close', reference_security='000001.XSHG')


def before_market_open(context):
    pass

def market_open(context):
    pass

def market_open_sell(context):
    pass

def after_market_close(context):
    pass