"""
rebalancing: TQQQ, TMF / 2010~2021 210x / Wow !!!
deploy priceRebalancing
"""


import pandas as pd
import os

def syncing_csv(tkrA, tkrB, prd):
    pathA = "C:/dell/python/backtesting/kiwoom/" + tkrA + "_" + tkrB + "_" + prd + "_synced.csv"
    pathB = "C:/dell/python/backtesting/kiwoom/" + tkrB + "_" + tkrA + "_" + prd + "_synced.csv"
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
            srA = dfA.iloc[i]
            for j in range(bp,len(dfB)):
                srB = dfB.iloc[j]

                if prd == "1d":
                    if srA[0]==srB[0]:
                        dfO = dfO.append(srA, ignore_index=True)
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
                        dfO = dfO.append(srA, ignore_index=True)
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
    dfO = pd.DataFrame(columns=['tkrA','tkrB','gap','trns','bal']) # output Dataframe

    inv = 100000000 # total investment
    balStckA = 0    # balance of stock of S&P500
    balStckB = 0    # balance of stock of Dollar
    balA = 0        # balance of S&P500
    balB = 0        # balance of Dollar
    balCsh = 0      # balance of cash
    bal = 0         # total balance

    gap = [(5/100) * x for x in range(20,201)] # price gap between TQQQ and TMF
    trns = [(5/100) * x for x in range(1,20)]  # selling transaction amount
    # gap = [(1/100) * x for x in range(65,66)] # price gap between TQQQ and TMF
    # trns = [(1/100) * x for x in range(55,56)]  # selling transaction amount

    op = 1 # open price
    if prd=="1d":       # set CLOSE PRICE columns
        cls = 4
    elif (prd=="5m") or (prd=="1m"):
        cls = 5
    else:
        pass

    for x in gap:
        for y in trns:
            print("%5.2f %5.2f" % (x, y))
            srA = dfA.iloc[0] # first row
            srB = dfB.iloc[0] # first row
            balStckA = (inv/2) // srA[op] # bought price = open price. more expensive stock first
            balStckB = (balStckA*srA[op]) // srB[op] # bought price = open price
            balCsh = inv - ((balStckA*srA[op])+(balStckB*srB[op])) # changes
            trnsA = srA[op]
            trnsB = srB[op]

            for i in range(1,len(dfA)):
            # for i in range(1,20):
                srA = dfA.iloc[i] # from second row
                srB = dfB.iloc[i] # from second row
                balA = balStckA * srA[op]
                balB = balStckB * srB[op]
                bal = balA + balB + balCsh

                if ((srA[op]/trnsA)-(srB[op]/trnsB)) > x: # TQQQ up, TMF down
                    amtA = ((balA*y) // srA[op]) + 1 # selling amount
                    balStckA -= amtA
                    amtB = (amtA*srA[op] + balCsh) // srB[op]
                    balStckB += amtB
                    balCsh = (amtA*srA[op] + balCsh) % srB[op]
                    trnsA = srA[op]
                    trnsB = srB[op]

                    # print(srA[0], end=', ')
                    # print("%4.1f"%((balStckA*srA[cls])/(balA+balB+balCsh)*100), "%4.1f"%((balStckB*srB[cls])/(balA+balB+balCsh)*100), int(balA+balB+balCsh))

                elif ((srB[op]/trnsB)-(srA[op]/trnsA)) > x: # TMF up, TQQQ down
                    amtB = ((balB*y) // srB[op]) + 1 # selling amount
                    balStckB -= amtB
                    amtA = (amtB*srB[op] + balCsh) // srA[op]
                    balStckA += amtA
                    balCsh = (amtB*srB[op] + balCsh) % srA[op]
                    trnsA = srA[op]
                    trnsB = srB[op]

                    # print(srA[0], end=', ')
                    # print("%4.1f"%((balStckA*srA[cls])/(balA+balB+balCsh)*100), "%4.1f"%((balStckB*srB[cls])/(balA+balB+balCsh)*100), int(balA+balB+balCsh))

                else:
                    pass

            balA = balStckA * srA[cls]
            balB = balStckB * srB[cls]
            bal = balA + balB + balCsh
            dfO = dfO.append({'tkrA':"%4.1f"%(balA/bal*100),'tkrB':"%4.1f"%(balB/bal*100),'gap':"%4.2f"%(x*100),'trns':"%4.1f"%(y*100),'bal':"%12d"%(bal)}, ignore_index=True) # output Dataframe
            # if (bal > (inv*150)):
            #     dfO = dfO.append({'tkrA':"%5.2f"%(x),'tkrB':"%5.2f"%(perB),'threshold':"%5.2f"%(y),'balance':"%12d"%(bal)}, ignore_index=True) # output Dataframe

    dfO.to_csv(tkrA + "_" + tkrB + "_" + prd + "_rebalanced.csv", index=False)

def sorting():
    df = pd.read_csv(tkrA + "_" + tkrB + "_" + prd + "_rebalanced.csv")
    df.sort_values(by=['bal'], inplace=True, ascending=False)
    df.to_csv(tkrA + "_" + tkrB + "_" + prd + "_sorted.csv", index=False)

def main(tkrA, tkrB, prd):
    syncing_csv(tkrA, tkrB, prd)
    syncing_csv(tkrB, tkrA, prd)
    rebalancing()
    sorting()

tkrA = "TQQQ" # Ticker: TQQQ NASDAQ100 3x, 304940 KODEX NASDAQ100
tkrB = "TMF"  # Ticker: TMF 20+ Treasury 3x, 304660 KODEX 30 Years Treasury
prd = "1d"
main(tkrA, tkrB, prd)
