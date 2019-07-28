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
flag6 = '--wait-symb'
flag7 = '-v' # volume
flag8 = '-vr' # volume ratio
flag10 = '--view-max'

flag1_rec = flag2_rec = flag3_rec = flag4_rec = flag5_rec = False
flag6_rec = flag7_rec = flag8_rec = flag9_rec = flag10_rec = False

flag5_val = None
flag7_val = None
flag8_val = None

iOrdNone = 0
iOrdBuy = 1
iOrdSell = 2
iOrdBuyLimSell = 3

fMarketBuyAdjPerc = 0.95

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
    balance = fCurrBTCBal
    if currency != 'BTC':
        balance = fGetBalanceForSymb(bin_client, assetSymb=currency)

    print(f'\nGetting max buy volume for {symbTick}...')
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
    fVolMaxAdj = truncate(maxVolTrunc * fMarketBuyAdjPerc, iPrec) #adjust vol from rising pump (set from global constant)
    fVolMaxPerc75 = truncate(maxVolTrunc * 0.75, iPrec)
    fVolMaxHalf = truncate(maxVolTrunc * 0.50, iPrec)
    fVolMaxPerc25 = truncate(maxVolTrunc * 0.25, iPrec)
    print(f"  {assetSymb} volume can buy...", f"max = {fVolMax}", f"max-adj ({fMarketBuyAdjPerc*100}%) = {fVolMaxAdj}", f"75% max = {fVolMaxPerc75}", f"50% max = {fVolMaxHalf}", f"25% max = {fVolMaxPerc25}", sep='\n   ')

    return maxVolTrunc

def execMarketOrder(orderType, symb, symBTC, fVol, bin_client):
    funcname = '<{__filename}> execMarketOrder'
    print(f'{funcname} _ ENTER')
    print(f' params: ({orderType}, {symb}, {symBTC}, {fVol}, {bin_client})')
    balance = '<error: failed to get balance>'
    order = '<error: failed to fill order>'
    try:
        if orderType == iOrdBuy:
            print('Executing "order_market_buy"...')
            incRestCnt(start=True)
            order = bin_client.order_market_buy(symbol=symBTC,quantity=fVol)
            incRestCnt()
    except exceptions.BinanceAPIException as e:
        printException(e, debugLvl=2)
        print(f'ERROR -> BinanceAPIException; checking for recursive trigger (to try again)...')
        if bMaxMarketBuy or bRatioMarketBuy:
            iSec = 0.5
            print(f"FOUND trigger -> bMaxMarketBuy={bMaxMarketBuy} | bRatioMarketBuy={bRatioMarketBuy}...", f"waiting {iSec} sec, then trying again...", sep='\n  ')
            time.sleep(iSec)   # wait 0.5 sec.
            dVolMax = getMaxBuyVolForAssetSymb(bin_client, currency='BTC', assetSymb=symb, symbTick=symBTC, maxPrec=2)
            fVol = float(dVolMax) * fRatioMarketBuy #adjust vol w/ market buy ratio (set from input param through flag '-v')
            fVol = fVol * fMarketBuyAdjPerc #adjust volume for rising price pump (set from global constant)
            prin(f"RECURSIVE '-v' flag w/ 'max' detected ...", f"set 'fVol' = {fVol} ...", f"adujusted from {dVolMax} ...", sep='\n    ')

            return execMarketOrder(orderType, symb, symBTC, fVol, bin_client)
        else:
            print(f'ERROR -> BinanceAPIException; no recursive trigger found; exiting...')
            printEndAndExit(2)
    except Exception as e:
        printException(e, debugLvl=2)
        printEndAndExit(3)

    return order, balance

