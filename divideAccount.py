"""
swing
divide account
1st step
print - previous high, bid price, ask price
"""

import pandas as pd

ticker = "TQQQ"
iBpP = [(1/100) * x for x in range(3,4)]  # initial bid price percent
gap =  [(1/100) * x for x in range(5,6)]  # gap between bid price percent
aPp =  [(1/100) * x for x in range(1,2)]  # ask price percent compared to previous bid price
nA =   30    # number of account

dfO = pd.DataFrame(columns=['initialBid', 'gap', 'aPp', 'maxBalance', 'sum'])   # output Dataframe

log = (len(iBpP) == 1) and (len(gap) == 1) and (len(aPp) == 1)

df = pd.read_csv(ticker + ".csv")   # read csv file of stock

sr = df.iloc[0]   # first row
pH = sr[2]

print('initialBid', iBpP)
print('gap       ', gap)
print('aPp       ', aPp)
print()

for x in iBpP:
	for y in gap:
		for z in aPp:

			if log:
				print("%6.3f"%(pH))

			bP = [0] * nA  # bid price
			aF = [0] * nA  # account flag
			aP = [0] * nA  # ask price
			aB = [1] * nA  # account balance
			cT = [0] * nA  # count of trades
			pH = 0         # previous high
		
			for i in range(1, len(df)):
				sr = df.iloc[i]
				if sr[2] > pH:
					pH = sr[2]
					if log:
						print("%6.3f"%(pH))

				if (aF[0] == 0) and (sr[3] < (pH * (1 - x))):
					aF[0] = 1
					bP[0] = pH * (1 - x)
					if log:
						print('buy0', sr[0], "%6.3f"%(bP[0]))

				for bb in range(1, nA):
					# if (aF[bb] == 0) and (sr[3] < (bP[bb-1] * (1 - x - y * (bb - 1)))):
					if (aF[bb] == 0) and (sr[3] < (bP[bb-1] * (1 - x - y * (bb)))):
						aF[bb] = 1  # buy
						bP[bb] = bP[bb-1] * (1 - x - y)
						if log:
							trade = 'buy' + str(bb)
							print(trade, sr[0], "%6.3f"%(bP[bb]))


				if (aF[0] == 1) and (sr[2] > (bP[0] / (1 - x) * (1 + z))):
					aF[0] = 0  # sell
					aP[0] = bP[0] / (1 - x)
					aB[0] = aB[0] * (aP[0] / bP[0])
					cT[0] += 1
					if log:
						print('sell0', sr[0], "%6.3f"%(aP[0]), 'accoutBalance0', "%17.2f"%(aB[0]))

				for pp in reversed(range(1, nA)):
					if (aF[pp] == 1) and (sr[2] > (bP[pp-1] * (1 + z))):
						aF[pp] = 0
						aP[pp] = bP[pp-1]
						aB[pp] = aB[pp] * (aP[pp] / bP[pp])
						cT[pp] += 1
						if log:
							trade = 'sell' + str(pp)
							accoutBalance = 'accoutBalance' +  str(pp)
							print(trade, sr[0], "%6.3f"%(aP[pp]), accoutBalance, "%17.2f"%(aB[pp]))

			dfT = pd.DataFrame({'initialBid':["%6.3f"%(x)], 'gap':["%6.3f"%(y)], 'aPp':["%6.3f"%(z)], 'maxBalance':["%6d"%(max(aB))], 'sum':["%6d"%(sum(aB))]})
			dfO = pd.concat([dfO, dfT], ignore_index = True, axis = 0)

			if log:
				print()
				print('initialBid', x, '  gap', y, '  aPp', z)
				print('balance', [int(aB) for aB in aB])
				print('count ', cT)
				print()

dfO.sort_values(by=['maxBalance'], inplace=True, ascending=False)
print('by maxBalance')
print(dfO)
print()
dfO.sort_values(by=['sum'], inplace=True, ascending=False)
print('by sum')
print(dfO)
