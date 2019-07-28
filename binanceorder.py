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
flag1 = '-m'
flag2 = '-l'
flag3 = '--buy'
flag4 = '--sell'
flag5 = '-s'
flag6 = '--wait-symb'
flag7 = '--view-max'

flag1_rec = flag2_rec = flag3_rec = flag4_rec = flag5_rec = False
flag6_rec = flag7_rec = flag8_rec = flag9_rec = flag10_rec = False

flag5_val = None

iOrdNone = 0
iOrdBuy = 1
iOrdSell = 2

fMarketBuyAdjPerc = 0.95

iCntRestReq = 0
lst_iTimeSec = []
lst_strTimeSec = []
lst_strTimeDt = []


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
    incRestCnt(start=True)
    client = Client(api_key, api_secret) # performs binance REST api handshakes
    incRestCnt()

    print(f'DONE getting Binance api keys')

def incExeClock(strInfo=''):
    iNowSec = int(round(time.time()))
    strNowDt = datetime.fromtimestamp(iNowSec)

    lst_iTimeSec.append(iNowSec)
    lst_strTimeSec.append(f'{iNowSec} {strInfo}')
    lst_strTimeDt.append(f'{strNowDt} {strInfo}')
    return lst_iTimeSec[len(lst_iTimeSec)-1] - lst_iTimeSec[0]

def incRestCnt(start=False):
    global iCntRestReq, lst_iTimeSec, lst_strTimeDt
    if not start: iCntRestReq += 1
    strType = 'start' if start else 'end  '
    incExeClock(f' <- {strType} REST Request')

def fGetBalanceForSymb(bin_client, assetSymb='USDT', maxPrec=9):
    incRestCnt(start=True)
    balanceDict = bin_client.get_asset_balance(asset=assetSymb)
    incRestCnt()

    balance = float(balanceDict['free'])
    return balance

def fGetCurrPriceForSymbTick(bin_client, symbTick='BTCUSDT'):
    incRestCnt(start=True)
    tick = bin_client.get_symbol_ticker(symbol=symbTick)
    incRestCnt()

    price = tick['price']
    strPrice = str(price).rstrip('0')
    return float(strPrice)

def getMaxBuyVolForAssetSymb(bin_client, currency='USDT', assetSymb='BTC', symbTick='BTCUSDT', maxPrec=8):
    balance = fGetBalanceForSymb(bin_client, assetSymb=currency)

    print(f'\nGetting max buy volume for {symbTick}...')
    currPrice = fGetCurrPriceForSymbTick(bin_client, symbTick=symbTick)
    maxVol = decimal.Decimal(balance / currPrice)
    maxVolTrunc = truncate(maxVol, maxPrec)

    #print(f' {currency} balance = {decimal.Decimal(balance)}')
    print(f' {currency} balance = {balance}')
    print(f' {symbTick} currPrice = {truncate(currPrice, 8, bDecReturn=True)} | truncate @ maxPrec: 8')
    print(f' {assetSymb} maxVol = {maxVol} | pre-truncate @ maxPrec: {maxPrec}')
    print(f' {assetSymb} maxVol = {maxVolTrunc} | truncate @ maxPrec: {maxPrec}')
    print()
    return maxVolTrunc

