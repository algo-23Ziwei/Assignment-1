# 导入函数库
import jqdata
#import statsmodels.api as sm
#from statsmodels.tsa.stattools import adfuller

## 初始化函数，设定基准等等
def initialize(context):
    # 设置参数
    set_params(context)
    # 设定基准
    set_benchmark(get_future_code(g.future_index))
    # 开启动态复权模式(真实价格)
    set_option('use_real_price', True)
    # 过滤掉order系列API产生的比error级别低的log
    log.set_level('order', 'error')
    # 初始化标的
    g.future = get_future_code(g.future_index)


    ### 期货相关设定 ###
    # 设定账户为期货账户
    set_subportfolios([SubPortfolioConfig(cash=context.portfolio.starting_cash, type='futures')])
    # 期货类每笔交易时的手续费是：买入时万分之0.23,卖出时万分之0.23,平今仓为万分之23
    set_order_cost(OrderCost(open_commission=0.000023, close_commission=0.000023,close_today_commission=0.0023), type='futures')
    # 设定保证金比例
    set_option('futures_margin_rate', 0.15)

    # 运行函数（reference_security为运行时间的参考标的；传入的标的只做种类区分，因此传入'IF1512.CCFX'或'IH1602.CCFX'是一样的）
      # 开盘前运行
    run_daily( before_market_open, time='before_open', reference_security=get_future_code(g.future_index))
      # 开盘时运行
    run_daily( while_open, time='open', reference_security=get_future_code(g.future_index))
      # 收盘后运行
    run_daily( after_market_close, time='after_close', reference_security=get_future_code(g.future_index))


def set_params(context):
    # 设置唐奇安通道时间窗口
    g.window = 20
    # 最大unit数目
    g.limit_unit = 6
    # 每次交易unit数目
    g.unit = 0
    # 加仓次数
    g.add_time = 0
    # 持仓状态
    g.position = 0
    # 最高价指标，用作移动止损
    g.price_mark = 0
    # 最近一次交易的合约
    g.last_future = None
    # 上一次交易的价格
    g.last_price = 0
    # 合约
    g.future_index = 'SR'
    
## 开盘前运行函数     
def before_market_open(context):
    ## 获取要操作的期货(g.为全局变量)
      # 获取当月期货合约
    g.future = get_dominant_future(g.future_index) 
    
## 开盘时运行函数
def while_open(context):
    # 如果期货标的改变，重置参数
    if g.last_future == None:
        g.last_future = g.future
    elif g.last_future != g.future:
        if g.position == -1:
            order_target(g.last_future,0,side='short')
            g.position == 0
        elif g.position == 1:
            order_target(g.last_future,0,side='long')
            g.position == 0
        g.last_future = g.future
        re_set()
        log.info("主力合约改变，平仓！")
    
    # 当月合约
    future = g.future
    # 获取当月合约交割日期
    end_date = get_CCFX_end_date(future)
    # 当月合约交割日当天不开仓
    if (context.current_dt.date() == end_date):
        return
    price_list = attribute_history(future,g.window+1,'1d',['close','high','low'])
    # 如果没有数据，返回
    if len(price_list) == 0: 
        return
    close_price = price_list['close'].iloc[-1] 
    # 计算ATR
    ATR = get_ATR(price_list,g.window)
    
    ## 判断加仓或止损
      # 先判断是否持仓
    #g.position = get_position(context)
    if g.position != 0 :   
        signal = get_next_signal(close_price,g.last_price,ATR,g.position)
        # 判断加仓且持仓没有达到上限
        if signal == 1 and g.add_time < g.limit_unit:  
            g.unit = get_unit(context.portfolio.total_value,ATR,g.future_index)
            # 多头加仓
            if g.position == 1: 
                order(future,g.unit,side='long')
                log.info( '多头加仓成功:',context.current_dt.time(),future,g.unit)
                g.last_price = close_price
                g.add_time += 1
            # 空头加仓
            elif g.position == -1: 
                order(future,g.unit,side='short')
                log.info( '空头加仓成功:',context.current_dt.time(),future,g.unit)
                g.last_price = close_price
                g.add_time += 1
        # 判断平仓止损
        elif signal == -1:
            # 多头平仓
            if g.position == 1:
                order_target(future,0,side='long')
                g.price_mark = 0
                g.position = 0
                log.info( '多头止损成功:',context.current_dt.time(),future)
                log.info('----------------------------------------------------------')
            # 空头平仓
            elif g.position == -1:  
                order_target(future,0,side='short')
                g.price_mark = 0
                g.position = 0
                log.info( '空头止损成功:',context.current_dt.time(),future)
                log.info('----------------------------------------------------------')
            # 重新初始化参数
            re_set()
    
    ## 开仓
      # 得到开仓信号
    open_signal = check_break(price_list,close_price,g.window)
    # 多头开仓
    if open_signal ==1 and g.position !=1:  
        # 检测否需要空头平仓
        if g.position == -1:
            order_target(future,0,side='short')
            if context.portfolio.short_positions[future].total_amount==0:
                g.price_mark = 0
                # 重新初始化参数
                re_set()
                log.info( '空头平仓成功:',context.current_dt.time(),future)
                log.info('----------------------------------------------------------')
        # 多头开仓
        g.unit = get_unit(context.portfolio.total_value,ATR,g.future_index)
        order(future,g.unit,side='long')
        if context.portfolio.positions[future].total_amount>0:
            g.position = 1
            g.price_mark = context.portfolio.long_positions[future].price
            log.info( '多头建仓成功:',context.current_dt.time(),future,g.unit)
            log.info('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
            g.add_time = 1
            g.last_price = close_price
            g.last_future= future
    # 空头开仓
    elif open_signal == -1 and g.position != -1:
        # 检测否需要多头平仓
        if g.position == 1:
            order_target(future,0,side='long')
            if context.portfolio.positions[future].total_amount==0:
                g.price_mark = 0
                # 重新初始化参数
                re_set()
                log.info( '多头平仓成功:',context.current_dt.time(),future)
                log.info('----------------------------------------------------------')
        # 空头开仓
        g.unit = get_unit(context.portfolio.total_value,ATR,g.future_index)
        order(future,g.unit,side='short')
        if context.portfolio.short_positions[future].total_amount > 0:
            g.position = -1
            g.price_mark = context.portfolio.short_positions[future].price
            log.info( '空头建仓成功:',context.current_dt.time(),future,g.unit)
            log.info('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
            g.add_time = 1
            g.last_price = close_price
            g.last_future= future
    
    # 判断今日是否出现最高价
    if g.position != 0:
        set_price_mark(context,future)
    # 得到止损信号
    signal = get_risk_signal(context,future)
    # 止损平仓
    if signal:
        order_target(future, 0, side='short')
        order_target(future, 0, side='long')
        if context.portfolio.positions[future].total_amount==0 and context.portfolio.short_positions[future].total_amount==0:
            log.info("止损平仓!")
            g.position = 0
            g.price_mark = 0
    return  
        
## 收盘后运行函数  
def after_market_close(context):
    pass
