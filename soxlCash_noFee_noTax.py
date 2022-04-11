"""
Rebalancing: TQQQ/SOXL and Cash
best result: TQQQ, Cash 89:11 10% X148 -> rarely trades
considerable: TQQQ, Cash 90:10 1% x96
IMPORTANT: stock holdings are DECREASED !!!
"""

import pandas as pd


ticker = "TQQQ"
capital = 10000
proportion = [(1/100) * x for x in range(90,91)]  # percentage of ticker
threshold = [(1/100) * x for x in range(1,2)]  # rebalancing threshold
aW = [(1/10) * x for x in range(10,11)]  # amount weight
fee = 0.0007   # trade fee

trade_log = (len(proportion) == 1) and (len(threshold) == 1)

print("Capital:  ", capital, "$")
print("Proportion:  ", "%5.2f"%(proportion[0]*100), "~", "%5.2f"%(proportion[-1]*100), "%")
print("Threshold:   ", "%5.2f"%(threshold[0]*100), "~",  "%5.2f"%(threshold[-1]*100), "%")
print("AmountWeight:", "%4.1f"%(aW[0]), "~",  "%4.1f"%(aW[-1]), "%")
print("Fee:         ", "%5.2f"%(fee*100), "%")

dfO = pd.DataFrame(columns=['Proportion', 'Threshold', 'AmountWeight', 'Balance'])   # output Dataframe
maxBalance = []

price = 0
cash = 0
balance = 0
balanceStock = 0

df = pd.read_csv(ticker + ".csv")   # read csv file of stock

for p in proportion:
	for t in threshold:
		for a in aW:

			sr = df.iloc[0]   # first row
			balanceStock = (capital*p) // sr[4]   # close price, bought price
			cash = capital - (((sr[2]+sr[3])/2) * balanceStock)   # changes

			for i in range(1,len(df)):
			# for i in range(1,200):

				previousBS = 0
				sr = df.iloc[i]

				if ((1-p-t) > 0) and (sr[2] > (cash * ((p+t)/(1-p-t)) / balanceStock)):   # ticker rise by threshold %

					price = cash * ((p+t)/(1-p-t)) / balanceStock
					previousBS = balanceStock
					if previousBS > (((cash*t/(1-p-t)) // price) * a) - 1:
						balanceStock = previousBS - (((cash*t/(1-p-t)) // price) * a) - 1
					else:
						balanceStock = 0
					cash = cash + (price * (previousBS-balanceStock))
					balance = price * balanceStock + cash

					if trade_log:
						print()
						print("Rise")
						print(sr[0])
						print(price)
						print(previousBS)
						print(balanceStock)
						print(price * balanceStock / balance)
						print(balance)

				if sr[2] > (cash * ((p-t)/(1-p+t)) / balanceStock) > sr[3]:   # ticker drop by threshold %

					price = cash * ((p-t)/(1-p+t)) / balanceStock
					previousBS = balanceStock
					balanceStock = previousBS + (((cash*t/(1-p+t)) // price) * a) + 1
					if cash > (price * (balanceStock-previousBS)):
						cash = cash - (price * (balanceStock-previousBS))
					else:
						cash = 0
					balance = price * balanceStock + cash

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

			dfT = pd.DataFrame({'Proportion':["%5.2f"%(p)], 'Threshold':["%5.2f"%(t)],  'AmountWeight':["%4.1f"%(a)],'Balance':["%10d"%(balance)]})
			dfO = pd.concat([dfO, dfT], ignore_index = True, axis = 0)

print()
dfO.sort_values(by=['Balance'], inplace=True, ascending=False)
dfO.to_csv(ticker + "Cash_sorted.csv", index=False)
print(dfO)

if trade_log:
	print()
	print("Max Balance: ", "%10d"%(max(maxBalance)))
	print()

