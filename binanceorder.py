__filename = 'binanceorder.py'
cStrDivider = '#================================================================#'
print('', cStrDivider, f'START _ {__filename}', cStrDivider, sep='\n')

# dependency imports
import sys
import decimal
import time
#from datetime import datetime
from house_tools import *
import sites #required: sites/__init__.py
from binance.client import Client
from binance import exceptions

# log output paths (xlogger.py -> import logging)
devpath = None
isepath = None

# binance keys & client
api_key = None
api_secret = None
client = None

# CLI flags
flagHelp = '--help'
flag1 = '-m' # market
flag2 = '-l' # limit
flag3 = '--buy'
flag4 = '--sell'
flag5 = '-s' # symbol
flag6 = '--wait-s' # input symbol
flag7 = '-v' # volume
flag8 = '-vr' # volume ratio
flag9 = '--buy-r' # buy recursive
flag10 = '--view'
flag11 = '--set-ls'
flag12 = '-c' # currency
flag13 = '--term-launch' # launch additionl term tools'
flag14 = '--open-orders' # display current open orders
flag15 = '--open-orders-cancel' # cancel all current open orders

flag1_rec = flag2_rec = flag3_rec = flag4_rec = flag5_rec = False
flag6_rec = flag7_rec = flag8_rec = flag9_rec = flag10_rec = False
flag11_rec = flag12_rec = flag13_rec = flag14_rec = flag15_rec = False

flag2_val = None
flag5_val = None
flag7_val = None
flag8_val = None
flag12_val = None

iOrdNone = 0
iOrdBuy = 1
iOrdSell = 2
iOrdBuyLimSell = 3

fPumpVolAdjRatio = 0.95
fInputVolRatio = 1.0

iCntRestReq = 0
lst_iTimeSec = []
lst_strTimeSec = []
lst_strTimeDt = []

fCurrBTCBal = 0.0

def setActiveLogPaths():
    print(f'\nGetting Active LOG PATHS...')
    devpath = sites.GLOBAL_PATH_DEV_LOGS
    isepath = sites.GLOBAL_PATH_ISE_LOGS
    print(f"LOG PATHS found..", f"  dev Logs: '{devpath}'", f"  ise Logs: '{isepath}'", sep='\n')

def setApiKeys():
    print(f'\nGetting / Validating Binance api keys...')
    global client
    api_key = sites.binance_api_key
    api_secret = sites.binance_api_secret
    incRestCnt(start=True, note='Client(api_key, api_secret)')
    client = Client(api_key, api_secret) # performs binance REST api handshakes
    incRestCnt(note='Client(api_key, api_secret)')

    print(f'DONE getting Binance api keys')

def incExeClock(strInfo=''):
    iNowSec = int(round(time.time()))
    strNowDt = datetime.fromtimestamp(iNowSec)

    lst_iTimeSec.append(iNowSec)
    lst_strTimeSec.append(f'{iNowSec} {strInfo}')
    lst_strTimeDt.append(f'{strNowDt} {strInfo}')
    return lst_iTimeSec[len(lst_iTimeSec)-1] - lst_iTimeSec[0]

def incRestCnt(start=False, note=''):
    global iCntRestReq, lst_iTimeSec, lst_strTimeDt
    if not start: iCntRestReq += 1
    strType = 'start' if start else 'end  '
    incExeClock(f" <- {strType} REST Request '{note}'")

def bin_clientGoMarketBuy(bin_client, symbTick, fVol):
    print("\nExecuting 'order_market_buy'...")
    incRestCnt(start=True, note='order_market_buy')
    order = bin_client.order_market_buy(symbol=symbTick,quantity=fVol)
    incRestCnt(note='order_market_buy')
    print("Done executing 'order_market_buy'")
    return order

def bin_clientGoMarketSell(bin_client, symbTick, fVol):
    print("\nExecuting 'order_market_sell'...")
    incRestCnt(start=True, note='order_market_sell')
    order = bin_client.order_market_sell(symbol=symbTick,quantity=fVol)
    incRestCnt(note='order_market_sell')
    print("Done executing 'order_market_sell'")
    return order

def bin_clientGoLimitBuy(bin_client, symbTick, fVol, strPrice):
    print("\nExecuting 'order_limit_buy'...")
    incRestCnt(start=True, note='order_limit_buy')
    order = bin_client.order_limit_buy(symbol=symbTick,quantity=fVol,price=strPrice)
    incRestCnt(note='order_limit_buy')
    print("Done executing 'order_limit_buy'")
    return order

def bin_clientGoLimitSell(bin_client, symbTick, fVol, strPrice):
    print("\nExecuting 'order_limit_sell'...")
    incRestCnt(start=True, note='order_limit_sell')
    order = bin_client.order_limit_sell(symbol=symbTick,quantity=fVol,price=strPrice)
    incRestCnt(note='order_limit_sell')
    print("Done executing 'order_limit_sell'")
    return order

def bin_clientGetOpenOrders(bin_client, symbTick):
    print("\nExecuting 'get_open_orders'...")
    incRestCnt(start=True, note='get_open_orders')
    lstOrders = []
    lstOrders = bin_client.get_open_orders(symbol=symbTick)
    incRestCnt(note='get_open_orders')
    print("Done executing 'get_open_orders'")
    return lstOrders

