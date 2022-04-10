"""
swing
to follow chart
1st drop then rise, 2nd drop then rise, ...
"""


import pandas as pd

ticker = 'SOXL'
# cashFlow = 10000
dropP = [(1/100) * x for x in range(10,11)]  # drop percent
riseP = [(1/100) * x for x in range(12,13)]  # rise percent
weightP = [(1/100) * x for x in range(10,11)]  # weight percent
nA = 20  # number of account

df = pd.read_csv(ticker + '.csv')
# dfO = pd.DataFrame(columns=['date', 'price', 'amount', 'cash', 'balance', 'capital'])


for x in dropP:
	for y in riseP:
		for z in weightP:
			# high = 0

				aB = [1] * nA  # account balance
				aBP = [0] * nA  # account buy price
				aF = 0  # account flag

				sr  = df.iloc[0]
				high = sr[2]

				for i in range(1,len(df)):
					sr  = df.iloc[i]


					if sr[2] > high:
						high = sr[2]
						# print(sr[0], 'high', "%5.2f"%(high))


					if (aF == 0) and (aBP[0] > 0) and (sr[2] > (aBP[0] * (1 + y))):
						sellPrice = aBP[0] * (1 + y)
						aBpre = aB[0]
						aB[0] = aBpre * (sellPrice / aBP[0])
						aBP[0] = 0
						# print(sr[0], 'sell', 0, "%5.2f"%(sellPrice), aBP)
						print('aB[ 0 ]', "%5.2f"%(aB[0]))
						print()
						high = sr[2]
						aF = 0

					for j in range(aF,0,-1):
						if sr[2] > aBP[j-1]:
							aBpre = aB[j]
							aB[j] = aBpre * (aBP[j-1] / aBP[j])
							print('aB[', j, ']', "%5.2f"%(aB[j]))
							aBP[j] = 0
							# print(sr[0], 'sell', j, "%5.2f"%(aBP[j-1]), ["%.2f" % elem for elem in aBP])
							high = sr[2]
							aF = j - 1
						else:
							break

					if sr[3] < (high * (1 - x) * (1 - z)):
						for j in range(0,nA):
							if aBP[j] == 0:
								aBP[j] = high * (1 - x)
								# print(sr[0], 'buy', j, "%5.2f"%(aBP[j]), ["%.2f" % elem for elem in aBP])
								high = aBP[j]
								aF = j
								break

				print(["%.2f" % elem for elem in aB])
