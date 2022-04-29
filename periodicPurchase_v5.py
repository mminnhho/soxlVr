"""
buy and hold
cost averaging
periodic purchase tickerA, tickerB
buy EVERY WEEK whick rises more by previous HIGH price
cumulative rate 52x
yearly average rate 39%
monthly average rate 2.8%
"""

import pandas as pd
import matplotlib.pyplot as plt

tickerA = 'tqqq'
tickerB = 'soxl'
# cashFlow = 500  # month
cashFlow = 500 * 12 / 53  # week
feeRate = 0.0007
maxYield = 0
ohlc = 1  # open 1, high 2, low 3, close 4
drop = 0.98  # after open price

dfA = pd.read_csv('soxl_tqqq_synced.csv')
dfB = pd.read_csv('tqqq_soxl_synced.csv')
dfO = pd.DataFrame(columns = ['date', 'quantityA', 'sumA', 'quantityB', 'sumB', 'cashBalance', 'fee', 'sumFee', 'balance', 'capital', 'yield'])

for i in range(0, len(dfA)):
	if i != 0:
		srA = dfA.iloc[i]
		srB = dfB.iloc[i]

		week = pd.Period(srA[0], freq='W')
		if (week != previousMonth) or (i == 1):
			cashBalance += cashFlow

			if (srA[ohlc] / previousHighA) <= (srB[ohlc] / previousHighB):  # maxYield 52x
			# if (srA[ohlc] / initialA) >= (srB[ohlc] / initialB):  # maxYield 36x
				quantityA = int(cashBalance / ((srA[ohlc] * drop) * (1 + feeRate)))
				quantityB = 0
				sumA += quantityA
				fee = ((srA[ohlc] * drop) * quantityA) * feeRate
				sumFee += fee

			else:
				quantityA = 0
				quantityB = int(cashBalance / ((srB[ohlc] * drop) * (1 + feeRate)))
				sumB += quantityB
				fee = ((srB[ohlc] * drop) * quantityB) * feeRate
				sumFee += fee

			cashBalance -= ((srA[ohlc] * quantityA) + (srB[ohlc] * quantityB) + fee)
			balance = (srA[4] * sumA) + (srB[4] * sumB) + cashBalance
			capital += cashFlow

			dfT = pd.DataFrame({'date':[srA[0]], 'quantityA':["%5d"%(quantityA)], 'sumA':["%6d"%(sumA)], 'quantityB':["%5d"%(quantityB)], 'sumB':["%5d"%(sumB)], 'cashBalance':["%6.2f"%(cashBalance)], 'fee':["%5.2f"%(fee)], 'sumFee':["%3d"%(sumFee)], 'balance':["%8d"%(balance)], 'capital':["%7d"%(capital)], 'yield':["%3d"%(balance / capital)]})
			dfO = pd.concat([dfO, dfT], ignore_index=False, axis=0)

			if (balance / capital) > maxYield:
				date = srA[0]
				maxYield = balance / capital
			
			if previousHighA < srA[1]:
				previousHighA = srA[1]

			if previousHighB < srB[1]:
				previousHighB = srB[1]
				
			previousMonth = week

	else:
		srA = dfA.iloc[i]
		srB = dfB.iloc[i]

		previousHighA = srA[1]
		previousHighB = srB[1]

		cashBalance = 0
		balance = 0
		capital = 0
		sumA = 0
		sumB = 0
		sumFee = 0
		maxYield = 0
		
		dfT = pd.DataFrame({'date':[srA[0]], 'quantityA':["%5d"%(0)], 'sumA':["%6d"%(sumA)], 'quantityB':["%5d"%(0)], 'sumB':["%5d"%(sumB)], 'cashBalance':["%6.2f"%(cashBalance)], 'fee':["%5.2f"%(sumFee)], 'sumFee':["%3d"%(sumFee)], 'balance':["%8d"%(balance)], 'capital':["%7d"%(capital)], 'yield':["%3d"%(0)]})
		dfO = pd.concat([dfO, dfT], ignore_index=False, axis=0)
		previousMonth = pd.Period(srA[0], freq='W')

dfO.to_csv(tickerA + '_' + tickerB + '_periodicPurchase_v3.csv', index=False)
print(date, 'maxYield', int(maxYield))

y = dfO['yield'].tolist()

for i in range(0, len(y)):
	y[i] = int(y[i])

plt.plot(y)

plt.show()