def bin_clientCancelOrder(bin_client, symbTick, iOrderID):
    print(f"\nExecuting 'cancel_order'... (orderID: {iOrderID})")
    incRestCnt(start=True, note='cancel_order')
    order = bin_client.cancel_order(symbol=symbTick, orderId=iOrderID)
    incRestCnt(note='cancel_order')
    print("Done executing 'cancel_order'")
    return order

def lstGetOpenOrderIDs(arrOrders, symbTick):
    arrOrderIdsReturn = []
    for dictOrder in arrOrders:
        symbol = dictOrder['symbol']
        orderId = dictOrder['orderId']
        clientOrderId = dictOrder['clientOrderId']
        strPrice = dictOrder['price']
        strOrigQty = dictOrder['origQty']
        strExecutedQty = dictOrder['executedQty']
        strCummQuoteQty = dictOrder['cummulativeQuoteQty']
        strTypeLimMark = dictOrder['type']
        strSideBuySell = dictOrder['side']
        strMarker = '------------------------------------------------------------>'
        print(f"\n INFO '{symbol}' order {strTypeLimMark} {strSideBuySell} id: {orderId} ...")
        print(f'  price    {strMarker} price: {strPrice}', f'  orig vol {strMarker} orig vol: {strOrigQty}', sep='\n')
        print(f'  exec vol: {strExecutedQty}', f'  cummulative vol: {strCummQuoteQty}', sep='\n')
        if symbol.lower() == symbTick.lower():
            arrOrderIdsReturn.append(orderId)
    return arrOrderIdsReturn

def fGetBalanceForSymb(bin_client, assetSymb='nil', maxPrec=9):
    print(f'\nGetting free balance for {assetSymb}...')
    incRestCnt(start=True, note='get_asset_balance')
    balanceDict = bin_client.get_asset_balance(asset=assetSymb)
    incRestCnt(note='get_asset_balance')

    balance = float(balanceDict['free'])
    #print(f' {assetSymb} balance = {balance}')
    return balance

def fGetCurrPriceForSymbTick(bin_client, symbTick='BTCUSDT'):
    incRestCnt(start=True, note='get_symbol_ticker')
    tick = bin_client.get_symbol_ticker(symbol=symbTick)
    incRestCnt(note='get_symbol_ticker')

    price = tick['price']
    strPrice = str(price).rstrip('0')
    return float(strPrice)

def getMaxBuyVolForAssetSymb(bin_client, currency='USDT', assetSymb='BTC', assetPrice='-1.0', symbTick='BTCUSDT', maxPrec=8):
    balance = fCurrBTCBal
    if currency != 'BTC':
        balance = fGetBalanceForSymb(bin_client, assetSymb=currency)

    print(f'\nGetting max buy volume for {symbTick}...')
    currPrice = float(assetPrice)
    if not currPrice > 0.0:
        currPrice = fGetCurrPriceForSymbTick(bin_client, symbTick=symbTick)
    maxVol = decimal.Decimal(balance / currPrice)
    maxVolTrunc = truncate(maxVol, maxPrec)

    #print(f' {currency} balance = {decimal.Decimal(balance)}')
    print(f' {currency} balance = {balance}')
    print(f' {symbTick} currPrice = {truncate(currPrice, 8, bDecReturn=True)} | truncate @ maxPrec: 8')
    print(f' {assetSymb} maxVol = {maxVol} | pre-truncate @ maxPrec: {maxPrec}')
    print(f' {assetSymb} maxVol = {maxVolTrunc} | truncate @ maxPrec: {maxPrec} \n')
    
    iPrec = maxPrec
    fVolMax = truncate(maxVolTrunc, iPrec) * 1.0
    fVolMaxAdj = truncate(maxVolTrunc * fPumpVolAdjRatio, iPrec) #adjust vol from rising pump (set from global constant)
    fVolMaxPerc75 = truncate(maxVolTrunc * 0.75, iPrec)
    fVolMaxHalf = truncate(maxVolTrunc * 0.50, iPrec)
    fVolMaxPerc25 = truncate(maxVolTrunc * 0.25, iPrec)
    print(f"  {assetSymb} volume can buy... (truncate(all-vol, {iPrec}))", f"max = {fVolMax}", f"max-adj ({fPumpVolAdjRatio*100}%) = {fVolMaxAdj}", f"75% max = {fVolMaxPerc75}", f"50% max = {fVolMaxHalf}", f"25% max = {fVolMaxPerc25}", sep='\n   ')

    iPrec = 0
    fVolMax = truncate(maxVolTrunc, iPrec) * 1.0
    fVolMaxAdj = truncate(maxVolTrunc * fPumpVolAdjRatio, iPrec) #adjust vol from rising pump (set from global constant)
    fVolMaxPerc75 = truncate(maxVolTrunc * 0.75, iPrec)
    fVolMaxHalf = truncate(maxVolTrunc * 0.50, iPrec)
    fVolMaxPerc25 = truncate(maxVolTrunc * 0.25, iPrec)
    print(f"  {assetSymb} volume can buy... (truncate(all-vol, {iPrec}))", f"max = {fVolMax}", f"max-adj ({fPumpVolAdjRatio*100}%) = {fVolMaxAdj}", f"75% max = {fVolMaxPerc75}", f"50% max = {fVolMaxHalf}", f"25% max = {fVolMaxPerc25}", sep='\n   ')

    return maxVolTrunc

