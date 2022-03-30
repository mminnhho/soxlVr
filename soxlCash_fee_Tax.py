"""
Rebalancing: SOXL/TQQQ and Cash
"""

import pandas as pd
import datetime


ticker = "TQQQ"
capital = 10000
proportion = [(1/100) * x for x in range(90,91)]   # percentage of ticker
threshold = [(1/100) * x for x in range(1,2)]    # rebalancing threshold
fee = 0.0007   # trade fee

trade_log = (len(proportion) == 1) and (len(threshold) == 1)

print("Capital:   ", capital)
print("Proportion:", "%5.2f"%(proportion[0]*100), "~", "%5.2f"%(proportion[-1]*100), "%")
print("Threshold: ", "%5.2f"%(threshold[0]*100), "~",  "%5.2f"%(threshold[-1]*100), "%")
print("Fee:       ", "%5.2f"%(fee*100), "%")

dfO = pd.DataFrame(columns=['Proportion', 'Threshold', 'Balance'])   # output Dataframe
dfTS = pd.DataFrame(columns=['Date', 'BuySell', 'Price', 'Amount', 'PriceBought'])
dfAR = pd.DataFrame(columns=['Year', 'Revenue'])
maxBalance = []

price = 0
amount = 0
cash = 0
balance = 0
balanceStock = 0

df = pd.read_csv(ticker + ".csv")   # read csv file of stock

for p in proportion:
	for t in threshold:

		sr = df.iloc[0]   # first row
		balanceStock = (capital*p) // sr[4]   # close price, bought price
		cash = capital - (((sr[2]+sr[3])/2) * balanceStock)   # changes

		dfTST = pd.DataFrame({'Date':sr[0], 'BuySell':['Buy'], 'Price':sr[4], 'Amount':[balanceStock], 'PriceBought':[0]})   # temp DataFrame
		dfTS = pd.concat([dfTS, dfTST], ignore_index = True, axis = 0)

		for i in range(1,len(df)):
		# for i in range(1,200):

			previousBS = 0
			sr = df.iloc[i]

			if ((1-p-t) > 0) and (sr[2] > (cash * ((p+t)/(1-p-t)) / balanceStock)):   # Sell, ticker rise by threshold %

				price = cash * ((p+t)/(1-p-t)) / balanceStock
				previousBS = balanceStock
				balanceStock = previousBS - ((cash*t/(1-p-t)) // price) - 1
				cash = cash + ((price * (previousBS-balanceStock)) * (1 - fee))
				balance = price * balanceStock + cash

				dfTST = pd.DataFrame({'Date':sr[0], 'BuySell':['Sell'], 'Price':[price], 'Amount':[previousBS - balanceStock], 'PriceBought':[0]})   # temp DataFrame
				dfTS = pd.concat([dfTS, dfTST], ignore_index = True, axis = 0)

				if trade_log:
					print()
					print("Rise")
					print(sr[0])
					print(price)
					print(previousBS)
					print(balanceStock)
					print(price * balanceStock / balance)
					print(balance)

			if sr[2] > (cash * ((p-t)/(1-p+t)) / balanceStock) > sr[3]:   # Buy, ticker drop by threshold %

				price = cash * ((p-t)/(1-p+t)) / balanceStock
				previousBS = balanceStock
				balanceStock = previousBS + ((cash*t/(1-p+t)) // price) + 1
				cash = cash - ((price * (balanceStock-previousBS)) * (1 + fee))
				balance = price * balanceStock + cash

				dfTST = pd.DataFrame({'Date':sr[0], 'BuySell':['Buy'], 'Price':[price], 'Amount':[balanceStock - previousBS], 'PriceBought':[0]})   # temp DataFrame
				dfTS = pd.concat([dfTS, dfTST], ignore_index = True, axis = 0)

				if trade_log:
					print()
					print("Drop")
					print(sr[0])
					print(price)
					print(previousBS)
					print(balanceStock)
					print(price * balanceStock / balance)
					print(balance)

			if trade_log:
				maxBalance.append(sr[4] * balanceStock + cash)

		dictO = {'Proportion':["%5.2f"%(p)], 'Threshold':["%5.2f"%(t)], 'Balance':["%10d"%(balance)]}
		dfOT = pd.DataFrame.from_dict(dictO)   # temp DataFrame
		dfO = pd.concat([dfO, dfOT], ignore_index = True, axis = 0)

print()
dfO.sort_values(by=['Balance'], inplace=True, ascending=True)
print(dfO)

if trade_log:
	print()
	print("Max Balance: ", "%10d"%(max(maxBalance)))
	print()

print(dfTS)
