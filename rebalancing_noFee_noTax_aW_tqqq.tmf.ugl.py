"""
rebalancing: 2 of TK0, TK1, TK2, TK3
# fee 0.07 %
# tax 20 + 2 %
rebalancing price: close price
"""

import pandas as pd
import os
from datetime import datetime


ticker = ['tqqq', 'tmf', 'ugl']

dfTK0 = pd.read_csv(ticker[0] + '.csv')
dfTK1 = pd.read_csv(ticker[1] + '.csv')
dfTK2 = pd.read_csv(ticker[2] + '.csv')
# dfTK3 = pd.read_csv(ticker[3] + '.csv')
dfO = pd.DataFrame(columns = ['date'] + ticker + ['balance'])
dfOO = pd.DataFrame(columns = ticker + ['threshold', 'maxYield'])

# fee = 0.0007
# tax = 0.2 + 0.02

capital = 100000
proportionTK0 = [(1/100) * x for x in range(30,91)]  # proportion of first ticker(TK0)
proportionTK1 = [(1/100) * x for x in range(5,66)]  # proportion of first ticker(TK1)
proportionTK2 = [(1/100) * x for x in range(5,66)]  # proportion of first ticker(TK2)
threshold = [(1/1000) * x for x in range(5,301,5)]
maxxYield = 0

log = (len(proportionTK0) == 1) and (len(proportionTK1) == 1) and (len(proportionTK2) == 1) and (len(threshold) == 1)

