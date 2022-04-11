"""
rebalancing: S&P500 Leverage, Dollar Leverage / only date
rebalancing: TQQQ, SOXL, TMF
best result: TQQQ, TMF 2.4 78:22 10% x302
conderable: TQQQ, TMF 1.0 89:11 2% x134
IMPORTANT: stock holdings are increased !!!
"""


import pandas as pd
import os

def syncing_csv(tkrA, tkrB, prd):
    # pathA = "C:/dell/python/backtesting/kiwoom/" + tkrA + "_" + tkrB + "_" + prd + "_synced.csv"
    # pathB = "C:/dell/python/backtesting/kiwoom/" + tkrB + "_" + tkrA + "_" + prd + "_synced.csv"
    # pathA = "Users/joey/Documents/kiwoom" + tkrA + "_" + tkrB + "_" + prd + "_synced.csv"
    # pathB = "Users/joey/Documents/kiwoom" + tkrB + "_" + tkrA + "_" + prd + "_synced.csv"
    pathA = "D:/soxlVr/" + tkrA + "_" + tkrB + "_" + prd + "_synced.csv"
    pathB = "D:/soxlVr/" + tkrB + "_" + tkrA + "_" + prd + "_synced.csv"

    if (os.path.isfile(pathA)==False) or (os.path.isfile(pathB)==False):

        print("syncing")

        dfA = pd.read_csv(tkrA + "_" + prd + ".csv") # read csv file of stock
        dfB = pd.read_csv(tkrB + "_" + prd + ".csv")

        if set(dfA.columns) != set(dfB.columns):
            print("Not matched columns names...")
        else:
            pass

        dfO = pd.DataFrame(columns=dfA.columns) # output Dataframe
        bp = 0 # beginning point

        for i in range(0,len(dfA)):
            srA = dfA.iloc[i]  # read first row of tkrA
            for j in range(bp,len(dfB)):
                srB = dfB.iloc[j]  # read first row of tkrB

                if prd == "1d":
                    if srA[0]==srB[0]:  # if same date
                        dfT = pd.DataFrame({'Date':[srA[0]], 'Open':[srA[1]], 'High':[srA[2]], 'Low':[srA[3]], 'Close':[srA[4]], 'Adj Close':[srA[5]], 'Volume':[srA[6]]})
                        dfO = pd.concat([dfO, dfT], ignore_index = True, axis = 0)
                        bp = j + 1
                        break
                    elif srA[0] < srB[0]:
                        break
                    else:
                        pass
                else:
                    pass

                if (prd=="5m") or (prd=="1m"):
                    if (srA[0]==srB[0]) and (srA[1]==srB[1]):
                        dfT = pd.DataFrame({'Date':[srA[0]], 'Open':[srA[1]], 'High':[srA[2]], 'Low':[srA[3]], 'Close':[srA[4]], 'Adj Close':[srA[5]], 'Volume':[srA[6]]})
                        dfO = pd.concat([dfO, dfT], ignore_index = True, axis = 0)
                        bp = j + 1
                        break
                    elif srA[0] < srB[0]:
                        break
                    else:
                        pass
                else:
                    pass

        dfO.to_csv(tkrA + "_" + tkrB + "_" + prd + "_synced.csv", index=False)

    else:
        pass

