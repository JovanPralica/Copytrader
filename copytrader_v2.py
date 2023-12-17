from telethon.sync import TelegramClient
import MetaTrader5 as mt5
import pandas as pd
import re

# DECORATION (NOT IMPORTANT DELETE IF YOU WANT)

print('\n* Copy trades from Telegram channel to MT5')
print('* Close trades')
print('* Modify existing trades')
print('* Free')
print('* Works 24/7')
print('* Open-source')

# DECORATION (NOT IMPORTANT DELETE IF YOU WANT)

# LOGIN INFO AND DATA
api_id = 'YOUR TELEGRAM API_ID'
api_hash = 'YOUR TELEGRAM API_HASH'

# METATRADER LOGIN/PASS INFO
account = int('YOUR ACCOUNT ID')
password = '*YOUR PASSWORD*'
server = '*YOUR SERVER NAME*'

# VERSION
print("\nMetaTrader5 package author: ",mt5.__author__)
print("MetaTrader5 package version: ",mt5.__version__,'\n')

# LOGGING IN MT5
mt5.initialize()
authorized=mt5.login(account,password,server)

if authorized:
    print("Connected: Connecting to MT5 Client\n")
else:
    print("Failed to connect at account #{}, error code: {}".format(account, mt5.last_error()))

chat = input('Enter channel name: ')

messages = []
trades = []
modifications = []
options_instant = ['Buy','Sell']
options_pending= ['Buy Limit','Sell Limit','Buy Stop','Sell Stop']
last_alert = ''
last_alert_alternative = []
tickets = []

# SCRAPING TRADES FROM TELEGRAM CHANNEL

# MT5 FUNCTIONS
def open_position(pair, order_type, size,price_value=None,tp_distance=None, stop_distance=None):

    # IDK WHY IT DOESN'T WORK WITHOUT GLOBALLING ALL THIS VARS
    global order
    global sl
    global tp
    global price
    global request

    symbol_info = mt5.symbol_info(pair)
    if symbol_info is None:
        print(pair, "not found")
        return

    if not symbol_info.visible:
        print(pair, "is not visible, trying to switch on")
        if not mt5.symbol_select(pair, True):
            print("symbol_select({}}) failed, exit", pair)
            return

    point = symbol_info.point

    if (order_type == "BUY"):
        order = mt5.ORDER_TYPE_BUY
        price = mt5.symbol_info_tick(pair).ask
        if (stop_distance):
            sl = float(stop_distance)
        if (tp_distance):
            tp = float(tp_distance)

    if (order_type == "SELL"):
        order = mt5.ORDER_TYPE_SELL
        price = mt5.symbol_info_tick(pair).bid
        if (stop_distance):
            sl = float(stop_distance)
        if (tp_distance):
            tp = float(tp_distance)

    if (order_type == "BUY STOP"):
        order = mt5.ORDER_TYPE_BUY_STOP
        if (price_value):
            price = float(price_value)
        if (stop_distance):
            sl = float(stop_distance)
        if (tp_distance):
            tp = float(tp_distance)

    if (order_type == "BUY LIMIT"):
        order = mt5.ORDER_TYPE_BUY_LIMIT
        if (price_value):
            price = float(price_value)
        if (stop_distance):
            sl = float(stop_distance)
        if (tp_distance):
            tp = float(tp_distance)

    if (order_type == "SELL STOP"):
        order = mt5.ORDER_TYPE_SELL_STOP
        if (price_value):
            price = float(price_value)
        if (stop_distance):
            sl = float(stop_distance)
        if (tp_distance):
            tp = float(tp_distance)

    if (order_type == "SELL LIMIT"):
        order = mt5.ORDER_TYPE_SELL_LIMIT
        if (price_value):
            price = float(price_value)
        if (stop_distance):
            sl = float(stop_distance)
        if (tp_distance):
            tp = float(tp_distance)

    if order_type == 'BUY':
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": pair,
            "volume": float(size),
            "type": order,
            "price": price,
            "sl": sl,
            "tp": tp,
            "magic": 234000,
            "comment": "",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
    elif order_type == 'SELL':
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": pair,
            "volume": float(size),
            "type": order,
            "price": price,
            "sl": sl,
            "tp": tp,
            "magic": 234000,
            "comment": "",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
    elif order_type == 'BUY STOP':
        request = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": pair,
            "volume": float(size),
            "type": order,
            "price": price,
            "sl": sl,
            "tp": tp,
            "magic": 234000,
            "comment": "",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

    elif order_type == 'BUY LIMIT':
        request = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": pair,
            "volume": float(size),
            "type": order,
            "price": price,
            "sl": sl,
            "tp": tp,
            "magic": 234000,
            "comment": "",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

    elif order_type == 'SELL STOP':
        request = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": pair,
            "volume": float(size),
            "type": order,
            "price": price,
            "sl": sl,
            "tp": tp,
            "magic": 234000,
            "comment": "",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

    elif order_type == 'SELL LIMIT':
        request = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": pair,
            "volume": float(size),
            "type": order,
            "price": price,
            "sl": sl,
            "tp": tp,
            "magic": 234000,
            "comment": "",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

    result = mt5.order_send(request)

    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print("Failed to send order :(")

