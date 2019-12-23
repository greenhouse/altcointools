__filename = 'altlauncher.py'
cStrDivider = '#================================================================#'
print('', cStrDivider, f'START _ {__filename}', cStrDivider, '', sep='\n')
from house_tools import *
print(f"IMPORTs complete:- STARTING -> file '{__filename}' . . . \n", sep='')

flagHelp = '--help'
flag1 = '-str' # market
lst_flags = [flagHelp, flag1]

usage = ("\n*** General Script Manual ***\n\n"
         "USAGE... \n"
         f" {__filename} -> CLI tool for... launching altcoin tools synchronously  \n"
         " \n"
         "INPUT PARAMS / FLAGS... \n"
         "  --help                       show this help screen (overrides all) \n"
         "  -str ['input']               set string input... \n"
         " \n"
         "EXAMPLES... \n"
         f" '$ python {__filename} --help' \n"
         f" '$ python {__filename} -str 'hello world' \n"
         " . . . \n"
         " \n"
         " exiting... \n"
         )

def checkPriorityFlagsAndExit():
    print('', f"Checking for '--help' flag...", sep='\n')
    for x in range(0, argCnt):
        argv = sys.argv[x]
        if argv == flagHelp:
            print(f"{cStrDivider}", f" argv[{x}]: '{flagHelp}' detected", f"{cStrDivider}", f"{usage}", f"{cStrDivider}\n", sep='\n')
            printEndAndExit(__filename, exit_code=0)
    print('', f"Done checking for '--help' flag...", '\n')


readCliArgs()
argCnt = len(sys.argv)
if argCnt > 1:
    strInput = None
    try:
        checkPriorityFlagsAndExit()

        print(f'Checking CLI flags...')
        for x in range(0, argCnt):
            argv = sys.argv[x].lower()
            if argv == flag1: # '-str'
                print(f" '{flag1}' string input flag detected; executing 'randomizeString' on remaining args")
                strArgRemain = ' '.join(sys.argv[x+1:])
                strInput = strArgRemain
        print('\n', f'DONE checking CLI flags...', '\n')

        if strInput is not None:
            strOutput = randomizeString(strInput)
            print('\n', f'randomized string: {strOutput}')
            printEndAndExit(__filename, exit_code=0)
        else:
            print("ERROR -> strInput is None;")
            printEndAndExit(__filename, exit_code=1)
    except Exception as e:
        printException(e, debugLvl=2)
        printEndAndExit(__filename, exit_code=2)

print('', f"*** ERROR -> invalid input param... ***", "expected flags:", *lst_flags, "\nexiting...", sep='\n')
printEndAndExit(__filename, exit_code=3)
