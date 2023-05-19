#### 获取期货合约信息 ####
# 获取当天时间正在交易的期货主力合约
def get_future_code(symbol):
    future_code_list = {'A':'A9999.XDCE', 'AG':'AG9999.XSGE', 'AL':'AL9999.XSGE', 'AU':'AU9999.XSGE',
                        'B':'B9999.XDCE', 'BB':'BB9999.XDCE', 'BU':'BU9999.XSGE', 'C':'C9999.XDCE', 
                        'CF':'CF9999.XZCE', 'CS':'CS9999.XDCE', 'CU':'CU9999.XSGE', 'ER':'ER9999.XZCE', 
                        'FB':'FB9999.XDCE', 'FG':'FG9999.XZCE', 'FU':'FU9999.XSGE', 'GN':'GN9999.XZCE', 
                        'HC':'HC9999.XSGE', 'I':'I9999.XDCE', 'IC':'IC9999.CCFX', 'IF':'IF9999.CCFX', 
                        'IH':'IH9999.CCFX', 'J':'J9999.XDCE', 'JD':'JD9999.XDCE', 'JM':'JM9999.XDCE', 
                        'JR':'JR9999.XZCE', 'L':'L9999.XDCE', 'LR':'LR9999.XZCE', 'M':'M9999.XDCE', 
                        'MA':'MA9999.XZCE', 'ME':'ME9999.XZCE', 'NI':'NI9999.XSGE', 'OI':'OI9999.XZCE', 
                        'P':'P9999.XDCE', 'PB':'PB9999.XSGE', 'PM':'PM9999.XZCE', 'PP':'PP9999.XDCE', 
                        'RB':'RB9999.XSGE', 'RI':'RI9999.XZCE', 'RM':'RM9999.XZCE', 'RO':'RO9999.XZCE', 
                        'RS':'RS9999.XZCE', 'RU':'RU9999.XSGE', 'SF':'SF9999.XZCE', 'SM':'SM9999.XZCE', 
                        'SN':'SN9999.XSGE', 'SR':'SR9999.XZCE', 'T':'T9999.CCFX', 'TA':'TA9999.XZCE', 
                        'TC':'TC9999.XZCE', 'TF':'TF9999.CCFX', 'V':'V9999.XDCE', 'WH':'WH9999.XZCE', 
                        'WR':'WR9999.XSGE', 'WS':'WS9999.XZCE', 'WT':'WT9999.XZCE', 'Y':'Y9999.XDCE', 
                        'ZC':'ZC9999.XZCE', 'ZN':'ZN9999.XSGE'}
    try:
        return future_code_list[symbol]
    except:
        return 'WARNING: 无此合约'


# 获取当天时间正在交易的股指期货合约
def get_stock_index_futrue_code(context,symbol,month='current_month'):
    '''
    获取当天时间正在交易的股指期货合约。其中:
    symbol:
            'IF' #沪深300指数期货
            'IC' #中证500股指期货
            'IH' #上证50股指期货
    month:
            'current_month' #当月
            'next_month'    #隔月
            'next_quarter'  #下季
            'skip_quarter'  #隔季
    '''
    display_name_dict = {'IC':'中证500股指期货','IF':'沪深300指数期货','IH':'上证50股指期货'}
    month_dict = {'current_month':0, 'next_month':1, 'next_quarter':2, 'skip_quarter':3}

    display_name = display_name_dict[symbol]
    n = month_dict[month]
    dt = context.current_dt.date()
    a = get_all_securities(types=['futures'], date=dt)
    try:
        df = a[(a.display_name == display_name) & (a.start_date <= dt) & (a.end_date >= dt)]
        return df.index[n]
    except:
        return 'WARRING: 无此合约'

# 获取当天时间正在交易的国债期货合约
def get_treasury_futrue_code(context,symbol,month='current'):
    '''
    获取当天时间正在交易的国债期货合约。其中:
    symbol:
            'T' #10年期国债期货
            'TF' #5年期国债期货
    month:
            'current' #最近期
            'next'    #次近期
            'skip'    #最远期
    '''
    display_name_dict = {'T':'10年期国债期货','TF':'5年期国债期货'}
    month_dict = {'current':0, 'next':1, 'skip':2}

    display_name = display_name_dict[symbol]
    n = month_dict[month]
    dt = context.current_dt.date()
    a = get_all_securities(types=['futures'], date=dt)
    try:
        df = a[(a.display_name == display_name) & (a.start_date <= dt) & (a.end_date >= dt)]
        return df.index[n]
    except:
        return 'WARRING: 无此合约'

# 获取金融期货合约到期日
def get_CCFX_end_date(fature_code):
    # 获取金融期货合约到期日
    return get_security_info(fature_code).end_date
