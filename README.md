# altcointools
### misc altcoin scripts / potential HFT &amp; analysis / APR &amp; air drops calculations

# binanceorder.py dependencies...
## 'from house_tools import *'
### required: https://github.com/greenhouse/house_tools.git
    clone into same directory as binanceorder.py
        $ cd <dir-of-binanceorder.py>
        $ git clone https://github.com/greenhouse/house_tools.git

## 'import sites' 
### required: sites/__init__.py
    devpath = sites.GLOBAL_PATH_DEV_LOGS
    isepath = sites.GLOBAL_PATH_ISE_LOGS
    api_key = sites.binance_api_key
    api_secret = sites.binance_api_secret

## Usage...
### --help
    *** General Script Manual ***

    USAGE... 
        binanceorder.py -> CLI tool for binance limit/market orders  

    INPUT PARAMS / FLAGS... 
        --help                       show this help screen (overrides all) 
        -m                           enable 'market' order (-m | -l required) 
        -l                           enable 'limit' order (-m | -l required) 
        --buy                        enable 'buy' order (--buy | --sell required) 
        --sell                       enable 'sell' order (--buy | --sell required) 
        -s ['symbol']                set 'symbol' for order; i.e. 'TRX', 'XMR' (required) 
        --wait-symb                  prompt user for 'symbol' input (overrides -s) 
        --view-max                   get / calc max vol can buy with BTC bal in binance acct (overrides all) 

    EXAMPLES... 
        '$ python binanceorder.py --help' 
        '$ python binanceorder.py -m --buy -s trx' 
        '$ python binanceorder.py -m --buy -s trx --view-max' 
        '$ python binanceorder.py -m --buy -s trx --wait-symb' 
        '$ python binanceorder.py -m --buy -s trx --wait-symb --view-max' 
        '$ python binanceorder.py -m --sell -s trx' 
    . . . 

# misc references
### ref: https://tron.network/usdt?lng=en


## ================================================= ##
## _ END 
