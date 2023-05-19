########################## 自定义函数 #################################
# 重置参数
def re_set():
    # 每次交易unit数目
    g.unit = 0
    # 加仓次数
    g.add_time = 0
    # 持仓状态
    g.position = 0

def check_break(price_list,price,T):
    up = max(price_list['high'].iloc[-T-1:-2])
    down = min(price_list['low'].iloc[-T-1:-2])  
    if price>up:
        return 1
    elif price<down:
        return -1
    else:
        return 0 

def get_ATR(price_list,T):
   
    #TR_list = [max(price_list['high'].iloc[i]-price_list['low'].iloc[i],abs(price_list['high'].iloc[i]-price_list['close'].iloc[i-1]),abs(price_list['close'].iloc[i-1]-price_list['low'].iloc[i])) for i in range(1,T+1)]
    TR_list = [(max(price_list['high'].iloc[i],price_list['close'].iloc[i-1]) - min(price_list['low'].iloc[i],price_list['close'].iloc[i-1])) for i in range(1,T+1)]
    ATR = np.array(TR_list).mean()
    return ATR

def get_next_signal(price,last_price,ATR,position):# 加仓或止损
    log.info( 'price:',price,'last_price:',last_price,'ATR:',ATR,'position',position)
    if (price >= last_price + 0.5*ATR and position==1) or (price <= last_price - 0.5*ATR and position==-1): # 多头加仓或空头加仓
        return 1
    elif (price <= last_price - 2*ATR and position==1) or (price >= last_price + 2*ATR and position==-1):  # 多头止损或空头止损
        return -1
    else:
        return 0
    
def get_position(context): # 0为未持仓，1为持多，-1为持空 
    try:
        tmp = context.portfolio.positions.keys()[0]
        if not context.portfolio.long_positions[tmp].total_amount and not context.portfolio.short_positions[tmp].total_amount:
            return 0
        elif context.portfolio.long_positions[tmp].total_amount:
            return 1
        elif context.portfolio.short_positions[tmp].total_amount:
            return -1
        else:
            return 0
    except:
        return 0

def get_unit(cash,ATR,symbol):
    future_coef_list = {'A':10, 'AG':15, 'AL':5, 'AU':1000,
                        'B':10, 'BB':500, 'BU':10, 'C':10, 
                        'CF':5, 'CS':10, 'CU':5, 'ER':10, 
                        'FB':500, 'FG':20, 'FU':50, 'GN':10, 
                        'HC':10, 'I':100, 'IC':200, 'IF':300, 
                        'IH':300, 'J':100, 'JD':5, 'JM':60, 
                        'JR':20, 'L':5, 'LR':10, 'M':10, 
                        'MA':10, 'ME':10, 'NI':1, 'OI':10, 
                        'P':10, 'PB':5, 'PM':50, 'PP':5, 
                        'RB':10, 'RI':20, 'RM':10, 'RO':10, 
                        'RS':10, 'RU':10, 'SF':5, 'SM':5, 
                        'SN':1, 'SR':10, 'T':10000, 'TA':5, 
                        'TC':100, 'TF':10000, 'V':5, 'WH':20, 
                        'WR':10, 'WS':50, 'WT':10, 'Y':10, 
                        'ZC':100, 'ZN':5}
    return (cash*0.01/ATR)/future_coef_list[symbol]

def set_price_mark(context,future):
    if g.position == -1:
        g.price_mark = min(context.portfolio.short_positions[future].price,g.price_mark)
    elif g.position == 1:
        g.price_mark = max(context.portfolio.long_positions[future].price,g.price_mark)
                
def get_risk_signal(context,future):
    if g.position == -1:
        if context.portfolio.short_positions[future].price >=1.05*g.price_mark:
            log.info("空头仓位止损，时间： "+str(context.current_dt.time()))
            return True
        else:
            return False
    elif g.position == 1:
        if context.portfolio.long_positions[future].price <= 0.95*g.price_mark:
            log.info("多头仓位止损，时间： "+str(context.current_dt.time()))
            return True
        else:
            return False
