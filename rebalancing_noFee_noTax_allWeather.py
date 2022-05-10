"""
rebalancing: 2 of tqqq, soxl, tmf, ugl
# fee 0.07 %
# tax 20 + 2 %
rebalancing price: close price
"""

import pandas as pd
import os
from datetime import datetime


def sync(tickerA, tickerB):

    print('syncing...')

    dfA = pd.read_csv(tickerA + '_sync.csv')
    dfB = pd.read_csv(tickerB + '_sync.csv')
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

    dfO.to_csv(tickerA + '_sync.csv', index=False)
    print('synced ' + tickerA + ' with ' + tickerB)
    print()


def rebal(ticker):

    dfTQQQ = pd.read_csv('tqqq_sync.csv')
    dfSOXL = pd.read_csv('soxl_sync.csv')
    dfTMF = pd.read_csv('tmf_sync.csv')
    dfUGL = pd.read_csv('ugl_sync.csv')
    dfO = pd.DataFrame(columns = ['date'] + ticker + ['balance'])
    dfOO = pd.DataFrame(columns = ['tqqq', 'soxl', 'tmf', 'ugl', 'threshold', 'maxYield'])

    # fee = 0.0007
    # tax = 0.2 + 0.02

    capital = 100000
    proportion = [(1/100) * x for x in range(82, 83)]  # proportion of first ticker(tqqq)
    threshold = [(1/1000) * x for x in range(46, 47)]
    maxxYield = 0

    log = (len(proportion) == 1) and (len(threshold) == 1)

    for a in proportion:
        b = (1 - a) * 0.6
        c = (1 - a - b) * 0.6
        d = 1 - a - b - c
        # b, c, d = 0.25, 0.25, 0.25

        for t in threshold:
            maxBalance = 0
            minBalance = 0
            # cashBalance = 0

            srTQQQ = dfTQQQ.iloc[0]
            quantityTQQQ = int((capital * a) / srTQQQ[4])

            srSOXL = dfSOXL.iloc[0]
            quantitySOXL = int((capital * b) / srSOXL[4])

            srTMF = dfTMF.iloc[0]
            quantityTMF = int((capital * c) / srTMF[4])

            srUGL = dfUGL.iloc[0]
            quantityUGL = int((capital * d) / srUGL[4])

            cashBalance = capital - (srTQQQ[4] * quantityTQQQ) -(srSOXL[4] * quantitySOXL) - (srTMF[4] * quantityTMF) - (srUGL[4] * quantityUGL)

            dfT = pd.DataFrame({'date':[srTQQQ[0]], 'tqqq':[quantityTQQQ], 'soxl':[quantitySOXL], 'tmf':[quantityTMF], 'ugl':[quantityUGL], 'balance':[int(capital)]})
            dfO = pd.concat([dfO, dfT], ignore_index = True, axis = 0)

            for i in range(1, len(dfTQQQ)):
                srTQQQ = dfTQQQ.iloc[i]
                srSOXL = dfSOXL.iloc[i]
                srTMF = dfTMF.iloc[i]
                srUGL = dfUGL.iloc[i]
                srO = dfO.iloc[-1]

                balance = (srTQQQ[4] * srO[1]) + (srSOXL[4] * srO[2]) + (srTMF[4] * srO[3]) + (srUGL[4] * srO[4]) + cashBalance

                if (abs(((srTQQQ[4] * srO[1]) / balance) - a) > t) or (abs(((srSOXL[4] * srO[2]) / balance) - b) > t) or (abs(((srTMF[4] * srO[3]) / balance) - c) > t) or (abs(((srUGL[4] * srO[4]) / balance) - d) > t):
                    # if log:
                        # print(dfO.iloc[-1])
                        # print()

                    if ((srTQQQ[4] * srO[1]) / balance) > a:
                        quantityTQQQ = srO[1] - int(((((srTQQQ[4] * srO[1]) / balance) - a) * balance) / srTQQQ[4]) - 1
                        cashBalance += (srO[1] - quantityTQQQ) * srTQQQ[4]

                    if ((srSOXL[4] * srO[2]) / balance) > b:
                        quantitySOXL = srO[2] - int(((((srSOXL[4] * srO[2]) / balance) - b) * balance) / srSOXL[4]) - 1
                        cashBalance += (srO[2] - quantitySOXL) * srSOXL[4]

                    if ((srTMF[4] * srO[3]) / balance) > c:
                        quantityTMF = srO[3] - int(((((srTMF[4] * srO[3]) / balance) - c) * balance) / srTMF[4]) - 1
                        cashBalance += (srO[3] - quantityTMF) * srTMF[4]

                    if ((srUGL[4] * srO[4]) / balance) > d:
                        quantityUGL = srO[4] - int(((((srUGL[4] * srO[4]) / balance) - d) * balance) / srUGL[4]) - 1
                        cashBalance += (srO[4] - quantityUGL) * srUGL[4]



                    if ((srTQQQ[4] * srO[1]) / balance) < a:
                        quantityTQQQ = srO[1] + int(((a - ((srTQQQ[4] * srO[1]) / balance)) * balance) / srTQQQ[4])
                        cashBalance -= (quantityTQQQ - srO[1]) * srTQQQ[4]

                    if ((srSOXL[4] * srO[2]) / balance) < b:
                        quantitySOXL = srO[2] + int(((b - ((srSOXL[4] * srO[2]) / balance)) * balance) / srSOXL[4])
                        cashBalance -= (quantitySOXL - srO[2]) * srSOXL[4]

                    if ((srTMF[4] * srO[3]) / balance) < c:
                        quantityTMF = srO[3] + int(((c - ((srTMF[4] * srO[3]) / balance)) * balance) / srTMF[4])
                        cashBalance -= (quantityTMF - srO[3]) * srTMF[4]

                    if ((srUGL[4] * srO[4]) / balance) < d:
                        quantityUGL = srO[4] + int(((d - ((srUGL[4] * srO[4]) / balance)) * balance) / srUGL[4])
                        cashBalance -= (quantityUGL - srO[4]) * srUGL[4]



                    balance = (srTQQQ[4] * srO[1]) + (srSOXL[4] * srO[2]) + (srTMF[4] * srO[3]) + (srUGL[4] * srO[4]) + cashBalance

                    dfT = pd.DataFrame({'date':[srTQQQ[0]], 'tqqq':[quantityTQQQ], 'soxl':[quantitySOXL], 'tmf':[quantityTMF], 'ugl':[quantityUGL], 'balance':[int(balance)]})
                    dfO = pd.concat([dfO, dfT], ignore_index = True, axis = 0)

                    # if log:
                    #     print(srTQQQ[0], quantityTQQQ, quantitySOXL, quantityTMF, quantityUGL, int(cashBalance), str(int(balance / capital)) + 'x\n')

                if balance > maxBalance:
                    maxBalance = balance
                    minBalance = balance
                    date = srTQQQ[0]

                if balance < minBalance:
                    minBalance = balance
                    dateMin = srTQQQ[0]

            maxYield = int(maxBalance / capital)
            minYield = int(minBalance / capital)

            if maxYield > maxxYield:
                maxxYield = maxYield
                aa = a
                bb = b
                cc = c
                dd = d
                tt = t

            dfT = pd.DataFrame({'tqqq':["%5.3f"%(a)], 'soxl':["%5.3f"%(b)], 'tmf':["%5.3f"%(c)], 'ugl':["%5.3f"%(d)], 'threshold':["%5.3f"%(t)], 'maxYield':[maxYield]})
            dfOO = pd.concat([dfOO, dfT], ignore_index = True, axis = 0)

            if not log:
                print("%5.3f"%(a), "%5.3f"%(b), "%5.3f"%(c), "%5.3f"%(d), "%5.3f"%(t), 'maxYield', str(int(maxYield)) + 'x')


    if log:
        print('Max', date, "%4.2f"%(a), "%4.2f"%(b), "%4.2f"%(c), "%4.2f"%(d), "%5.3f"%(t),  'maxYield', str(int(maxYield)) + 'x')
        print('Min', dateMin, 'minYield', str(int(minYield)) + 'x')


    now = datetime.now().strftime("%Y%m%d%H%M")

    if not log:
        print('Max Case', "%4.2f"%(aa), "%4.2f"%(bb), "%4.2f"%(cc), "%4.2f"%(dd), "%5.3f"%(tt), 'maxYield', str(int(maxxYield)) + 'x')
        dfOO.to_csv(ticker[0] + "_" + ticker[1] + "_" + ticker[2] + "_" + ticker[3] + "_allWeather_" + now + ".csv", index=False)
        dfOO.sort_values(by=['maxYield'], inplace=True, ascending=False)
        dfOO.to_csv(ticker[0] + "_" + ticker[1] + "_" + ticker[2] + "_" + ticker[3] + "_sorted_" + now + ".csv", index=False)

    if log:
        dfO.to_csv(ticker[0] + str(int(aa*100)) + ticker[1] + str(int(bb*100)) + ticker[2] + str(int(cc*100)) + ticker[3] + str(int(dd*100)) + "t" + str("%3.1f"%(tt*100)) + "_rebalanced_" + now + ".csv", index=False)


def main(ticker):
    # for i in range(1, len(ticker)):
    #     sync(ticker[0], ticker[i])

    # for i in range(1, len(ticker)):
    #     sync(ticker[i], ticker[0])

    rebal(ticker)


ticker = ['tqqq', 'soxl', 'tmf', 'ugl']


main(ticker)
