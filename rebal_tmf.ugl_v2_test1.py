"""
rebalancing tmf, ugl
useing segments
no tax
"""


import pandas as pd
import os
from datetime import datetime
import statistics

ticker = ['TMF', 'UGL']

dfTK0 = pd.read_csv(ticker[0] + '.csv')
dfTK1 = pd.read_csv(ticker[1] + '.csv')

dfO = pd.DataFrame(columns = ['date'] + ticker + ['balance'])
dfOO = pd.DataFrame(columns = ticker + ['threshold', 'maxYield'])

feeRate = 0.0007
bal = 100000
n = 10

stkBalTK0 = 0
stkBalTK1 = 0

countBuyTMF = 0
countBuyUGL = 0

propoTK0L = [(1/100) * x for x in range(50,51)]  # proportion of first ticker(TK0)
thre = [(1/1000) * x for x in range(50,51)]  # threshold
maxxYld = 0  # max yield for each threshold

log = (len(propoTK0L) == 1) and (len(thre) == 1)

for propoTK0 in propoTK0L:
    propoTK1 = 1 - propoTK0  # proportion of first ticker(TK1)

    for t in thre:

        srTK0 = dfTK0.iloc[0]
        priceTK0 = srTK0[4]

        srTK1 = dfTK1.iloc[0]
        priceTK1 = srTK1[4]

        date = srTK0[0]
        dateMin = srTK0[0]

#        cashBalance = capital - (srTK0[4] * quantityTK0) - (srTK1[4] * quantityTK1)

        for i in range(1, len(dfTK0)):
#        for i in range(1, 21):
            for oc in [1, 4]:

                srTK0 = dfTK0.iloc[i]
                srTK1 = dfTK1.iloc[i]
                date = srTK0[0]

                balTK0 = srTK0 * stkBalTK0
                balTK1 = srTK1 * stkBalTK1
#                cashBalance = capital - balTK0 - balTK1

                if (srTK0[oc]/priceTK0-srTK1[oc]/priceTK1) < -t:
                    priceTK0 = srTK0[oc]
                    priceTK1 = srTK1[oc]
                    print('rebalanced',date,priceTK0,priceTK1)

                    countBuyTMF += 1
                    if countBuyUGL != 0:
                        countBuyUGL -= 1

                if (srTK0[oc]/priceTK0-srTK1[oc]/priceTK1) > t:
                    priceTK0 = srTK0[oc]
                    priceTK1 = srTK1[oc]
                    print('rebalanced',date,priceTK0,priceTK1)

                    countBuyUGL += 1
                    if countBuyTMF != 0:
                        countBuyTMF -= 1

print(countBuyTMF, countBuyUGL)