for a in proportionTK0:
    for b in proportionTK1:
        for c in proportionTK2:

            if (a+b+c) == 1:
                for t in threshold:

                    # print(a,b,c,t)

                    maxBalance = 0
                    minBalance = 0
                    # cashBalance = 0

                    aa = a
                    bb = b
                    cc = c
                    tt = t

                    srTK0 = dfTK0.iloc[0]
                    quantityTK0 = int((capital * a) / srTK0[4])

                    srTK1 = dfTK1.iloc[0]
                    quantityTK1 = int((capital * b) / srTK1[4])

                    srTK2 = dfTK2.iloc[0]
                    quantityTK2 = int((capital * c) / srTK2[4])

                    date = srTK0[0]
                    dateMin = srTK0[0]

                    cashBalance = capital - (srTK0[4] * quantityTK0) - (srTK1[4] * quantityTK1) - (srTK2[4] * quantityTK2)

                    dfT = pd.DataFrame({'date':[srTK0[0]], ticker[0]:[quantityTK0], ticker[1]:[quantityTK1], ticker[2]:[quantityTK2], 'balance':[int(capital)]})
                    dfO = pd.concat([dfO, dfT], ignore_index = True, axis = 0)

                    for i in range(1, len(dfTK0)):
                        srTK0 = dfTK0.iloc[i]
                        srTK1 = dfTK1.iloc[i]
                        srTK2 = dfTK2.iloc[i]
                        srO = dfO.iloc[-1]

                        balance = (srTK0[4] * srO[1]) + (srTK1[4] * srO[2]) + (srTK2[4] * srO[3]) + cashBalance

                        if (abs(((srTK0[4] * srO[1]) / balance) - a) > t) or (abs(((srTK1[4] * srO[2]) / balance) - b) > t) or (abs(((srTK2[4] * srO[3]) / balance) - c) > t):
                            # if log:
                                # print(dfO.iloc[-1])
                                # print()

                            if ((srTK0[4] * srO[1]) / balance) > a:
                                quantityTK0 = srO[1] - int(((((srTK0[4] * srO[1]) / balance) - a) * balance) / srTK0[4]) - 1
                                cashBalance += (srO[1] - quantityTK0) * srTK0[4]

                            if ((srTK1[4] * srO[2]) / balance) > b:
                                quantityTK1 = srO[2] - int(((((srTK1[4] * srO[2]) / balance) - b) * balance) / srTK1[4]) - 1
                                cashBalance += (srO[2] - quantityTK1) * srTK1[4]

                            if ((srTK2[4] * srO[3]) / balance) > c:
                                quantityTK2 = srO[3] - int(((((srTK2[4] * srO[3]) / balance) - c) * balance) / srTK2[4]) - 1
                                cashBalance += (srO[3] - quantityTK2) * srTK2[4]


                            if ((srTK0[4] * srO[1]) / balance) < a:
                                quantityTK0 = srO[1] + int(((a - ((srTK0[4] * srO[1]) / balance)) * balance) / srTK0[4])
                                cashBalance -= (quantityTK0 - srO[1]) * srTK0[4]

                            if ((srTK1[4] * srO[2]) / balance) < b:
                                quantityTK1 = srO[2] + int(((b - ((srTK1[4] * srO[2]) / balance)) * balance) / srTK1[4])
                                cashBalance -= (quantityTK1 - srO[2]) * srTK1[4]

                            if ((srTK2[4] * srO[3]) / balance) < c:
                                quantityTK2 = srO[3] + int(((c - ((srTK2[4] * srO[3]) / balance)) * balance) / srTK2[4])
                                cashBalance -= (quantityTK2 - srO[3]) * srTK2[4]

                            balance = (srTK0[4] * srO[1]) + (srTK1[4] * srO[2]) + (srTK2[4] * srO[3]) + cashBalance

                            dfT = pd.DataFrame({'date':[srTK0[0]], ticker[0]:[quantityTK0], ticker[1]:[quantityTK1], ticker[2]:[quantityTK2], 'balance':[int(balance)]})
                            dfO = pd.concat([dfO, dfT], ignore_index = True, axis = 0)

                            if log:
                                print(srTK0[0], quantityTK0, quantityTK1, quantityTK2, int(cashBalance), str("%5.1f"%(balance / capital)) + 'x')

                        if balance > maxBalance:
                            maxBalance = balance
                            minBalance = balance
                            date = srTK0[0]

                        if balance < minBalance:
                            minBalance = balance
                            dateMin = srTK0[0]

                    maxYield = maxBalance / capital
                    minYield = minBalance / capital

                    if maxYield > maxxYield:
                        maxxYield = maxYield
                        aa = a
                        bb = b
                        cc = c
                        tt = t

                    dfT = pd.DataFrame({'tqqq':["%5.3f"%(a)], 'tmf':["%5.3f"%(b)], 'ugl':["%5.3f"%(c)], 'threshold':["%5.3f"%(t)], 'maxYield':["%5.1f"%(maxYield)]})
                    dfOO = pd.concat([dfOO, dfT], ignore_index = True, axis = 0)

                    if not log:
                        print("%5.3f"%(a), "%5.3f"%(b), "%5.3f"%(c), "%5.3f"%(t), str("%5.1f"%(maxYield)) + 'x')


if log:
    print('Max', date, "%4.2f"%(a), "%4.2f"%(b), "%4.2f"%(c), "%5.3f"%(t), str("%5.1f"%(maxYield)) + 'x')
    print('Min', dateMin, str(int(minYield)) + 'x')


now = datetime.now().strftime("%Y%m%d%H%M")


if not log:
    print('Max Case', "%4.2f"%(aa), "%4.2f"%(bb), "%4.2f"%(cc), "%5.3f"%(tt), 'maxYield', str("%5.1f"%(maxxYield)) + 'x')
    dfOO.to_csv(ticker[0] + "_" + ticker[1] + "_" + ticker[2] + "_allWeather_" + now + ".csv", index=False)
    dfOO.sort_values(by=['maxYield'], inplace=True, ascending=False)
    dfOO.to_csv(ticker[0] + "_" + ticker[1] + "_" + ticker[2] + "_sorted_" + now + ".csv", index=False)


if log:
    dfO.to_csv(ticker[0] + str(int(aa*100)) + ticker[1] + str(int(bb*100)) + ticker[2] + str(int(cc*100)) + "t" + str("%3.1f"%(tt*100)) + "_rebalanced_" + now + ".csv", index=False)