def printEndAndExit(exit_code):
    funcname = f'<{__filename}> printEndAndExit'
    if exit_code > 0:
        print(f"{funcname} -> ERROR")
        if exit_code == 1:
            print(f"\n INPUT param error;")
            print(f"  expected -> 'flag' [recieved]      : '{flag1}' [{flag1_rec}]")
            print(f"  expected -> 'flag' [recieved]      : '{flag2}' [{flag2_rec}]")
            print(f"  expected -> 'flag' [recieved]      : '{flag3}' [{flag3_rec}]")
            print(f"  expected -> 'flag' [recieved]      : '{flag4}' [{flag4_rec}]")
            print(f"  expected -> 'flag' [recieved] 'val': '{flag5}' [{flag5_rec}] '{flag5_val}'")
            print(f"  expected -> 'flag' [recieved]      : '{flag6}' [{flag6_rec}]")
            print(f"  expected -> 'flag' [recieved] 'val': '{flag7}' [{flag7_rec}] '{flag7_val}'")
            print(f"  expected -> 'flag' [recieved]      : '{flag10}' [{flag10_rec}]")

        print(f"\n Example use:", f"  '$ python {__filename} -m --buy -s trx -v 100'", sep='\n')
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
         "  --help                       show this help screen (overrides all) \n"
         "  -m                           enable 'market' order (-m | -l required) \n"
         "  -l                           enable 'limit' order (-m | -l required) \n"
         "  --buy                        enable 'buy' order (--buy | --sell required) \n"
         "  --sell                       enable 'sell' order (--buy | --sell required) \n"
         "  -s ['symbol']                set 'symbol' for order; i.e. 'TRX', 'XMR' (required) \n"
         "  --wait-symb                  prompt user for 'symbol' input (overrides -s) \n"
         "  --view-max                   get / calc max vol can buy with BTC bal in binance acct (overrides all) \n"
         "  -v [amount]                  set volume amount for order (-v | -vr required) \n"
         "  -vr [ratio]                  set volume ratio of max for order (-v | -vr required) \n"
         " \n"
         "EXAMPLES... \n"
         f" '$ python {__filename} --help' \n"
         f" '$ python {__filename} -m --buy -s trx' -v 100 \n"
         f" '$ python {__filename} -m --buy -s trx' -vr 0.5 \n"
         f" '$ python {__filename} -m --buy -s trx --view-max' \n"
         f" '$ python {__filename} -m --buy -s trx --wait-symb' \n"
         f" '$ python {__filename} -m --buy -s trx --wait-symb --view-max' \n"
         f" '$ python {__filename} -m --sell -s trx' \n"
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
    fVolRatio = 0.0
    
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
        fCurrBTCBal = fGetBalanceForSymb(client, assetSymb='BTC', maxPrec=9)
        print(f'\nCurrent BTC Balance = {fCurrBTCBal}')

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

            if argv == flag5 and argCnt > x+1 and not bWaitForSymb: # '-s'
                flag5_rec = True
                argv1 = str(sys.argv[x+1])
                if argv1[0:1] == '-': continue
                flag5_val = argv1
                strAssSymb = str(argv1).upper()
                print(f" '{flag5}' asset symbol flag detected; w/ value = '{flag5_val}'")

            if argv == flag6: # '--wait-symb'
                flag6_rec = bWaitForSymb = True
                print(f" '{flag6}' wait for symbol flag detected; 'bWaitForSymb' = {bWaitForSymb}")
                argv1 = input("\n Symbol Please? (-s): ")
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
                flag8_val = flag7_val = argv1
                fVolRatio = float(argv1)
                print(f" '{flag8}' volume ratio flag detected; w/ value = '{flag8_val}'")

            if argv == flag10: # '--view-max'
                flag10_rec = bViewMaxDetect = True
                print(f" '{flag10}' view max flag detected; 'bViewMaxDetect' = {bViewMaxDetect}")

        print(f'DONE checking CLI flags...')
        
        print(f'\nValidating required CLI params...')
        if bIsMarketOrder == bIsLimitOrder: # validate -m | -l (only either 'market' or 'limit used)
            printEndAndExit(1)
        if bIsBuyOrder == bIsSellOrder: # validate --buy | -- sell (only either 'buy' or 'sell' used)
            printEndAndExit(1)
        if flag5_val is None or flag7_val is None: # validate -s & -v (symbol & volume provided)
            printEndAndExit(1)
        print(f'DONE validating required CLI params...\n')

        if bViewMaxDetect: # PRIORITY if statement
            print(f"PRIORITY flag '--view-max' detected")
            if strAssCurr is None: strAssCurr = 'BTC'
            strSymbTick = strAssSymb + strAssCurr
            print(f' strAssSymb = {strAssSymb}', f'strAssCurr = {strAssCurr}', f'strSymbTick = {strSymbTick}', sep='\n ')
            
            iPrec = 2
            fVolMax = getMaxBuyVolForAssetSymb(client, currency=strAssCurr, assetSymb=strAssSymb, symbTick=strSymbTick, maxPrec=iPrec)
            print("\n\n exiting...\n")
            printEndAndExit(0)

        if flag8_rec: # '-vr'
            print('TESTING... flag8_rec...')
            if strAssCurr is None: strAssCurr = 'BTC'
            strSymbTick = strAssSymb + strAssCurr
            print(f' strAssSymb = {strAssSymb}', f'strAssCurr = {strAssCurr}', f'strSymbTick = {strSymbTick}', sep='\n ')
            
            iPrec = 2
            fVolMax = getMaxBuyVolForAssetSymb(client, currency=strAssCurr, assetSymb=strAssSymb, symbTick=strSymbTick, maxPrec=iPrec)
            fVolume = fVolMax * fVolRatio
            print(f'TESTING... fVolume = {fVolume}; exiting...')
            sys.exit()

        if bIsMarketOrder:
            #note: maybe we should integrate the recursive call here, in a loop?
            print('(bIsMarketOrder) _ TESTING... exiting...')
            sys.exit()
            #execMarketOrder(iOrdBuy, strAssSymb, strSymbTick, fVolume, client)

    except ValueError as e:
        printException(e, debugLvl=0)
        print(f'ERROR -> Exception ValueError; invalid input param (expected a number), exiting...')
        printEndAndExit(2)
    except Exception as e:
        printException(e, debugLvl=2)
        printEndAndExit(3)
else:
    printEndAndExit(1)
print(f'\n\n * END _ {__filename} * \n\n')
