filename = 'calcprofloss.py'
cStrDivider = '#===============================================================#'
cStrDividerExcept = '***************************************************************'
print(cStrDivider, f'START _ {filename}', cStrDivider, sep='\n')
import sys
import decimal

flagHelp = '--help'
flag1 = '-b'
flag2 = '-s'
flag1_val = None
flag2_val = None

def calculateProfitLossPercent(fInitial, fFinal):
    step1 = fFinal / fInitial
    step2 = step1 - 1
    if fFinal < fFinal: # loss
        loss = step2 * (-1)
        return loss * 100.0
    else:
        return step2 * 100.0

def goCLI(fBuyPrice, fSellPrice):
    print(f'Calculating ProfitLosss Percent...')
    profLoss = calculateProfitLossPercent(fBuyPrice, fSellPrice)
    
    buyPrice = round(decimal.Decimal(fBuyPrice), 8)
    sellPrice = round(decimal.Decimal(fSellPrice), 8)
    profLoss = round(decimal.Decimal(profLoss), 2)
    strMarker = '------------------------------------------------------------>'
    print(f' {strMarker} Buy Price: {buyPrice}')
    print(f' {strMarker} Sell Price: {sellPrice}')
    if fSellPrice > fBuyPrice:
        print(f' {strMarker} Profit: {profLoss}%')
    else:
        print(f' {strMarker} Loss: {profLoss}%')

    print(f'DONE calculating ProfitLosss Percent...')
    printEndAndExit(0)

def readCliArgs():
    funcname = f'<{filename}> readCliArgs'
    #print(f'\n{funcname} _ ENTER\n')
    print(f'\nReading CLI args...')
    argCnt = len(sys.argv)
    print(' Number of arguments: %i' % argCnt)
    print(' Argument List: %s' % str(sys.argv))
    for idx, val in enumerate(sys.argv):
        print(' Argv[%i]: %s' % (idx,str(sys.argv[idx])))
    print(f'DONE reading CLI args...')
    #print(f'\n{funcname} _ EXIT\n')

def printException(e):
    print('', cStrDividerExcept, f' Exception Caught: {e}', cStrDividerExcept, sep='\n')

def printEndAndExit(exit_code):
    funcname = f'<{filename}> printEndAndExit'
    if exit_code > 0:
        print(f"{funcname} -> ERROR")
        if exit_code == 1:
            print(f"\n INPUT param error;")
            print(f"  flag expected [recieved]: '{flag1} [{flag1_val}]'")
            print(f"  flag expected [recieved]: '{flag2} [{flag2_val}]'")

        print(f"\n Example use:", f"  '$ python {filename} -b 100 -s 200'", sep='\n')
        print(f"\n For more info, use:", f"  '$ python {filename} {flagHelp}'", sep='\n')
              
    print('', cStrDivider, f'END _ {filename} _ sys.exit({exit_code})', cStrDivider, '', sep='\n')
    sys.exit(exit_code)

usage = ("\nHELP! HELP! HELP! \n\n"
         "USAGE... \n"
         f" {filename} -> CLI tool to calculate percent profit or loss based on input params  \n"
         " \n"
         "INPUT PARAMS / FLAGS... \n"
         " -b [float]   set buy price (required)  \n"
         " -s [float]   set sell price (required) \n"
         " \n"
         "EXAMPLES... \n"
         " '$ python calcprofloss -b [float] -s [float]' \n"
         " . . . \n"
         " \n"
         " exiting... \n"
         )

argCnt = len(sys.argv)
if argCnt > 1:
    readCliArgs()
    bHelpDetected = False
    fBuyPrice = 0.0
    fSellPrice = 0.0

    try:
        print(f'\nChecking CLI flags...')
        for x in range(0, argCnt):
            argv = sys.argv[x]
            if argv == flagHelp:
                print(f"{cStrDivider}", f" argv[{x}]: '{flagHelp}' detected", f"{cStrDivider}", f"{usage}", f"{cStrDivider}", sep='\n')
                bHelpDetected = True
                sys.exit()

            if argv == flag1: # '-b'
                argv1 = str(sys.argv[x+1])
                flag1_val = argv1
                fBuyPrice = float(argv1)
                print(f" '{flag1}' fBuyPrice flag detected w/ price: '{fBuyPrice}'")

            if argv == flag2: # '-s'
                argv1 = str(sys.argv[x+1])
                flag2_val = argv1
                fSellPrice = float(argv1)
                print(f" '{flag2}' fSellPrice flag detected w/ price: '{fSellPrice}'")

        print(f'DONE checking CLI flags...\n')
        if flag1_val is None or flag1_val is None:
            printEndAndExit(1)

        goCLI(fBuyPrice, fSellPrice)
    except ValueError as e:
        printException(e)
        print(f'ERROR -> invalid input param (expected a number), exiting...')
        printEndAndExit(2)
    except Exception as e:
        printException(e)
        printEndAndExit(3)
        #print type(e)       # the exception instance
        #print e.args        # arguments stored in .args
        #print e             # __str__ allows args to be printed directly
else:
    printEndAndExit(1)
print(f'\n\n * END _ {filename} * \n\n')
