"""
rebalancing: TQQQ, TMF
fee 0.07 %
tax 20 + 2 %
when no fee, no tax: 2010-2022 1.0 89:11 2% x134 (max x196 55.2%Y)
noticeable: 2010-2022 1.5 89:11 5% x166 (max x207 55.9%Y)
rebalancing twice a day: open, close price
"""

import pandas as pd
import os


def sync(tickerA, tickerB):

    print('syncing...')

    dfA = pd.read_csv(tickerA + '.csv')
    dfB = pd.read_csv(tickerB + '.csv')
    dfO = pd.DataFrame(columns = dfA.columns)

    beginPointer = 0

    for i in range(0, len(dfA)):
        srA = dfA.iloc[i]

        for j in range(beginPointer, len(dfB)):
            srB = dfB.iloc[j]

            if srA[0] == srB[0]:
                dfT = pd.DataFrame({'Date':[srA[0]], 'Open':[srA[1]], 'High':[srA[2]], 'Low':[srA[3]], 'Close':[srA[4]], 'Adj Close':[srA[5]], 'Volume':[srA[6]]})
                dfO = pd.concat([dfO, dfT], ignore_index = True, axis = 0)
                beginPointer = j + 1

            elif srA[0] < srB[0]:
                break

    dfO.to_csv(tickerA + '_' + tickerB + '_synced.csv', index=False)
    print('synced ' + tickerA + ' with ' + tickerB)
    print()


def rebal(tickerA, tickerB):

    dfA = pd.read_csv(tickerA + "_" + tickerB + "_synced.csv")
    dfB = pd.read_csv(tickerB + "_" + tickerA + "_synced.csv")
    dfO = pd.DataFrame(columns = ['virtualAsset', 'tickerA', 'tickerB', 'threshold', 'maxYield'])

    fee = 0.0007
    tax = 0.2 + 0.02

    capital = 100000
    stockBalanceA = 0
    stockBalanceB = 0
    balanceA = 0
    balanceB = 0
    cashBalance = 0
    balance = 0

    virtualAsset = [(1/10) * x for x in range(7, 10)]
    proportionA = [(1/100) * x for x in range(92, 95)]
    threshold = [(1/100) * x for x in range(1, 3)]

    log = (len(virtualAsset) == 1) and (len(proportionA) == 1) and (len(threshold) == 1)

    for a in virtualAsset:

        for p in proportionA:
            proportionB = 1 - p

            for t in threshold:

                # if log:
                print("%4.2f %4.2f %4.2f" % (a, p, t))

                srA = dfA.iloc[0]
                srB = dfB.iloc[0]
                priceA = (srA[1] + srA[4]) / 2
                priceB = (srB[1] + srB[4]) / 2
                stockBalanceA = (capital * p) // priceA
                stockBalanceB = (capital * proportionB) // priceB
                cashBalance = capital - (priceA * stockBalanceA) - (priceB * stockBalanceB)
                maxYield = balance / capital
                maxDate = srA[0]

                for i in range(1, len(dfA)):

                    srA = dfA.iloc[i]
                    srB = dfB.iloc[i]
                    priceA = (srA[1] + srA[4]) / 2
                    priceB = (srB[1] + srB[4]) / 2
                    balanceA = priceA * stockBalanceA
                    balanceB = priceB * stockBalanceB
                    balance = balanceA + balanceB + cashBalance

                    if ((balanceA / balance) - p) > t:
                        amountA = ((balanceA - (balance * p)) // priceA) + 1
                        amountA *= a
                        amountA = int(amountA)

                        if amountA > stockBalanceA:
                            amountA = stockBalanceA

                        stockBalanceA -= amountA
                        amountB = (amountA * priceA + cashBalance) // priceB
                        stockBalanceB += amountB
                        cashBalance = (amountA * priceA + cashBalance) % priceB
                        balance = balanceA + balanceB + cashBalance

                        if (balance / capital) > maxYield:
                            maxYield = balance / capital
                            maxDate = srA[0]

                        if log:
                            print(srA[0], int(stockBalanceA), ',' ,int(stockBalanceB), ',' ,int(maxYield))

                    elif ((balanceB / balance) - proportionB) > t:
                        amountB = ((balanceB - (balance * proportionB)) // priceB) + 1
                        amountB *= a
                        amountB = int(amountB)

                        if amountB > stockBalanceB:
                            amountB = stockBalanceB

                        stockBalanceB -= amountB
                        amountA = (amountB * priceB + cashBalance) // priceA
                        stockBalanceA += amountA
                        cashBalance = (amountB * priceB + cashBalance) % priceA
                        balance = balanceA + balanceB + cashBalance

                        if (balance / capital) > maxYield:
                            maxYield = balance / capital
                            maxDate = srA[0]

                        if log:
                            print(srA[0], int(stockBalanceA), ',' ,int(stockBalanceB), ',' ,int(maxYield))

                print('max', maxDate, "%4d"%(maxYield))
                print()

                balanceA = priceA * stockBalanceA
                balanceB = priceB * stockBalanceB
                balance = balanceA + balanceB + cashBalance

                dfT = pd.DataFrame({'virtualAsset':["%5.2f"%(a)], 'tickerA':["%5.2f"%(p)], 'tickerB':["%5.2f"%(proportionB)], 'threshold':["%5.2f"%(t)], 'maxYield':["%4d"%(maxYield)]})
                dfO = pd.concat([dfO, dfT], ignore_index = True, axis = 0)

    dfO.to_csv(tickerA + "_" + tickerB + "_rebalanced.csv", index=False)


def sort(tickerA, tickerB):
    df = pd.read_csv(tickerA + "_" + tickerB + "_rebalanced.csv")
    df.sort_values(by=['maxYield'], inplace=True, ascending=False)
    df.to_csv(tickerA + "_" + tickerB + "_sorted.csv", index=False)
    sr = df.iloc[0]
    print(sr[0], tickerA, sr[1], tickerB, sr[2], sr[3], "%4d"%(sr[4]))


def main(tickerA, tickerB):
    pathA = "D:/soxlVr/" + tickerA + "_" + tickerB + "_synced.csv"
    pathB = "D:/soxlVr/" + tickerB + "_" + tickerA + "_synced.csv"

    if (os.path.isfile(pathA)==False) or (os.path.isfile(pathB)==False):
        sync(tickerA, tickerB)
        sync(tickerB, tickerA)

    else:
        print('synced')
        print()

    rebal(tickerA, tickerB)

    sort(tickerA, tickerB)


tickerA = 'TQQQ'
tickerB = 'TMF'


main(tickerA, tickerB)