def rebalancing():
    dfA = pd.read_csv(tkrA + "_" + tkrB + "_" + prd + "_synced.csv") # read synced csv file of stock
    dfB = pd.read_csv(tkrB + "_" + tkrA + "_" + prd + "_synced.csv")
    dfO = pd.DataFrame(columns=['vA','tkrA','tkrB','threshold','balance']) # output Dataframe

    inv = 100000000     # total investment
    balStckA = 0        # balance of stock of S&P500
    balStckB = 0        # balance of stock of Dollar
    balA = 0            # balance of S&P500
    balB = 0            # balance of Dollar
    balCsh = 0          # balance of cash
    bal = 0             # total balance

    """
    multiplying amount. test virtual asset
    """
    vA = [(1/10) * x for x in range(10,11)] # percentage of virtual asset
    perA = [(1/100) * x for x in range(89,90)] # percentage of tkrA
    thr = [(1/100) * x for x in range(2,3)]  # rebalancing threshold
    # perA = [(1/200) * x for x in range(154,159)] # percentage of tkrA
    # thr = [(1/200) * x for x in range(16,21)]  # rebalancing threshold
    # perA = [0.82]
    # thr = [0.07]

    log = (len(vA) == 1) and (len(perA) == 1) and (len(thr) == 1)

    if prd=="1d":       # set CLOSE PRICE columns
        cls = 4
    elif (prd=="5m") or (prd=="1m"):
        cls = 5
    else:
        pass

    for v in vA:
        for x in perA:
            perB = 1 - x    # percentage of tkrB

            for y in thr:
                if log:
                    print("%5.2f %5.2f %5.2f" % (v, x, y))
                srA = dfA.iloc[0] # first row
                balStckA = (inv*x) // srA[cls] # close price, bought price
                balCsh += ((inv*x) % srA[cls]) # changes
                srB = dfB.iloc[0] # first row
                balStckB = (inv*perB) // srB[cls] # close price, bought price
                balCsh += ((inv*perB) % srB[cls]) # changes

                for i in range(1,len(dfA)):
                # for i in range(1,10):

                    srA = dfA.iloc[i]
                    srB = dfB.iloc[i]
                    balA = balStckA * srA[cls]
                    balB = balStckB * srB[cls]
                    bal = balA + balB + balCsh

                    if ((balA/bal)-x) > y:
                        amtA = ((balA-(bal*x)) // srA[cls]) + 1 # selling amount
                        amtA *= v # virtua Asset Weight
                        if amtA > balStckA:
                            amtA = balStckA
                        else:
                            pass
                        balStckA -= amtA
                        amtB = (amtA*srA[cls] + balCsh) // srB[cls]
                        balStckB += amtB
                        balCsh = (amtA*srA[cls] + balCsh) % srB[cls]

                        if log:
                            print(srA[0], end=',')
                            # print(int(balStckA * srA[cls]),',',int(balStckB * srB[cls]),',',int(balA + balB + balCsh))
                            print(int(balStckA),',',int(balStckB),',',int(balA + balB + balCsh))

                    elif ((balB/bal)-perB) > y:
                        amtB = ((balB-(bal*perB)) // srB[cls]) + 1 # selling amount
                        amtB *= v # virtua Asset Weight
                        if amtB > balStckB:
                            amtB = balStckB
                        else:
                            pass
                        balStckB -= amtB
                        amtA = (amtB*srB[cls] + balCsh) // srA[cls]
                        balStckA += amtA
                        balCsh = (amtB*srB[cls] + balCsh) % srA[cls]

                        if log:
                            print(srA[0], end=', ')
                            # print(int(balStckA * srA[cls]),',',int(balStckB * srB[cls]),',',int(balA + balB + balCsh))
                            print(int(balStckA),',',int(balStckB),',',int(balA + balB + balCsh))

                    else:
                        pass

                balA = balStckA * srA[cls]
                balB = balStckB * srB[cls]
                bal = balA + balB + balCsh

                dfT = pd.DataFrame({'vA':["%5.2f"%(v)], 'tkrA':["%5.2f"%(x)], 'tkrB':["%5.2f"%(perB)], 'threshold':["%5.2f"%(y)], 'balance':["%12d"%(bal)]})
                dfO = pd.concat([dfO, dfT], ignore_index = True, axis = 0)

    dfO.to_csv(tkrA + "_" + tkrB + "_" + prd + "_rebalanced.csv", index=False)

def sorting():
    df = pd.read_csv(tkrA + "_" + tkrB + "_" + prd + "_rebalanced.csv")
    df.sort_values(by=['balance'], inplace=True, ascending=False)
    df.to_csv(tkrA + "_" + tkrB + "_" + prd + "_sorted.csv", index=False)
    print(df.iloc[0])

def main(tkrA, tkrB, prd):
    syncing_csv(tkrA, tkrB, prd)
    syncing_csv(tkrB, tkrA, prd)
    rebalancing()
    sorting()

tkrA = "TQQQ" # 304940 KODEX NASDAQ100
# tkrA = "SOXL" # 304940 KODEX NASDAQ100
tkrB = "TMF" # 304660 KODEX 30 Years Treasury
prd = "1d"

main(tkrA, tkrB, prd)