def last_tick_instant(symbol=None):
    if (symbol is None):
        res = mt5.positions_get()
        for position in res:
            tickets.append(position.ticket)

def last_tick(symbol=None):
    if (symbol is None):
        res = mt5.orders_get()
        for order in res:
            tickets.append(order.ticket)

def positions_get(symbol=None):
    if (symbol is None):
        res = mt5.positions_get()
    else:
        res = mt5.positions_get(symbol=symbol)

    if (res is not None and res != ()):
        df = pd.DataFrame(list(res), columns=res[0]._asdict().keys())
        df['time'] = pd.to_datetime(df['time'], unit='s')
        return df

    return pd.DataFrame()

def position_data(pos, select_data):
    dt = {'ticket': pos[0],
          'open_time': pos[1],
          'ortype': pos[5],  # 0=buy, 1=sell
          'mgNB': pos[6],
          'lot': pos[9],
          'open_price': pos[10],
          'sl': pos[11],
          'tp': pos[12],
          'curr_price': pos[13],
          'swap': pos[14],
          'profit': pos[15],
          'symbol': pos[16],
          'comment': pos[17]
          }
    return dt[select_data]

def get_symbol_info(mt5, symbol_f, sel):

    tm = mt5.symbol_info_tick(symbol_f).time
    bid = mt5.symbol_info_tick(symbol_f).bid
    ask = mt5.symbol_info_tick(symbol_f).ask
    spread = mt5.symbol_info(symbol_f).spread
    digits = mt5.symbol_info(symbol_f).digits
    point = mt5.symbol_info(symbol_f).point
    positions = mt5.positions_get(symbol=symbol_f)
    lot = 0   # total lot size of position on symbol
    if len(positions) > 0:
        for position in positions:
            lot += position[9]
    d = {'time': tm, 'bid': bid, 'ask': ask, 'spread': spread, 'digits': digits, 'point': point, 'lot': lot}
    return d[sel]


