
print('\n\n START _ tronapr.py\n')
cStrDivider = '#===============================================================#'

eg_startBTT = 470847 # TronWallet
serg_startBTT = 182591 # TronWallet
currBTTTRX = 0.038904 # TronWallet

currBTTBTC = 0.00000009 # Binance
currTRXBTC = 0.0000024 # Binance

currBTCUSDT = 10229 # BitKeep
currTRXUSDT = 0.02462 # BitKeep

startUSD = 423

def tronWallet_BTT_TRX(amntBTT, priceTRX):
    return amntBTT * priceTRX

def bitKeep_TRX_USDT(amntTRX, priceUSDT):
    return amntTRX * priceUSDT

def binance_BTT_BTC(amntBTT, priceBTC):
    return amntBTT * priceBTC

def bitKeep_BTC_USDT(amntBTC, priceUSDT):
    return amntBTC * priceUSDT

def binance_BTC_TRX(amntBTC, priceTRX):
    return amntBTC / currTRXBTC

def tronWalletBTT_to_bitKeepUSDT(startBTT):
    print(cStrDivider)
    print("TronWallet BTT -> TronWallet TRX -> BitKeeper USDT")
    print(f'  TronWallet BTT = {startBTT}')
    tronWalletTRX = tronWallet_BTT_TRX(startBTT, currBTTTRX)
    print(f'  TronWallet TRX = {tronWalletTRX}')
    bitKeepUSDT = bitKeep_TRX_USDT(tronWalletTRX, currTRXUSDT)
    print(f'  BitKeep USDT = {bitKeepUSDT}')
    print(cStrDivider)
    
    earnginsUSDT = calcEarnings(startUSDT=bitKeepUSDT, percAPR=100.0, numDays=1)
    earnginsUSDT = calcEarnings(startUSDT=earnginsUSDT, percAPR=50.0, numDays=1)
    earnginsUSDT = calcEarnings(startUSDT=earnginsUSDT, percAPR=15.0, numDays=10)
    earnginsUSDT = calcEarnings(startUSDT=earnginsUSDT, percAPR=3.0, numDays=19)
    print(cStrDivider)
    
    print(cStrDivider)
    print("TronWallet BTT -> Binance BTC -> BitKeeper USDT")
    print(f'  TronWallet BTT = {startBTT}')
    binanceBTC = binance_BTT_BTC(startBTT, currBTTBTC)
    print(f'  Binance BTC = {binanceBTC}')
    bitKeepUSDT = bitKeep_BTC_USDT(binanceBTC, currBTCUSDT)
    print(f'  BitKeep USDT = {bitKeepUSDT}')
    print(cStrDivider)
    
    earnginsUSDT = calcEarnings(startUSDT=bitKeepUSDT, percAPR=100.0, numDays=1)
    earnginsUSDT = calcEarnings(startUSDT=earnginsUSDT, percAPR=50.0, numDays=1)
    earnginsUSDT = calcEarnings(startUSDT=earnginsUSDT, percAPR=15.0, numDays=10)
    earnginsUSDT = calcEarnings(startUSDT=earnginsUSDT, percAPR=3.0, numDays=19)
    print(cStrDivider)
    
    print(cStrDivider)
    print("TronWallet BTT -> Binance BTC -> Binance TRX -> BitKeeper USDT")
    print(f'  TronWallet BTT = {startBTT}')
    binanceBTC = binance_BTT_BTC(startBTT, currBTTBTC)
    print(f'  Binance BTC = {binanceBTC}')
    binanceTRX = binance_BTC_TRX(binanceBTC, currTRXBTC)
    print(f'  Binance TRX = {binanceTRX}')
    bitKeepUSDT = bitKeep_TRX_USDT(tronWalletTRX, currTRXUSDT)
    print(f'  BitKeep USDT = {bitKeepUSDT}')
    print(cStrDivider)
    
    earnginsUSDT = calcEarnings(startUSDT=bitKeepUSDT, percAPR=100.0, numDays=1)
    earnginsUSDT = calcEarnings(startUSDT=earnginsUSDT, percAPR=50.0, numDays=1)
    earnginsUSDT = calcEarnings(startUSDT=earnginsUSDT, percAPR=15.0, numDays=10)
    earnginsUSDT = calcEarnings(startUSDT=earnginsUSDT, percAPR=3.0, numDays=19)
    print(cStrDivider)
    print(cStrDivider)
    print(cStrDivider)

def calcEarnings(startUSDT, percAPR, numDays):
    print(cStrDivider)
    print(f'\ncalcEarnings.. {numDays} days @ {percAPR}% compound...')
    print(f' startUSDT: {startUSDT}; percAPR: {percAPR}; numDays: {numDays}')
    sum = float(startUSDT)
    endUSDT = 0.0
    for x in range(1, numDays+1):
        print(f'\n day {x}...')
        print(f'  curr sum: {sum}')
        
        apr = float(percAPR) / 100.0
        earned = float(sum) * float(apr) / 365.0
        sum = sum + earned
        
        print(f'  earned: {earned}')
        print(f'  day end sum: {sum}')

    endUSDT = sum
    return endUSDT

print("\n\nEG options _ 'tronWalletBTT_to_bitKeepUSDT'")
tronWalletBTT_to_bitKeepUSDT(eg_startBTT)

#print("\n\nSERG options _ 'tronWalletBTT_to_bitKeepUSDT'")
#tronWalletBTT_to_bitKeepUSDT(serg_startBTT)

straightUSDAmnt = '100000'
print(f"\n\n other straigh USDT ${straightUSDAmnt} 'calcEarnings'")
earnginsUSDT = calcEarnings(startUSDT=straightUSDAmnt, percAPR=100.0, numDays=1)
earnginsUSDT = calcEarnings(startUSDT=earnginsUSDT, percAPR=50.0, numDays=1)
earnginsUSDT = calcEarnings(startUSDT=earnginsUSDT, percAPR=15.0, numDays=10)
earnginsUSDT = calcEarnings(startUSDT=earnginsUSDT, percAPR=3.0, numDays=19)


print('\n\n END _ tronapr.py\n\n')
