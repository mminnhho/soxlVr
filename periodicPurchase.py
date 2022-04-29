"""
buy and hold
cost averaging
periodic purchase TICKER
cumulative rate x42
monthly average rate 1.97%
"""

import pandas as pd

ticker = 'TQQQ'
cashFlow = 500
feeRate = 0.0007
maxYield = 0

df = pd.read_csv(ticker + '.csv')

for i in range(0, len(df)):
	if i != 0:
		sr  = df.iloc[i]
		month = pd.Period(sr[0], freq='M')
		if month != previousMonth:
			quantity = int(cashFlow / (sr[4] * (1 + feeRate)))
			sumStock += quantity
			fee = (sr[4] * quantity) * feeRate
			cash = cashFlow - (sr[4] * quantity) - fee
			balance = (sr[4] * sumStock) + cash
			capital += cashFlow
			yyield = balance / capital

			dfT = pd.DataFrame({'date':[sr[0]], 'price':["%7.2f"%(sr[4])], 'quantity':["%6d"%(quantity)], 'sumStock':["%7d"%(sumStock)], 'cash':["%7.2f"%(cash)], 'fee':["%6.2f"%(fee)], 'balance':["%9d"%(balance)], 'capital':["%7d"%(capital)], 'yield':["%3d"%(yyield)]})
			dfO = pd.concat([dfO, dfT], ignore_index=False, axis=0)

			sumFee += fee
			if (balance / capital) > maxYield:
				date = sr[0]
				maxYield = balance / capital
			
			previousMonth = month

		else:
			pass

	else:
		sr  = df.iloc[i]
		month = pd.Period(sr[0], freq='M')
		quantity = int(cashFlow / (sr[4] * (1 + feeRate)))
		sumStock = quantity
		fee = (sr[4] * quantity) * feeRate
		cash = cashFlow - (sr[4] * quantity) - fee
		balance = (sr[4] * sumStock) + cash
		capital = cashFlow
		yyield = balance / capital
		
		dfO = pd.DataFrame({'date':[sr[0]], 'price':["%7.2f"%(sr[4])], 'quantity':["%6d"%(quantity)], 'sumStock':["%7d"%(sumStock)], 'cash':["%7.2f"%(cash)], 'fee':["%6.2f"%(fee)], 'balance':["%9d"%(balance)], 'capital':["%7d"%(capital)], 'yield':["%3d"%(yyield)]})

		sumFee = fee
		if (balance / capital) > maxYield:
			date = sr[0]
			maxYield = balance / capital

		previousMonth = pd.Period(sr[0], freq='M')

dfO.to_csv(ticker + '_periodicPurchase.csv', index=False)
# print('sumFee', int(sumFee))
print(date, 'maxYield', int(maxYield))