def printOrderStatus(order={}, symbTick=None, success=False):
    print(f" {symbTick} orderSuccess = {success}")
    print(getStrJsonPretty(order))

#NOTE: only canceling ‘ALL’ orders is currently supported
def execOpenOrder(bin_client, symbTick, goCancelAll=False, recurs=False):
    funcname = f'<{__filename}> execOpenOrder'
    print(f'\nENTER _ {funcname} _ ')
    print(f'  params: ({bin_client}, {symbTick}, goCancelAll={goCancelAll})')

    arrOrders = arrOrderIds = []
    try:
        arrOrders = bin_clientGetOpenOrders(bin_client, symbTick)
        arrOrderIds = lstGetOpenOrderIDs(arrOrders, symbTick)

        iCntId = len(arrOrderIds)
        if iCntId < 1:
            print(' 0 open orders found')

        strLogID = 'ID' if iCntId == 1 else 'IDs'
        if goCancelAll:
            print(f' RECEIVED {iCntId} order {strLogID} to cancel\n')
            for iOrderID in arrOrderIds:
                print(f'Attempting to cancel order ID: {iOrderID}...')
                order = bin_clientCancelOrder(bin_client, symbTick, iOrderID)
                print(f'Canceled Order:\n{getStrJsonPretty(order)}\n')
            print(f'\n FOUND & Canceled {iCntId} open order {strLogID}: {arrOrderIds}')
        else:
            print(f'\n FOUND (returning) {iCntId} open order {strLogID}: {arrOrderIds}')
    except exceptions.BinanceAPIException as e:
        printException(e, debugLvl=2)
        print(f'ERROR -> BinanceAPIException; checking for recursive trigger (to try again)...')
        if recurs:
            pass
        else:
            print(f'ERROR -> BinanceAPIException; no recursive trigger found; exiting...')
            printEndAndExit(2)
    except Exception as e:
        printException(e, debugLvl=2)
        printEndAndExit(3)

    return arrOrderIds

def execLimitOrder(orderType, symb, symbTick, fVol, strPrice, bin_client, recurs=False):
    funcname = f'<{__filename}> execLimitOrder'
    print(f'\nENTER _ {funcname} _ ')
    print(f'  params: (orderType={orderType}, {symb}, {symbTick}, {fVol}, {strPrice}, {bin_client}, recurs={recurs})')
    
    order = {'ERROR': f"failed to fill '{symbTick}' limit order"}
    orderSuccess = False
    fSymbFinalBal = -1.0
    try:
        if orderType == iOrdSell:
            order = bin_clientGoLimitSell(bin_client, symbTick, fVol, strPrice)
            orderSuccess = True
        if orderType == iOrdBuy:
            order = bin_clientGoLimitBuy(bin_client, symbTick, fVol, strPrice)
            orderSuccess = True

        printOrderStatus(order, symbTick, success=orderSuccess)

        # final balance after order fills executed
        fSymbFinalBal = fGetBalanceForSymb(bin_client, assetSymb=symb, maxPrec=9)
    except exceptions.BinanceAPIException as e:
        printException(e, debugLvl=2)
        print(f'ERROR -> BinanceAPIException; checking for recursive trigger (to try again)...')
        if recurs:
            pass
        else:
            print(f'ERROR -> BinanceAPIException; no recursive trigger found; exiting...')
            printEndAndExit(2)
    except Exception as e:
        printException(e, debugLvl=2)
        printEndAndExit(3)

    return order, fSymbFinalBal, orderSuccess

