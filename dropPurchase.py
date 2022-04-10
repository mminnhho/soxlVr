"""
buy and hold
cost averaging
drop then purchase TICKER (vs periodic purchase)
cost averaging
cumulative rate x00
monthly average rate 0.00%
"""

import pandas as pd

ticker = 'TQQQ'
cashFlow = 500
dropP = [(1/100) * x for x in range(1,20,2)]  # drop percent
buyP = [(1/100) * x for x in range(100,50,-5)]  # buy percent

dfO = pd.DataFrame(columns=['date', 'price', 'amount', 'cash', 'balance', 'capital'])

df = pd.read_csv(ticker + '.csv')

lO = []

for x in dropP:
	for y in buyP:

		for i in range(0, len(df)):
			pH= 0
			if i != 0:
				sr  = df.iloc[i]
				if sr[2] > pH:
					pH = sr[2]
				month = pd.Period(sr[0], freq='M')

				if month != previousMonth:
					cash += cashFlow
					capital += cashFlow
					previousMonth = month

				elif (sr[3] < (pH * (1 - x))) and (cash // (pH * (1 - x)) > 0):
					priceBuy = (pH * (1 - x))
					amount = (cash // priceBuy) * y
					stockSum += amount
					cash = cash - (priceBuy * amount)
					balance = (priceBuy * stockSum) + cash

					dfT = pd.DataFrame({'date':[sr[0]], 'price':["%7.2f"%(sr[4])], 'amount':["%7d"%(stockSum)], 'cash':["%7.2f"%(cash)], 'balance':["%10d"%(balance)], 'capital':["%7d"%(capital)]})
					dfO = pd.concat([dfO, dfT], ignore_index=False, axis=0)

					previousMonth = month
					pH = priceBuy


			else:
				sr  = df.iloc[i]
				pH = sr[2]

				month = pd.Period(sr[0], freq='M')
				stockSum = 0
				cash = cashFlow
				balance = cashFlow
				capital = cashFlow

				dfT = pd.DataFrame({'date':[sr[0]], 'price':["%7.2f"%(sr[4])], 'amount':["%7d"%(stockSum)], 'cash':["%7.2f"%(cash)], 'balance':["%10d"%(balance)], 'capital':["%7d"%(capital)]})
				dfO = pd.concat([dfO, dfT], ignore_index=False, axis=0)

				previousMonth = pd.Period(sr[0], freq='M')

		srO = dfO.iloc[-1]
		lO.append("%4.1f"%(float(srO[4]) / float(srO[5])))
		# print(x, y)
		print("%4.2f"%(x), "%4.2f"%(y))
		print(max(lO))
		print()
