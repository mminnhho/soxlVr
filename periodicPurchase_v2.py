"""
buy and hold
cost averaging
buy 00% of cashBalance when drops by 00%
cumulative rate 000x
monthly average rate 0.00%
"""

import pandas as pd

ticker = 'TQQQ'
cashFlow = 500
feeRate = 0.0007
yyield = 0
maxYield = 0
previousHigh = 0

drop = [(1/100) * x for x in range(10, 11)]
proportion = [(1/100) * x for x in range(100, 101)]

log = (len(drop) == 1) and (len(proportion) == 1)
# log = False

df = pd.read_csv(ticker + '.csv')
dfO = pd.DataFrame(columns = ['date', 'price', 'quantity', 'sumStock', 'cashBalance', 'fee', 'balance', 'capital'])

for d in drop:

	for p in proportion:
		capital = 0
		cashBalance = 0

		for i in range(0, len(df)):
			if i != 0:
				sr  = df.iloc[i]
				month = pd.Period(sr[0], freq='M')


				if month != previousMonth:
					cashBalance += cashFlow
					capital += cashFlow
					previousMonth = month

					# print(month)
					# print('capital', capital)
					# print('cashBalance', cashBalance)

				if sr[2] > previousHigh:
					previousHigh = sr[2]

				if (sr[3] < (previousHigh * (1 - d))) and (sr[4] < cashBalance * p):

					quantity = int((cashBalance * p) / (sr[4] * (1 + feeRate)))
					sumStock += quantity
					fee = (sr[4] * quantity) * feeRate
					cashBalance = cashBalance - (sr[4] * quantity) - fee
					balance = (sr[4] * sumStock) + cashBalance

					if log:
						dfT = pd.DataFrame({'date':[sr[0]], 'price':["%7.2f"%(sr[4])], 'quantity':["%6d"%(quantity)], 'sumStock':["%7d"%(sumStock)], 'cashBalance':["%7.2f"%(cashBalance)], 'fee':["%6.2f"%(fee)], 'balance':["%9d"%(balance)], 'capital':["%7d"%(capital)]})
						dfO = pd.concat([dfO, dfT], ignore_index=False, axis=0)

					sumFee += fee
					if (balance / capital) > yyield:
						yyield = balance / capital
					
					previousMonth = month

				else:
					pass

			else:
				sr  = df.iloc[i]
				month = pd.Period(sr[0], freq='M')
				previousHigh = sr[2]
				quantity = int(cashFlow / (sr[4] * (1 + feeRate)))
				sumStock = quantity
				fee = (sr[4] * quantity) * feeRate
				cashBalance = cashFlow - (sr[4] * quantity) - fee
				balance = (sr[4] * sumStock) + cashBalance
				capital = cashFlow
				
				if log:
					dfO = pd.DataFrame({'date':[sr[0]], 'price':["%7.2f"%(sr[4])], 'quantity':["%6d"%(quantity)], 'sumStock':["%7d"%(sumStock)], 'cashBalance':["%7.2f"%(cashBalance)], 'fee':["%6.2f"%(fee)], 'balance':["%9d"%(balance)], 'capital':["%7d"%(capital)]})

				sumFee = fee
				if (balance / capital) > yyield:
					yyield = balance / capital

				previousMonth = pd.Period(sr[0], freq='M')

		print('drop', "%4.2f"%(d), 'proportion', "%4.2f"%(p), 'yield', "%5.2f"%(yyield))

if yyield > maxYield:
	maxYield = yyield

print('maxYield', int(maxYield))

if log:
	dfO.to_csv(ticker + '_periodicPurchase_v2.csv', index=False)
# print('sumFee', int(sumFee))

print(dfO)