def execMarketOrder(orderType, symb, symbTick, fVol, bin_client, recurs=False):
    funcname = f'<{__filename}> execMarketOrder'
    print(f'\nENTER _ {funcname} _ ')
    print(f'  params: (orderType={orderType}, {symb}, {symbTick}, {fVol}, {bin_client}, recurs={recurs})')
    
    order = {'ERROR': f"failed to fill '{symbTick}' market order"}
    orderSuccess = False
    fSymbFinalBal = -1.0
    try:
        if orderType == iOrdSell:
            order = bin_clientGoMarketSell(bin_client, symbTick, fVol)
            orderSuccess = True
        if orderType == iOrdBuy:
            order = bin_clientGoMarketBuy(bin_client, symbTick, fVol)
            orderSuccess = True
            
        if orderSuccess:
            strOrderSymb = order['symbol']
            strFirstPrice = order['fills'][0]['price']
            strFirstFilledVol = order['fills'][0]['qty']
            print(f" {strOrderSymb}  first order fill price  = '{strFirstPrice}'")
            print(f" {strOrderSymb}  first order fill volume = '{strFirstFilledVol}'")
        else:
            print(f" {symbTick} orderSuccess = {orderSuccess}")
            print(f" order = {order}")

        # final balance after order fills executed
        fSymbFinalBal = fGetBalanceForSymb(bin_client, assetSymb=symb, maxPrec=9)
    except exceptions.BinanceAPIException as e:
        printException(e, debugLvl=2)
        print(f'ERROR -> BinanceAPIException; checking for recursive trigger (to try again)...')
        if recurs:
            iSec = 0.5
            print(f"FOUND trigger -> recurs={recurs}...", f"waiting {iSec} sec, then trying again...", sep='\n  ')
            time.sleep(iSec)   # wait 0.5 sec.
            fVolMax = getMaxBuyVolForAssetSymb(bin_client, currency='BTC', assetSymb=symb, symbTick=symbTick, maxPrec=2)
            fVol = fVolMax * fInputVolRatio #adjust vol w/ market buy ratio (set w/ flag '-vr')
            fVol = fVol * fPumpVolAdjRatio #adjust volume for rising price pump (set from global constant)
            bTruncate = False
            
            fVol = truncate(fVol, 0)
            bTruncate = True
            
            prin(f"RECURSIVE '--buy-r' flag' detected...", f"set 'fVol' = {fVol}", f"original 'fVolMax' = {fVolMax}", f"... adj w/ input ratio {fInputVolRatio}", f"... adj w/ pump ratio {fPumpVolAdjRatio}", f"... bTruncate = {bTruncate}", sep='\n    ')

            return execMarketOrder(orderType, symb, symbTick, fVol, bin_client, recurs)
        else:
            print(f'ERROR -> BinanceAPIException; no recursive trigger found; exiting...')
            printEndAndExit(2)
    except Exception as e:
        printException(e, debugLvl=2)
        printEndAndExit(3)

    return order, fSymbFinalBal, orderSuccess

def printEndAndExit(exit_code, time_stamps=True):
    funcname = f'<{__filename}> printEndAndExit'
    if exit_code > 0:
        print(f"\nERROR _ {funcname} _ exit_code: {exit_code}")
        if exit_code == 1:
            print(f"\n INPUT param error caught;")
            print(f"  expected ->   [recieved] 'flag'       : [{flag1_rec}] '{flag1}'")
            print(f"  expected ->   [recieved] 'flag' 'val' : [{flag2_rec}] '{flag2}' '{flag2_val}'")
            print(f"  expected ->   [recieved] 'flag'       : [{flag3_rec}] '{flag3}'")
            print(f"  expected ->   [recieved] 'flag'       : [{flag4_rec}] '{flag4}'")
            print(f"  expected ->   [recieved] 'flag' 'val' : [{flag5_rec}] '{flag5}' '{flag5_val}'")
            print(f"  expected ->   [recieved] 'flag'       : [{flag6_rec}] '{flag6}'")
            print(f"  expected ->   [recieved] 'flag' 'val' : [{flag7_rec}] '{flag7}' '{flag7_val}'")
            print(f"  expected ->   [recieved] 'flag' 'val' : [{flag8_rec}] '{flag8}' '{flag8_val}'")
            print(f"  expected ->   [recieved] 'flag'       : [{flag9_rec}] '{flag9}'")
            print(f"  expected ->   [recieved] 'flag'       : [{flag10_rec}] '{flag10}'")
            print(f"  expected ->   [recieved] 'flag'       : [{flag11_rec}] '{flag11}'")
            print(f"  expected ->   [recieved] 'flag'       : [{flag12_rec}] '{flag12}'")
            print(f"  expected ->   [recieved] 'flag'       : [{flag13_rec}] '{flag13}'")
            print(f"  expected ->   [recieved] 'flag'       : [{flag14_rec}] '{flag14}'")
            print(f"  expected ->   [recieved] 'flag'       : [{flag15_rec}] '{flag15}'")
            print()
        if exit_code == 2:
            print(f"\n BINANCE or Value error caught;")
        if exit_code == 3:
            print(f"\n General Exception error caught;")
                
        print(f"\n Example use:", f"  '$ python {__filename} -m --buy -s trx -v 100'", sep='\n')
        print(f"\n For more info, use:", f"  '$ python {__filename} {flagHelp}'", sep='\n')

    global lst_iTimeSec, lst_strTimeSec, lst_strTimeDt
    totExeTime = f"{incExeClock(' <- EXIT')} sec"
    currTimeStamp = getStrTimeNow()
    print('', cStrDivider, f'END _ {__filename} _ sys.exit({exit_code}) __ RestCnt: {iCntRestReq} _ TotTime: {totExeTime} _ TimeStamp: {currTimeStamp}', cStrDivider, '', sep='\n')
    if time_stamps:
        getPrintListStr(lst=lst_strTimeSec, strListTitle=f'Time Stamps: {totExeTime}'), print()
    sys.exit(exit_code)