def modify_position(mt5, symbol_f, ticket, nw_sl, nw_tp):
    positions = mt5.positions_get(symbol=symbol_f)
    p = get_symbol_info(mt5, symbol_f, 'point')
    d = get_symbol_info(mt5, symbol_f, 'digits')
    bid = get_symbol_info(mt5, symbol_f, 'bid')
    div = 10 * p  # min step size
    if positions is None:
        print("Cannot read position on {0}".format(symbol_f))
        return 0
    elif len(positions) > 0:
        for position in positions:
            tk = position_data(position, 'ticket')
            order_type = position_data(position, 'ortype')
            opp = position_data(position, 'open_price')
            sl = position_data(position, 'sl')
            tp = position_data(position, 'tp')
            mg = position_data(position, 'mgNB')
            ocm = position_data(position, 'comment')

            fmt = '{0:2.0f}'
            if d == 1:
                fmt = '{0:3.1f}'
            if d == 2:
                fmt = '{0:4.2f}'
            if d == 3:
                fmt = '{0:5.3f}'
            if d == 4:
                fmt = '{0:6.4f}'
            if d == 5:
                fmt = '{0:7.5f}'

            if nw_sl > 0:
                nw_sl = float(fmt.format(nw_sl))
            else:
                nw_sl = float(fmt.format(sl))

            if nw_tp > 0:
                nw_tp = float(fmt.format(nw_tp))
            else:
                nw_tp = float(fmt.format(tp))

            if abs(nw_sl - sl) < div and abs(nw_tp - tp) < div:
                return

            request = {
                'action': mt5.TRADE_ACTION_SLTP,
                'position': tk,
                'symbol': symbol_f,
                'sl': nw_sl,
                'tp': nw_tp,
                'magic': mg,
            }

            if tk == ticket:
                result = mt5.order_send(request)
                if result.retcode != mt5.TRADE_RETCODE_DONE:
                    print(result)
                else:
                    print('{0}, have been modify...'.format(symbol_f))

def close_position(deal_id):
    open_positions = positions_get()
    open_positions = open_positions[open_positions['ticket'] == deal_id]
    order_type = open_positions["type"].iloc[0]
    symbol = open_positions['symbol'].iloc[0]
    volume = open_positions['volume'].iloc[0]

    if (order_type == mt5.ORDER_TYPE_BUY):
        order_type = mt5.ORDER_TYPE_SELL
        price = mt5.symbol_info_tick(symbol).bid
    else:
        order_type = mt5.ORDER_TYPE_BUY
        price = mt5.symbol_info_tick(symbol).ask

    close_request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": float(volume),
        "type": order_type,
        "position": deal_id,
        "price": price,
        "magic": 234000,
        "comment": "Close trade",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    if (order_type == mt5.ORDER_TYPE_BUY_STOP):
        price = mt5.symbol_info_tick(symbol).ask
        order_type = mt5.ORDER_TYPE_BUY_STOP

        close_request = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": symbol,
            "volume": float(volume),
            "type": order_type,
            "position": deal_id,
            "price":price,
            "magic": 234000,
            "comment": "Close trade",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }


    result = mt5.order_send(close_request)

    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print("Failed to close order :(")
    else:
        print("Order successfully closed!")

def close_position_partial(deal_id,partial):
    open_positions = positions_get()
    open_positions = open_positions[open_positions['ticket'] == deal_id]
    order_type = open_positions["type"].iloc[0]
    symbol = open_positions['symbol'].iloc[0]

    if (order_type == mt5.ORDER_TYPE_BUY):
        order_type = mt5.ORDER_TYPE_SELL
        price = mt5.symbol_info_tick(symbol).bid
    else:
        order_type = mt5.ORDER_TYPE_BUY
        price = mt5.symbol_info_tick(symbol).ask

    close_request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": float(partial),
        "type": order_type,
        "position": deal_id,
        "price": price,
        "magic": 234000,
        "comment": "Close trade",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    if (order_type == mt5.ORDER_TYPE_BUY_STOP):
        price = mt5.symbol_info_tick(symbol).ask
        order_type = mt5.ORDER_TYPE_BUY_STOP

        close_request = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": symbol,
            "volume": float(partial),
            "type": order_type,
            "position": deal_id,
            "price":price,
            "magic": 234000,
            "comment": "Close trade",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }


    result = mt5.order_send(close_request)

    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print("Failed to close order :(")
    else:
        print("Partial close successfully executed!")