def execMarketOrder(orderType, symb, symBTC, fVol, bin_client):
    funcname = '(%s) goBinanceBuyMarket' % (filename,)
    logenter(funcname, ' params: (%s, %s, %.4f, %s)' % (symb,symBTC,fVol,bin_client), tprint=False)
    strTimeNow = getStrLocalDtTradeTime(getTimeSecNow(milli=True), getTimeSecNow(), use_milli_dt=False)
    balance = '<error: failed to get balance>'
    order = '<error: failed to fill order>'
    priceBTCUSDT = '<error: failed to get BTCUSDT price>'
    try:
        loginfo(funcname, 'Executing "order_market_buy"...', simpleprint=True)
        incRestCnt(start=True)
        order = bin_client.order_market_buy(symbol=symBTC,quantity=fVol)
        incRestCnt()
        
        incRestCnt(start=True)
        balance = bin_client.get_asset_balance(asset=symb)
        incRestCnt()
        
        priceBTCUSDT = getCurrPriceBTCUSDT(bin_client)
    except exceptions.BinanceAPIException as e:
        title = "_BUY '%s': %.4f; *ERROR* -> BinanceAPIException [%s]" % (symBTC,fVol,strTimeNow)
        text = 'exception: %s \n\nbalance: %s; \n\nOrder: %s' % (e,balance,order)
        logerror(funcname,' title: %s \n text: %s \n' % (title,text), 'Exception data... \n type(e): %s \n e.args: %s \n e: %s ' % (type(e),e.args,e))
        if bMaxMarketBuy or bRatioMarketBuy:
            iSec = 0.5
            logwarn(funcname, f' bMaxMarketBuy={bMaxMarketBuy} | bRatioMarketBuy={bRatioMarketBuy}... waiting {iSec} sec, then trying again...')
            time.sleep(iSec)   # wait 0.5 sec.
            #fVolume = getMaxBTCBuyVolForAssetSymb(bin_client, assetSymb='USDT')
            dVolumeMax = getMaxBuyVolForAssetSymb(bin_client, currency='BTC', assetSymb=symb, symbTick=symBTC, maxPrec=2)
            fVolume = float(dVolumeMax) * fRatioMarketBuy #adjust volume to market buy ratio (set from input param through flag '-v')
            fVolume = fVolume * fMarketBuyAdjPerc #adjust volume to rising pump value (set from global constant)
            loginfo(filename, f"RECURSIVE '-v' flag w/ 'max' detected ... \n    set 'fVolume' = {fVolume} ... \n    adujusted from {dVolumeMax} ...\n", simpleprint=True)

            return goBinanceBuyMarket(symb,symBTC,fVolume,bin_client)

        notify(title,text,enable=True,popup=True,goPrint=False) # spawn 'display dialog'
        return False
    except Exception as e:
        title = "_BUY '%s': %.4f; *ERROR* [%s]" % (symBTC,fVol,strTimeNow)
        text = 'exception: %s \n\nBalance: %s; \n\nOrder: %s' % (e,balance,order)
        logerror(funcname,' title: %s \n text: %s \n' % (title,text), 'Exception data... \n type(e): %s \n e.args: %s \n e: %s ' % (type(e),e.args,e))
        notify(title,text,enable=True,popup=True,goPrint=False) # spawn 'display dialog'
        return False

    title = '_BUY %s: %.4f; SUCCESS! [%s]' % (symBTC,fVol,strTimeNow)
    logNotify(balance,order,title, btcusdt=priceBTCUSDT)
    return order, balance


def printEndAndExit(exit_code):
    funcname = f'<{__filename}> printEndAndExit'
    if exit_code > 0:
        print(f"{funcname} -> ERROR")
        if exit_code == 1:
            print(f"\n INPUT param error;")
            print(f"  expected -> 'flag' [recieved]: '{flag1}' [{flag1_rec}]")
            print(f"  expected -> 'flag' [recieved]: '{flag2}' [{flag2_rec}]")
            print(f"  expected -> 'flag' [recieved]: '{flag3}' [{flag3_rec}]")
            print(f"  expected -> 'flag' [recieved]: '{flag4}' [{flag4_rec}]")
            print(f"  expected -> 'flag' [recieved] 'val': '{flag5}' [{flag5_rec}] '{flag5_val}'")
            print(f"  expected -> 'flag' [recieved]: '{flag6}' [{flag6_rec}]")
            print(f"  expected -> 'flag' [recieved]: '{flag7}' [{flag7_rec}]")

        print(f"\n Example use:", f"  '$ python {__filename} -m --buy -s trx'", sep='\n')
        print(f"\n For more info, use:", f"  '$ python {__filename} {flagHelp}'", sep='\n')

    global lst_iTimeSec, lst_strTimeSec, lst_strTimeDt
    totExeTime = f"{incExeClock(' <- EXIT')} sec"
    print('', cStrDivider, f'END _ {__filename} _ sys.exit({exit_code}) __ RestCnt: {iCntRestReq} _ TotTime: {totExeTime}', cStrDivider, '', sep='\n')
    getPrintListStr(lst=lst_strTimeSec, strListTitle=f'Time Stamps: {totExeTime}'), print()
    sys.exit(exit_code)

usage = ("\n*** General Script Manual ***\n\n"
         "USAGE... \n"
         f" {__filename} -> CLI tool for binance limit/market orders  \n"
         " \n"
         "INPUT PARAMS / FLAGS... \n"
         " --help                       show this help screen (overrides all) \n"
         " -m                           enable 'market' order (-m | -l required) \n"
         " -l                           enable 'limit' order (-m | -l required) \n"
         " --buy                        enable 'buy' order (--buy | --sell required) \n"
         " --sell                       enable 'sell' order (--buy | --sell required) \n"
         " -s ['symbol']                set 'symbol' for order; i.e. 'TRX', 'XMR' (required) \n"
         " --wait-symb                  prompt user for 'symbol' input (overrides -s) \n"
         " --view-max                   get / calc max vol can buy with BTC bal in binance acct (overrides all) \n"
         " \n"
         "EXAMPLES... \n"
         f" '$ python {__filename} --help' \n"
         f" '$ python {__filename} -m --buy -s trx' \n"
         f" '$ python {__filename} -m --buy -s trx --view-max' \n"
         f" '$ python {__filename} -m --buy -s trx --wait-symb' \n"
         f" '$ python {__filename} -m --buy -s trx --wait-symb --view-max' \n"
         f" '$ python {__filename} -m --sell -s trx' \n"
         " . . . \n"
         " \n"
         " exiting... \n"
         )