usage = ("\n*** General Script Manual ***\n\n"
         "USAGE... \n"
         f" {__filename} -> CLI tool for binance limit/market orders  \n"
         " \n"
         "INPUT PARAMS / FLAGS... \n"
         "  --help                       show this help screen (overrides all) \n"
         "  -m                           enable 'market' order (-m | -l required) \n"
         "  -l ['price']                 enable 'limit' order & set price (-m | -l required) \n"
         "  --buy                        enable 'buy' order (--buy | --buy-r | --sell required) \n"
         "  --buy-r                      enable 'buy recursively' for active pump condition (--buy | --buy-r | --sell required) \n"
         "  --sell                       enable 'sell' order (--buy | --buy-r | --sell required) \n"
         "  -c ['currency']              set 'currency' for asset; i.e. 'BTC' in 'TRXBTC' - or - 'USDT' in 'BTCUSDT' (defaults to 'BTC') \n"
         "  -s ['symbol']                set 'symbol' for order; i.e. 'TRX', 'XMR' (required) \n"
         "  --wait-s                     prompt user for 'symbol' input (overrides -s) \n"
         "  --view                       get / calc various ratio vol can buy with BTC bal in binance acct (overrides all) \n"
         "  -v [amount]                  set order volume amount (-v | -vr required) \n"
         "  -vr [ratio]                  set order volume ratio of max available (-v | -vr required) \n"
         "  --set-ls                     set limit sell orders after market buy; REQUIRES -m & (--buy | --buy-r) \n"
         "  --term-launch                launch additional tools (set manually in source code) \n"
         "  --open-orders                display current open orders (overrides all except --view) \n"
         "  --open-orders-cancel         cancel all current open orders (overrides all except --view) \n"
         " \n"
         "EXAMPLES... \n"
         f" '$ python {__filename} --help' \n"
         f" '$ python {__filename} -s BTC -c USDT -vr 1.0 --buy -m --open-orders' \n"
         f" '$ python {__filename} -s BTC -c USDT -vr 1.0 --sell -m --open-orders-cancel' \n"
         f" '$ python {__filename} -s BTC -c USDT -vr 0.95 --buy -m' \n"
         f" '$ python {__filename} -s BTC -c USDT -vr 1.0 --buy -l 7264.0' \n"
         f" '$ python {__filename} -s BTC -c USDT -vr 1.0 --sell -l 7499.97' \n"
         f" '$ python {__filename} -s BTC -c USDT -vr 1.0 --sell -m' \n"
         f" '$ python {__filename} -s trx' -v 100 --buy -l 0.00000217' \n"
         f" '$ python {__filename} -s trx --sell -m' \n"
         f" '$ python {__filename} -m --buy -s trx' -vr 0.5 --set-ls' \n"
         f" '$ python {__filename} -m --buy -s trx' -vr 0.5 --set-ls --term-launch' \n"
         f" '$ python {__filename} -m --buy -s trx' -v 100' \n"
         f" '$ python {__filename} -m --buy -s trx' -vr 0.5' \n"
         f" '$ python {__filename} -m --buy-r -s trx' -vr 0.5' \n"
         f" '$ python {__filename} -m --buy -s trx --view' \n"
         f" '$ python {__filename} -m --buy -s trx --wait-s' \n"
         f" '$ python {__filename} -m --buy -s trx --wait-s --view' \n"
         " . . . \n"
         " \n"
         " exiting... \n"
         )

incExeClock(' <- ENTER')
setActiveLogPaths()
#setApiKeys()

