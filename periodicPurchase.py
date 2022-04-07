"""
periodic purchase TICKER
cost averaging
cumulative rate x42
monthly average rate 1.97%
"""

import pandas as pd

ticker = 'TQQQ'
cashFlow = 500

dfO = pd.DataFrame(columns=['date', 'price', 'amount', 'cash', 'balance', 'capital'])

df = pd.read_csv(ticker + '.csv')

for i in range(0, len(df)):
	if i != 0:
		sr  = df.iloc[i]
		month = pd.Period(sr[0], freq='M')
		if month != previousMonth:
			amount = cashFlow // sr[4]
			stockSum += amount
			cash = cashFlow - (sr[4] * amount)
			balance = (sr[4] * stockSum) + cash
			capital += cashFlow

			dfT = pd.DataFrame({'date':[sr[0]], 'price':["%7.2f"%(sr[4])], 'amount':["%7d"%(stockSum)], 'cash':["%7.2f"%(cash)], 'balance':["%10d"%(balance)], 'capital':["%7d"%(capital)]})
			dfO = pd.concat([dfO, dfT], ignore_index=False, axis=0)

			previousMonth = month

		else:
			pass

	else:
		sr  = df.iloc[i]
		month = pd.Period(sr[0], freq='M')
		amount = 0
		amount = cashFlow // sr[4]
		stockSum = amount
		cash = cashFlow - (sr[4] * amount)
		balance = (sr[4] * stockSum) + cash
		capital = cashFlow
		
		dfT = pd.DataFrame({'date':[sr[0]], 'price':["%7.2f"%(sr[4])], 'amount':["%7d"%(stockSum)], 'cash':["%7.2f"%(cash)], 'balance':["%10d"%(balance)], 'capital':["%7d"%(capital)]})
		dfO = pd.concat([dfO, dfT], ignore_index=False, axis=0)

		previousMonth = pd.Period(sr[0], freq='M')

dfO.to_csv(ticker + '_periodicPurchase.csv', index=False)