#usage = ("\nHELP! HELP! HELP! \n\n"
#         f"DESCRIPTION... {filename} -> CLI tool for binance buy  \n"
#         "      MARKET buy specified volume of specified symbol \n"
#         "      MARKET buy total volume of specified symbol \n"
#         "      view max volume of MARKET buy for specified symbol \n"
#         " \n"
#         "INPUT PARAMS / FLAGS... \n"
#         " -m                           enable 'market' order (required) \n"
#         " -s ['sym']                   set symbol to buy (required) \n"
#         " -v [amnt | 'max']            set volume amount to buy \n"
#         " -v ['1/4' | '2/4' | '3/4']   set volume amount to buy \n"
#         " -v ['max view']              calculate & display max volume amount can buy \n"
#         " -v ['3/4 view']              calculate & display 75% volume amount can buy \n"
#         " -v ['2/4 view']              calculate & display 50% volume amount can buy \n"
#         " -v ['1/4 view']              calculate & display 25% volume amount can buy \n"
#         " \n"
#         "EXAMPLES... \n"
#         " '$ python altbinance_buy.py -m -s trx -v 37' \n"
#         " '$ python altbinance_buy.py -m -s trx -v max' \n"
#         " '$ python altbinance_buy.py -m -s trx -v 3/4' \n"
#         " '$ python altbinance_buy.py -m -s trx -v 2/4' \n"
#         " '$ python altbinance_buy.py -m -s trx -v 1/4' \n"
#         " '$ python altbinance_buy.py -m -s trx -v max view' \n"
#         " '$ python altbinance_buy.py -m -s trx -v 3/4 view' \n"
#         " '$ python altbinance_buy.py -m -s trx -v 2/4 view' \n"
#         " '$ python altbinance_buy.py -m -s trx -v 1/4 view' \n"
#         " . . . \n\n"
#         "NOTE: no 'limit' order integration yet \n"
#         " \n"
#         " exiting... \n"
#         )

incExeClock(' <- ENTER')
setActiveLogPaths()
#setApiKeys()