argCnt = len(sys.argv)
if argCnt > 1:
    readCliArgs()
    fVolume = 0.0
    strLimPrice = '0.0'
    
    #required
    bIsMarketOrder = False
    bIsLimitOrder = False
    bIsBuyOrder = False
    bIsBuyOrderRecurs = False
    bIsSellOrder = False
    strAssSymb = None
    strAssCurr = None
    strSymbTick = None

    bViewMaxDetect = False
    bWaitForSymb = False
    bSetLimitOrders = False

    bTermLaunch = False
    bOpenOrders = False
    bOpenOrdersCancel = False
    
    try:
        print(f"\nChecking for '--help' flag...")
        for x in range(0, argCnt):
            argv = sys.argv[x]
            if argv == flagHelp:
                print(f"{cStrDivider}", f" argv[{x}]: '{flagHelp}' detected", f"{cStrDivider}", f"{usage}", f"{cStrDivider}\n", sep='\n')
                sys.exit()
        print(f"Done checking for '--help' flag...")

        setApiKeys()
        #print(f'\nCurrent BTC Balance = {fCurrUSDTBal}')
        
        assetSymb='BTC'
        fCurrBTCBal = fGetBalanceForSymb(client, assetSymb=assetSymb, maxPrec=9)
        print(f'DONE -> Current {assetSymb} Balance = {fCurrBTCBal} BTC')
        
        assetSymb='USDT'
        fCurrUSDTBal = fGetBalanceForSymb(client, assetSymb=assetSymb, maxPrec=3)
        print(f'DONE -> Current {assetSymb} Balance = ${fCurrUSDTBal}')

        print(f'\nChecking CLI flags...')
        for x in range(0, argCnt):
            argv = sys.argv[x].lower()
            if argv == flag1: # '-m'
                flag1_rec = bIsMarketOrder = True
                print(f" '{flag1}' market flag detected; 'bIsMarketOrder' = {bIsMarketOrder}")

            if argv == flag2: # '-l'
                flag2_rec = bIsLimitOrder = True
                argv1 = str(sys.argv[x+1])
                if argv1[0:1] == '-': continue
                flag2_val = argv1
                strLimPrice = str(argv1)
                print(f" '{flag2}' limit flag detected; 'bIsLimitOrder' = {bIsLimitOrder}")
                print(f" '{flag2}' limit flag detected; w/ value = '{flag2_val}'")

            if argv == flag3: # '--buy'
                flag3_rec = bIsBuyOrder = True
                print(f" '{flag3}' buy flag detected; 'bIsBuyOrder' = {bIsBuyOrder}")

            if argv == flag4: # '--sell'
                flag4_rec = bIsSellOrder = True
                print(f" '{flag4}' sell flag detected; 'bIsSellOrder' = {bIsSellOrder}")

            if argv == flag5 and argCnt > x+1 and not bWaitForSymb: # '-s'
                flag5_rec = True
                argv1 = str(sys.argv[x+1])
                if argv1[0:1] == '-': continue
                flag5_val = argv1
                strAssSymb = str(argv1).upper()
                print(f" '{flag5}' asset symbol flag detected; w/ value = '{flag5_val}'")

            if argv == flag6: # '--wait-s'
                flag6_rec = bWaitForSymb = True
                print(f" '{flag6}' wait for symbol flag detected; 'bWaitForSymb' = {bWaitForSymb}")
                strMarker = '============================================================>'
                argv1 = input(f"\n {strMarker} SYMBOL PLEASE? (-s): ")
                flag5_rec = True
                flag5_val = argv1
                strAssSymb = str(argv1).upper()
                print(f"\n '{flag5}' asset symbol flag detected; w/ value = '{flag5_val}'")

            if argv == flag7 and argCnt > x+1: # '-v'
                flag7_rec = True
                argv1 = str(sys.argv[x+1])
                if argv1[0:1] == '-': continue
                flag7_val = argv1
                fVolume = float(argv1)
                print(f" '{flag7}' volume flag detected; w/ value = '{flag7_val}'")
            
            if argv == flag8 and argCnt > x+1: # '-vr'
                flag8_rec = True
                argv1 = str(sys.argv[x+1])
                if argv1[0:1] == '-': continue
                flag8_val = argv1
                fInputVolRatio = float(argv1)
                print(f" '{flag8}' volume ratio flag detected; w/ value = '{flag8_val}'")

            if argv == flag9: # '--buy-r'
                flag9_rec = bIsBuyOrderRecurs = bIsBuyOrder = True
                print(f" '{flag9}' buy recursive flag detected; 'bIsBuyOrder' = {bIsBuyOrder}; 'bIsBuyOrderRecurs' = {bIsBuyOrderRecurs}")

            if argv == flag10: # '--view'
                flag10_rec = bViewMaxDetect = True
                print(f" '{flag10}' view max flag detected; 'bViewMaxDetect' = {bViewMaxDetect}")
            
            if argv == flag11: # '--set-ls'
                flag11_rec = bSetLimitOrders = True
                print(f" '{flag11}' set limit sells flag detected; 'bSetLimitOrders' = {bSetLimitOrders}")
            
            if argv == flag12: # '-c'
                flag12_rec = True
                argv1 = str(sys.argv[x+1])
                if argv1[0:1] == '-': continue
                strAssCurr = flag12_val = argv1
                print(f" '{flag2}' currency flag detected; w/ value = '{flag12_val}'; default was 'BTC'", sep='\n')

            if argv == flag13: # '--term-launch'
                flag13_rec = bTermLaunch = True
                print(f" '{flag13}' set limit sells flag detected; 'bTermLaunch' = {bTermLaunch}")
                    
            if argv == flag14: # '--open-orders'
                flag14_rec = bOpenOrders = True
                print(f" '{flag14}' display current open orders flag detected; 'bOpenOrders' = {bOpenOrders}")

            if argv == flag15: # '--open-orders-cancel'
                flag15_rec = bOpenOrdersCancel = True
                print(f" '{flag15}' cancel all current open orders flag detected; 'bOpenOrdersCancel' = {bOpenOrdersCancel}")

        print(f'DONE checking CLI flags...')
        
        print(f'\nValidating required CLI params...')
        if bIsMarketOrder == bIsLimitOrder: # validate -m | -l (only either 'market' or 'limit used)
            printEndAndExit(1)
        if bIsBuyOrder == bIsSellOrder: # validate --buy | --buy-r | -- sell (only either 'buy' or 'sell' used)
            printEndAndExit(1)
        if flag5_val is None: # validate -s | --wait-s (symbol provided)
            printEndAndExit(1)
        if flag7_val is None and flag8_val is None: # validate -v | -vr (vol or vol ratio provided)
            printEndAndExit(1)
        if bIsLimitOrder and flag2_val is None: # validate -l (price was included)
            printEndAndExit(1)
        print(f'DONE validating required CLI params...\n')

        print(f'\nValidating currency requirement set...')
        if strAssCurr is None:
            print(" currency requirement NOT set... assigning 'BTC'")
            strAssCurr = 'BTC'
        strSymbTick = strAssSymb + strAssCurr
        print(f'  strAssCurr = {strAssCurr}', f'strAssSymb = {strAssSymb}', f'strSymbTick = {strSymbTick}', sep='\n  ')
        print(f'DONE validating currency requirement set...\n')

        # PRIORITY if statement '--view' (overrides all)
        if bViewMaxDetect:
            print(f"PRIORITY flag '{flag10}' detected")

            # set volume precision to 8 decimal places if symbol is 'BTC' (else set to 2 decimal places)
            iPrec = 6 if strAssSymb == 'BTC' else 2
            fVolMax = getMaxBuyVolForAssetSymb(client, currency=strAssCurr, assetSymb=strAssSymb, symbTick=strSymbTick, maxPrec=iPrec)
            print(" exiting...\n")
            printEndAndExit(0)

        # PRIORITY if statement '--open-orders' or '--open-orders-cancel' (overrides all except '--view')
        if bOpenOrders or bOpenOrdersCancel:
            flagDetect = flag14 if not flag15_rec else flag15
            print(f"PRIORITY flag '{flagDetect}' detected")
            arrOrderIds = execOpenOrder(client, symbTick=strSymbTick, goCancelAll=bOpenOrdersCancel)
            print(" exiting...\n")
            printEndAndExit(0)

        if flag8_rec: # '-vr'
            print(f"Volume Ratio flag '{flag8}' detected")
            if bIsSellOrder:
                fSymbBal = fGetBalanceForSymb(client, assetSymb=strAssSymb, maxPrec=9)
                fVolume = fSymbBal * fInputVolRatio
                #fVolume = truncate(fVolume, 0)
                fVolume = truncate(fVolume, 6) if strAssCurr == 'USDT' else truncate(fVolume, 0)
            
            if bIsBuyOrder:
#                iPrec = 2
                # set volume precision to 8 decimal places if symbol is 'BTC' (else set to 2 decimal places)
                iPrec = 6 if strAssSymb == 'BTC' else 2
                price = '-1.0' if strLimPrice is None else strLimPrice
                fVolMax = getMaxBuyVolForAssetSymb(client, currency=strAssCurr, assetSymb=strAssSymb, assetPrice=price, symbTick=strSymbTick, maxPrec=iPrec)
                fVolume = fVolMax * fInputVolRatio
#                fVolume = truncate(fVolume, 0)
                fVolume = truncate(fVolume, iPrec if strAssSymb == 'BTC' else 0)

        if bIsLimitOrder and bIsSellOrder:
            print(f"Limit Order Sell flags '{flag2} {flag4}' detected")
            order, fBalance, success = execLimitOrder(iOrdSell, strAssSymb, strSymbTick, fVolume, strLimPrice, client, recurs=False)
            if success:
                print(f"\nSUCCESSFULLY executed _ LIMIT SELL ORDER\n")
            else:
                print(f" {strSymbTick} success = {success}")
                print(f" {strSymbTick} final bal = {fBalance}\n")

            print(" exiting...\n")
            printEndAndExit(0)

        if bIsLimitOrder and bIsBuyOrder:
            strFlag = '--buy-r' if flag9_rec else '--buy'
            print(f"Limit Order Buy flags '{flag2} {strFlag}' detected")
            order, fBalance, success = execLimitOrder(iOrdBuy, strAssSymb, strSymbTick, fVolume, strLimPrice, client, recurs=False)
            if success:
                print(f"\nSUCCESSFULLY executed _ LIMIT BUY ORDER\n")
            else:
                print(f" {strSymbTick} success = {success}")
                print(f" {strSymbTick} final bal = {fBalance}\n")

            print(" exiting...\n")
            printEndAndExit(0)

        if bIsMarketOrder and bIsSellOrder:
            print('\n', f"Market Order Sell flags '{flag1} {flag4}' detected")
            order, fBalance, success = execMarketOrder(iOrdSell, strAssSymb, strSymbTick, fVolume, client)
            if success:
                strOrderSymb = order['symbol']
                lst_OrderFills = order['fills']
                lst_FillPrices = [f" {i} -> price: '{v['price'].rstrip('0')}'; vol: '{v['qty'].rstrip('0')}'" for i,v in enumerate(lst_OrderFills)]
                iFillCnt = len(lst_OrderFills)
                print(f"\n {strOrderSymb}  all sell orders... (# of fills: {iFillCnt})", *lst_FillPrices, sep='\n  ')
                print(f" {strOrderSymb}  final bal = {fBalance}\n")
                print(f"\nSUCCESSFULLY executed _ MARKET SELL ORDER\n")
            else:
                print(f" {strSymbTick} success = {success}")
                print(f" {strSymbTick} final bal = {fBalance}\n")

            print(" exiting...\n")
            printEndAndExit(0)

        if bIsMarketOrder and bIsBuyOrder:
            strFlag = flag9 if flag9_rec else flag3
            print('\n', f"Market Order Buy flags '{flag1} {strFlag}' detected")
            #note: maybe we should integrate the recursive call here, in a loop?
            order, fBalance, success = execMarketOrder(iOrdBuy, strAssSymb, strSymbTick, fVolume, client, recurs=bIsBuyOrderRecurs)
            strOrderSymb = order['symbol']
            lst_OrderFills = order['fills']
            lst_FillPrices = [f" {i} -> price: '{v['price'].rstrip('0')}'; vol: '{v['qty'].rstrip('0')}'" for i,v in enumerate(lst_OrderFills)]
            lst_FillPricesVal = [v['price'] for i,v in enumerate(lst_OrderFills)]
            iFillCnt = len(lst_OrderFills)
            print(f"\n {strOrderSymb}  all buy orders... (# of fills: {iFillCnt})", *lst_FillPrices, sep='\n  ')
            print(f" {strOrderSymb}  final bal = {fBalance}\n")
            print(f"\nSUCCESSFULLY executed _ MARKET BUY ORDER\n")
            if bSetLimitOrders:
                print(f"Market buy w/ Set Limit Sells flags '{flag1} {strFlag} {flag11}' detected")
                strBuyPrice = lst_FillPricesVal[0]
                if strBuyPrice[-1] == '0': strBuyPrice = strBuyPrice[:-1]
                idxOfDec = strBuyPrice.find('.')
                iPriceDecCnt = len(strBuyPrice[idxOfDec+1:])
                iTrunc = iPriceDecCnt #iTrunc = 7
                
                fSellProfPerc = 0.05
                fBuyPrice = float(strBuyPrice)
                fFullVolume = fBalance