def delete_pending(ticket):
    close_request = {
        "action": mt5.TRADE_ACTION_REMOVE,
        "order": ticket,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    result = mt5.order_send(close_request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        result_dict = result._asdict()
    else:
        print('Delete complete...')

def execute_partial():
    close_position_partial(trades[-1][-1],0.01)

# COLLECTING LAST MESSAGES
def collect_last_message():
    global last_tick
    global last_alert
    global trades

    with TelegramClient('name', api_id, api_hash) as client:
        for msg in client.iter_messages(chat, 1000):
            messages.insert(0, [msg.text,msg.id])
            # KEYWORDS
            modification_key_1 = re.search('Close',messages[-1][0])
            modification_key_2 = re.search('Maximum Profit',messages[-1][0])
            modification_key_3 = re.search('Delete',messages[-1][0])
            modification_key_4 = re.search('Updated',messages[-1][0])
            modification_key_5 = re.search('Partial',messages[-1][0])

            if modification_key_5 != None:
                modifications.append([msg.text, msg.reply_to_msg_id])
                if modifications[-1][0] == last_alert:
                    continue
                else:
                    if trades[-1][-2] == modifications[-1][-1]:
                        execute_partial()
                        modify_position(mt5,trades[-1][0], float(trades[-1][-1]), float(trades[-1][2]),float(trades[-1][4]))
                        last_alert = modifications[-1][0]
                        break

            if modification_key_4 != None:
                modifications.append([msg.text, msg.reply_to_msg_id])
                for mod in modifications:
                    if mod[0] == last_alert:
                        continue
                    else:
                        for trade in trades:
                            for msg_test in client.iter_messages(chat, 1000):
                                if mod[-1] == msg_test.id:
                                    if mod[-1] == trade[-2]:

                                        new_parameters = msg_test.text
                                        new_price = new_parameters.partition('\n')[0].split(' ')[-1].replace('@', '')
                                        new_symbol = new_parameters.partition('\n')[0].split(' ')[-2]
                                        # GOLD
                                        if new_symbol == 'GOLD':
                                            new_symbol = 'XAUUSD'

                                        new_sl = new_parameters.split('\n')[1].split(' ')[-1].replace('**', '')
                                        new_tp = new_parameters.split('\n')[1].split(' ')[-1]
                                        modify_position(mt5, new_symbol, float(trade[-1]), float(new_sl), float(new_tp))
                                        break

                            break

            if modification_key_1 or modification_key_2 != None:
                modifications.append([msg.text, msg.reply_to_msg_id])
                for modif in modifications:
                    if modif[0] == last_alert:
                        continue
                    else:
                        if trades[-1][-2] == modifications[-1][-1]:
                            try:
                                closing_ticket = int(trades[-1][-1])
                                close_position(closing_ticket)
                                last_alert = modifications[-1][-1]
                                break

                            except IndexError:
                                continue

                            except KeyError:
                                continue


            if modification_key_3 != None:
                modifications.append([msg.text, msg.reply_to_msg_id])
                for modif in modifications:
                    if modif[0] == last_alert:
                        continue
                    else:
                        for mod in modifications:
                            for trade in trades:
                                if trade[-2] == mod[-1]:
                                    try:
                                        closing_ticket = int(trade[-1])
                                        delete_pending(closing_ticket)
                                        last_alert = mod[-1]

                                    except IndexError:
                                        continue

                                    break
                        break


def update():

    def ex_trade():
        last_message = ''
        global messages

        while True:
            messages = []
            collect_last_message()
                #1
            trade_key = re.search('Apply Adequate Money Mgt',messages[-1][0])
            buy_stop_op = re.search('Buy Stop',messages[-1][0])
            buy_limit_op = re.search('Buy Limit',messages[-1][0])
            sell_stop_op = re.search('Sell Stop',messages[-1][0])
            sell_limit_op = re.search('Sell Limit',messages[-1][0])

            if trade_key != None:
                if last_message == messages[-1][0]:
                    continue
                else:
                    for loop in range(True):

                        if buy_stop_op != None:
                            buy_cur = messages[-1][0].partition('\n')[0]

                            option = 'Buy Stop'
                            pair = buy_cur.split(' ')[2]
                            # GOLD
                            if pair == 'GOLD':
                                pair = 'XAUUSD'

                            sl = messages[-1][0].split('\n')[1].split(' ')[-1].replace('**', '')
                            tp = messages[-1][0].split('\n')[2].split(' ')[-1]
                            price = buy_cur.split(' ')[-1].replace('@','')

                            if option in buy_cur:
                                open_position(pair, option.upper(), 0.03, price, tp, sl)
                                last_tick()
                                last_message = messages[-1][0]
                                trades.append([pair, option, price, sl, tp, messages[-1][1], tickets[-1]])
                                print(trades)
                                break

                        elif buy_limit_op != None:
                            buy_cur = messages[-1][0].partition('\n')[0]

                            option = 'Buy Limit'
                            pair = buy_cur.split(' ')[2]
                            # GOLD
                            if pair == 'GOLD':
                                pair = 'XAUUSD'

                            sl = messages[-1][0].split('\n')[1].split(' ')[-1].replace('**', '')
                            tp = messages[-1][0].split('\n')[2].split(' ')[-1]
                            price = buy_cur.split(' ')[-1].replace('@','')

                            if option in buy_cur:
                                open_position(pair, option.upper(), 0.03, price, tp, sl)
                                last_tick()
                                last_message = messages[-1][0]
                                trades.append([pair, option, price, sl, tp, messages[-1][1], tickets[-1]])
                                print(trades)
                                break

                        elif sell_stop_op != None:
                            buy_cur = messages[-1][0].partition('\n')[0]

                            option = 'Sell Stop'
                            pair = buy_cur.split(' ')[2]
                            # GOLD
                            if pair == 'GOLD':
                                pair = 'XAUUSD'

                            sl = messages[-1][0].split('\n')[1].split(' ')[-1].replace('**', '')
                            tp = messages[-1][0].split('\n')[2].split(' ')[-1]
                            price = buy_cur.split(' ')[-1].replace('@','')

                            if option in buy_cur:
                                open_position(pair, option.upper(), 0.03, price, tp, sl)
                                last_tick()
                                last_message = messages[-1][0]
                                trades.append([pair, option, price, sl, tp, messages[-1][1], tickets[-1]])
                                print(trades)
                                break

                        elif sell_limit_op != None:
                            buy_cur = messages[-1][0].partition('\n')[0]

                            option = 'Sell Limit'
                            pair = buy_cur.split(' ')[2]
                            # GOLD
                            if pair == 'GOLD':
                                pair = 'XAUUSD'

                            sl = messages[-1][0].split('\n')[1].split(' ')[-1].replace('**', '')
                            tp = messages[-1][0].split('\n')[2].split(' ')[-1]
                            price = buy_cur.split(' ')[-1].replace('@','')

                            if option in buy_cur:
                                open_position(pair, option.upper(), 0.03, price, tp, sl)
                                last_tick()
                                last_message = messages[-1][0]
                                trades.append([pair, option, price, sl, tp, messages[-1][1], tickets[-1]])
                                print(trades)
                                break

                        else:
                            for last_op in options_instant:
                                buy_cur = messages[-1][0].partition('\n')[0]
                                pair = buy_cur.split(' ')[1]
                                # GOLD
                                if pair == 'GOLD':
                                    pair = 'XAUUSD'

                                option = last_op
                                sl = messages[-1][0].split('\n')[1].split(' ')[-1].replace('**', '')
                                tp = messages[-1][0].split('\n')[4].split(' ')[-1]
                                price = buy_cur.split(' ')[-1].replace('@','')

                                if option in buy_cur:
                                    open_position(pair, option.upper(), 0.03,price, tp, sl)
                                    last_tick_instant()
                                    last_message = messages[-1][0]
                                    trades.append([pair,option,price,sl,tp,messages[-1][1],tickets[-1]])
                                    print(trades)
                                    break

    ex_trade()

update()