argCnt = len(sys.argv)
if argCnt > 1:
    readCliArgs()
    fVolume = 0.0
    
    #required
    bIsMarketOrder = False
    bIsLimitOrder = False
    bIsBuyOrder = False
    bIsSellOrder = False
    strAssSymb = None
    strAssCurr = None
    strSymbTick = None

    bViewMaxDetect = False
    
    bWaitForSymb = False
    
    try:
        print(f"\nChecking for '--help' flag...")
        for x in range(0, argCnt):
            argv = sys.argv[x]
            if argv == flagHelp:
                print(f"{cStrDivider}", f" argv[{x}]: '{flagHelp}' detected", f"{cStrDivider}", f"{usage}", f"{cStrDivider}\n", sep='\n')
                sys.exit()
        print(f"Done checking for '--help' flag...")
        
        setApiKeys()
        
        print(f'\nChecking CLI flags...')
        for x in range(0, argCnt):
            argv = sys.argv[x].lower()
            if argv == flag1: # '-m'
                flag1_rec = bIsMarketOrder = True
                print(f" '{flag1}' market flag detected; 'bIsMarketOrder' = {bIsMarketOrder}")

            if argv == flag2: # '-l'
                flag2_rec = bIsLimitOrder = True
                print(f" '{flag2}' limit flag detected; 'bIsLimitOrder' = {bIsLimitOrder}")

            if argv == flag3: # '--buy'
                flag3_rec = bIsBuyOrder = True
                print(f" '{flag3}' limit flag detected; 'bIsBuyOrder' = {bIsBuyOrder}")

            if argv == flag4: # '--sell'
                flag4_rec = bIsSellOrder = True
                print(f" '{flag4}' limit flag detected; 'bIsSellOrder' = {bIsSellOrder}")

            if argv == flag5 and not bWaitForSymb: # '-s'
                flag5_rec = True
                argv1 = str(sys.argv[x+1])
                if argv1[0:1] == '-': continue
                
                flag5_val = argv1
                strAssSymb = str(argv1).upper()
                print(f" '{flag5}' asset symbol flag detected; w/ value: '{flag5_val}'")

            if argv == flag6: # '--wait-symb'
                flag6_rec = bWaitForSymb = True
                print(f" '{flag6}' wait for symbol flag detected; 'bWaitForSymb' = {bWaitForSymb}")
                argv1 = input("\n Symbol Please? (-s): ")
                flag5_rec = True
                flag5_val = argv1
                strAssSymb = str(argv1).upper()
                print(f"\n '{flag5}' asset symbol flag detected; w/ value: '{flag5_val}'")

            if argv == flag7: # '--view-max'
                flag7_rec = bViewMaxDetect = True
                print(f" '{flag7}' view max flag detected; 'bViewMaxDetect' = {bViewMaxDetect}")

        print(f'DONE checking CLI flags...')
        
        print(f'\nValidating required CLI params...')
        if bIsMarketOrder == bIsLimitOrder: # validate only either 'market' or 'limit used
            printEndAndExit(1)
        if bIsBuyOrder == bIsSellOrder: # validate only either 'buy' or 'sell' used
            printEndAndExit(1)
        if flag5_val is None: # validate a symbol was provided
            printEndAndExit(1)
        print(f'DONE validating required CLI params...\n')

        if bViewMaxDetect: # PRIORITY if statement
            if strAssCurr is None: strAssCurr = 'BTC'
            strSymbTick = strAssSymb + strAssCurr
            print(f'strAssSymb = {strAssSymb}')
            print(f'strAssCurr = {strAssCurr}')
            print(f'strSymbTick = {strSymbTick}')
            
            iPrec = 2
            dVolMax = getMaxBuyVolForAssetSymb(client, currency=strAssCurr, assetSymb=strAssSymb, symbTick=strSymbTick, maxPrec=iPrec)
            fVolMax = truncate(dVolMax, iPrec) * 1.0
            fVolMaxAdj = truncate(dVolMax * fMarketBuyAdjPerc, iPrec) #adjust vol from rising pump (set from global constant)
            fVolMaxPerc75 = truncate(dVolMax * 0.75, iPrec)
            fVolMaxHalf = truncate(dVolMax * 0.50, iPrec)
            fVolMaxPerc25 = truncate(dVolMax * 0.25, iPrec)
            print(f" '--view-max' flag detected", f"\n {strAssSymb} volume can buy...", f"  max = {fVolMax}", f"  max-adj ({fMarketBuyAdjPerc*100}%) = {fVolMaxAdj}", f"  75% max = {fVolMaxPerc75}", f"  50% max = {fVolMaxHalf}", f"  25% max = {fVolMaxPerc25}", sep='\n ')
            print("\n\n exiting...\n")
            printEndAndExit(0)

#        if bIsMarketOrder:

    except ValueError as e:
        printException(e, debugLvl=0)
        print(f'ERROR -> invalid input param (expected a number), exiting...')
        printEndAndExit(2)
    except Exception as e:
        printException(e, debugLvl=2)
        printEndAndExit(3)



#    try:
#        print(f'\nChecking CLI flags...')
#        for x in range(0, argCnt):
#            argv = sys.argv[x]
#            if argv == flagHelp:
#                print(f"{cStrDivider}", f" argv[{x}]: '{flagHelp}' detected", f"{cStrDivider}", f"{usage}", f"{cStrDivider}", sep='\n')
#                bHelpDetected = True
#                sys.exit()
#
#            if argv == flag1: # '-b'
#                argv1 = str(sys.argv[x+1])
#                flag1_val = argv1
#                fBuyPrice = float(argv1)
#                print(f" '{flag1}' fBuyPri ce flag detected w/ price: '{fBuyPrice}'")
#
#            if argv == flag2: # '-s'
#                argv1 = str(sys.argv[x+1])
#                flag2_val = argv1
#                fSellPrice = float(argv1)
#                print(f" '{flag2}' fSellPrice flag detected w/ price: '{fSellPrice}'")
#
#        print(f'DONE checking CLI flags...\n')
#        if flag1_val is None or flag1_val is None:
#            printEndAndExit(1)
#
#        goCLI(fBuyPrice, fSellPrice)
#    except ValueError as e:
#        printException(e)
#        print(f'ERROR -> invalid input param (expected a number), exiting...')
#        printEndAndExit(2)
#    except Exception as e:
#        printException(e)
#        printEndAndExit(3)


else:
    printEndAndExit(1)
print(f'\n\n * END _ {__filename} * \n\n')
