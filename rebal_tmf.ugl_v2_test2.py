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
capital = 100000
n = 29

stkBalTK0 = 0
stkBalTK1 = 0

countBuyTMF = 0
countBuyUGL = 0

propoTK0L = [(1/100) * x for x in range(50,51)]  # proportion of first ticker(TK0)
thre = [(1/1000) * x for x in range(40,41)]  # threshold
maxxYld = 0  # max yield for each threshold

log = (len(propoTK0L) == 1) and (len(thre) == 1)

for propoTK0 in propoTK0L:
    propoTK1 = 1 - propoTK0  # proportion of first ticker(TK1)

    for t in thre:

        srTK0 = dfTK0.iloc[0]
        priceTK0 = srTK0[4]

        srTK1 = dfTK1.iloc[0]
        priceTK1 = srTK1[4]

#        date = srTK0[0]
#        dateMin = srTK0[0]


        for i in range(1, len(dfTK0)):
#        for i in range(1, 21):
            for oc in [1, 4]:

                srTK0 = dfTK0.iloc[i]
                srTK1 = dfTK1.iloc[i]

                balTK0 = srTK0[oc] * stkBalTK0
                balTK1 = srTK1[oc] * stkBalTK1
                if i==1:
                    cashBal = capital - balTK0 - balTK1
                bal = balTK0 + balTK1 + cashBal
                date = srTK0[0]

                if (srTK0[oc]/priceTK0-srTK1[oc]/priceTK1) < -t:
                    priceTK0 = srTK0[oc]
                    priceTK1 = srTK1[oc]

#                    countBuyTMF += 1
#                    if countBuyUGL != 0:
#                        countBuyUGL -= 1
                
                    if (stkBalTK1*priceTK1) > (bal/n):
                        amountTK1 = (bal/n) // priceTK1
                        stkBalTK1 -= amountTK1
                        cashBal += priceTK1 * amountTK1

                    amountTK0 = (bal/n) // priceTK0
                    stkBalTK0 += amountTK0
                    cashBal -= priceTK0 * amountTK0

                    print('buyTK0',date,"%5.2f"%(priceTK0),"%5.2f"%(priceTK1),int(bal),int(cashBal))

                if (srTK0[oc]/priceTK0-srTK1[oc]/priceTK1) > t:
                    priceTK0 = srTK0[oc]
                    priceTK1 = srTK1[oc]

#                    countBuyUGL += 1
#                    if countBuyTMF != 0:
#                        countBuyTMF -= 1
                    
                    if (stkBalTK0*priceTK0) > (bal/n):
                        amountTK0 = (bal/n) // priceTK0
                        stkBalTK0 -= amountTK0
                        cashBal += priceTK0 * amountTK0

                    amountTK1 = (bal/n) // priceTK1
                    stkBalTK1 += amountTK1
                    cashBal -= priceTK1 * amountTK1

                    print('buyTK1',date,"%5.2f"%(priceTK0),"%5.2f"%(priceTK1),int(bal),int(cashBal))

#print(countBuyTMF, countBuyUGL)
