print('GO tronaprcalc.py -> starting IMPORTs')
import sys
cStrDivider = '#===============================================================#'

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

def goCLI(amntUSDT):
    print(f"\n\n CALCULATING earnings for USDT ${amntUSDT} 'calcEarnings'")
    earnginsUSDT = calcEarnings(startUSDT=amntUSDT, percAPR=100.0, numDays=1)
    earnginsUSDT = calcEarnings(startUSDT=earnginsUSDT, percAPR=50.0, numDays=1)
    earnginsUSDT = calcEarnings(startUSDT=earnginsUSDT, percAPR=15.0, numDays=10)
    earnginsUSDT = calcEarnings(startUSDT=earnginsUSDT, percAPR=3.0, numDays=19)

def printEndAndExit(exit_code):
    print(f'\n\n END _ tronaprcalc.py _ sys.exit({exit_code})\n\n')
    sys.exit(exit_code)

#===========================================================================#
#===========================================================================#
usage = (":- USAGE examples... \n\n"
         "1) ‘$ python tronaprcalc.py -usdt [amnt]’ \n"
         "      - cacluate & print specified earnings for specicied amount '-usdt [amnt] \n"
         "      - ref: https://tron.network/usdt?lng=en \n"
         "      - compound interest equation       \n\n"
         "         Time: 1 Day loop              \n"
         "          earned = sum * 100% / 365.0  \n"
         "          sum = sum + earned           \n\n"
         "         Time: 1 Day loop              \n"
         "          earned = sum * 50% / 365.0  \n"
         "          sum = sum + earned           \n\n"
         "         Time: 10 Day loop              \n"
         "          earned = sum * 15% / 365.0  \n"
         "          sum = sum + earned           \n\n"
         "         Time: 19 Day loop              \n"
         "          earned = sum * 3% / 365.0  \n"
         "          sum = sum + earned          \n\n"
         "2) examples... \n"
         "      - '$ python tronaprcalc.py -usdt 100' \n"
         "      - . . . \n\n"
         " exiting... \n"
         )

print('\nChecking CLI flags...')
argCnt = len(sys.argv)
if argCnt > 1:
    for x in range(0, argCnt):
        argv = sys.argv[x]
        if argv == '--help':
            print(f" {cStrDivider} \n argv[1]: '--help' detected \n{cStrDivider} \n{usage} \n{cStrDivider} \n\n")
            printEndAndExit(0)
        if argv == '-usdt':
            if argCnt > x+1:
                try:
                    argv1 = float(sys.argv[x+1])
                    fUSDT = argv1
                    goCLI(fUSDT)
                    printEndAndExit(0)
                except ValueError as ex:
                    print(f'Exception Caught: {ex}')
                    print(f'ERROR -> invalid input param (expected a number), exiting...')
                    print(f"Example: \n $ python tronaprcalc.py -usdt 100' \n")
                    printEndAndExit(2)
            else:
                print(f"ERROR -> missing input param '-usdt [amntUSDT]', exiting...")
                print(f"Example: \n $ python tronaprcalc.py -usdt 100' \n")
                printEndAndExit(1)

print(f"ERROR -> invalid input param (expected flag '-usdt' | '--help'), exiting...")
printEndAndExit(1)