#                fSellRatioProf = 1.0 + fSellProfPerc
#
#                fSellFullVol = truncate(fFullVolume, 0)
#                fSellFullPrice = fBuyPrice * fSellRatioProf
#                strSellHalfPrice = f'%.{iTrunc}f' % fSellFullPrice
#                order, fBalance, success = execLimitOrder(iOrdSell, strAssSymb, strSymbTick, fSellFullVol, strSellHalfPrice, client, recurs=False)

                fSellRatioHalf = 1.25
                fSellRatioQ1 = 1.30
                fSellRatioQ2 = 1.40

                fSellHalfVol = truncate(fFullVolume / 2, 0)
                fSellHalfPrice = truncate(fBuyPrice * fSellRatioHalf, 8)
                strSellHalfPrice = f'%.{iTrunc}f' % fSellHalfPrice
                order, fBalance, success = execLimitOrder(iOrdSell, strAssSymb, strSymbTick, fSellHalfVol, strSellHalfPrice, client, recurs=False)

                fSellQuart1Vol = truncate(fFullVolume / 4, 0)
                fSellQuart1Price = truncate(fBuyPrice * fSellRatioQ1, 8)
                strSellQuart1Price = f'%.{iTrunc}f' % fSellQuart1Price
                order, fBalance, success = execLimitOrder(iOrdSell, strAssSymb, strSymbTick, fSellQuart1Vol, strSellQuart1Price, client, recurs=False)

                fSellQuart2Vol = truncate(fFullVolume / 4, 0)
                fSellQuart2Price = truncate(fBuyPrice * fSellRatioQ2, 8)
                strSellQuart2Price = f'%.{iTrunc}f' % fSellQuart2Price
                order, fBalance, success = execLimitOrder(iOrdSell, strAssSymb, strSymbTick, fSellQuart2Vol, strSellQuart2Price, client, recurs=False)
                print(f"\nSUCCESSFULLY executed _ RATIO LIMIT SELL ORDERS\n")

            print(" exiting...\n")
            printEndAndExit(0)

    except ValueError as e:
        printException(e, debugLvl=0)
        print(f'ERROR -> Exception ValueError; invalid input param (expected a number), exiting...')
        printEndAndExit(2)
    except Exception as e:
        printException(e, debugLvl=2)
        printEndAndExit(3)
    finally:
        if bTermLaunch:
#            strAssSymb = None
#            strAssCurr = None
#            strSymbTick = None

#            if not strBuyPrice: strBuyPrice = '0.0'
            strSymb = strAssSymb

            pyPath = '~/devbtc/git/altcointools/calcprofloss.py'
            strArgs = f'-b {strBuyPrice} -s {strBuyPrice} _symb: {strSymb}'
            launchTerminalPython(pyPath, strArgs)

            pyPath = '~/devbtc/git/altcoins/binance/depthsock.py'
            strArgs = f'{strSymb} -p 10'
            launchTerminalPython(pyPath, strArgs)

            pyPath = '~/devbtc/git/altcoins/binance/depthsock.py'
            strArgs = f'{strSymb} -s 15 -r 1.0 --noasks =={strBuyPrice} ==={strBuyPrice} -t ttys015'
            launchTerminalPython(pyPath, strArgs)

            #pyPath = '~/devbtc/git/altcoins/binance/depthsock.py'
            #strArgs = f'{strSymb} -s 15 -r 1.0'
            #launchTerminalPython(pyPath, strArgs)

            #pyPath = '~/devbtc/git/altcointools/binance/binanceorder.py'
            #strArgs = f'-m -s {strSymb} -c BTC --buy -vr 0.5 --view'
            #launchTerminalPython(pyPath, strArgs)

else:
    printEndAndExit(1)
print(f'\n\n * END _ {__filename} * \n\n')
