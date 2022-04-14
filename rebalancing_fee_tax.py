"""
rebalancing: TQQQ, TMF
fee 0.07 %
tax 20 + 2 %
when no fee, no tax: 2010-2022 1.0 89:11 2% x134 (max x196 55.2%Y)
noticeable: 2010-2022 1.5 89:11 5% x166 (max x207 55.9%Y)
rebalancing price: (open + close) / 2
"""

import pandas as pd
import os


def sync(tickerA, tickerB):

    print('syncing...')

    dfA = pd.read_csv(tickerA + '.csv')
    dfB = pd.read_csv(tickerB + '.csv')
    dfO = pd.DataFrame(columns = dfA.columns)

    beginPointer = 0

    for i in range(0, len(dfA)):
        srA = dfA.iloc[i]

        for j in range(beginPointer, len(dfB)):
            srB = dfB.iloc[j]

            if srA[0] == srB[0]:
                dfT = pd.DataFrame({'Date':[srA[0]], 'Open':[srA[1]], 'High':[srA[2]], 'Low':[srA[3]], 'Close':[srA[4]], 'Adj Close':[srA[5]], 'Volume':[srA[6]]})
                dfO = pd.concat([dfO, dfT], ignore_index = True, axis = 0)
                beginPointer = j + 1

            elif srA[0] < srB[0]:
                break

    dfO.to_csv(tickerA + '_' + tickerB + '_synced.csv', index=False)
    print('synced ' + tickerA + ' with ' + tickerB)
    print()


def rebal(tickerA, tickerB):

    dfA = pd.read_csv(tickerA + "_" + tickerB + "_synced.csv")
    dfB = pd.read_csv(tickerB + "_" + tickerA + "_synced.csv")
    dfO = pd.DataFrame(columns = ['virtualAsset', 'tickerA', 'tickerB', 'threshold', 'maxYield'])

    # fee = 0
    # tax = 0
    fee = 0.0007
    tax = 0.2 + 0.02

    virtualAsset = [(1/100) * x for x in range(150, 151, 10)]
    proportionA  = [(1/100) * x for x in range(83, 84)]
    threshold    = [(1/100) * x for x in range(5, 6)]

    capital = 100000
    stockBalanceA = 0
    stockBalanceB = 0
    balanceA = 0
    balanceB = 0
    cashBalance = 0
    balance = 0
    sumFee = 0


    log = (len(virtualAsset) == 1) and (len(proportionA) == 1) and (len(threshold) == 1)
    # log = False

    for a in virtualAsset:

        for p in proportionA:
            proportionB = 1 - p

            for t in threshold:


                if t >= (1 - p):
                    break




                srA = dfA.iloc[0]
                srB = dfB.iloc[0]
                priceA = (srA[1] + srA[4]) / 2
                priceB = (srB[1] + srB[4]) / 2
                stockBalanceA = (capital * p) // priceA
                stockBalanceB = (capital * proportionB) // priceB
                cashBalance = capital - (priceA * stockBalanceA) - (priceB * stockBalanceB)
                maxYield = balance / capital
                maxDate = srA[0]

                dfBuyA = pd.DataFrame({'date':[srA[0]], 'price':[priceA], 'amount':[stockBalanceA]})
                dfBuyB = pd.DataFrame({'date':[srB[0]], 'price':[priceB], 'amount':[stockBalanceB]})
                
                dfSellA = pd.DataFrame(columns = ['date', 'price', 'amount', 'buyDate', 'buyPrice', 'revenue'])
                dfSellB = dfSellA

                dfTaxA = pd.DataFrame(columns = ['year', 'revenue', 'tax', 'profit'])
                dfTaxB = dfTaxA

                flagA = 0
                flagB = 0
                remainA = 0
                remainB = 0
                revenueA = 0
                revenueB = 0

                onceA = True
                onceB = True

                for i in range(1, len(dfA)):

                    srA = dfA.iloc[i]
                    srB = dfB.iloc[i]
                    priceA = (srA[1] + srA[4]) / 2
                    priceB = (srB[1] + srB[4]) / 2
                    balanceA = priceA * stockBalanceA
                    balanceB = priceB * stockBalanceB
                    balance = balanceA + balanceB + cashBalance

                    if i == 1:
                        previousPeriodA = (pd.Period(srA[0], freq='Y'))
                        previousPeriodB = (pd.Period(srB[0], freq='Y'))

                    if pd.Period(srA[0], freq='Y') != previousPeriodA:  ######################################## taxA
                        sumTax = (revenueA - 2500) * tax
                        if sumTax < 0:
                            sumTax = 0
                        dfT = pd.DataFrame({'year':[previousPeriodA], 'revenue':[revenueA], 'tax':[sumTax], 'profit':[revenueA - sumTax]})
                        dfTaxA = pd.concat([dfTaxA, dfT], ignore_index = True, axis = 0)

                        while cashBalance < ((balanceA / balance) * sumTax):
                            stockBalanceA -= 1
                            cashBalance += (priceA * (1 - fee))

                        cashBalance -= ((balanceA / balance) * sumTax)
                        previousPeriodA = pd.Period(srA[0], freq='Y')

                    if pd.Period(srB[0], freq='Y') != previousPeriodB:  ######################################## taxB
                        sumTax = (revenueB - 2500) * tax
                        if sumTax < 0:
                            sumTax = 0
                        dfT = pd.DataFrame({'year':[previousPeriodB], 'revenue':[revenueB], 'tax':[sumTax], 'profit':[revenueB - sumTax]})
                        dfTaxB = pd.concat([dfTaxB, dfT], ignore_index = True, axis = 0)

                        while cashBalance < ((balanceB / balance) * sumTax):
                            stockBalanceB -= 1
                            cashBalance += (priceB * (1 - fee))

                        cashBalance -= ((balanceB / balance) * sumTax)
                        previousPeriodB = pd.Period(srB[0], freq='Y')

                    if ((balanceA / balance) - p) > t:  ######################################## sell tickerA
                        amountA = ((balanceA - (balance * p)) // priceA) + 1
                        amountA *= a
                        amountA = int(amountA)

                        if amountA > stockBalanceA:
                            amountA = stockBalanceA

                        stockBalanceA -= amountA

                        if onceA:
                            srBuyA = dfBuyA.iloc[flagA]
                            remainA = srBuyA[2]
                            onceA = False

                        if amountA < remainA:
                            dfT = pd.DataFrame({'date':[srA[0]], 'price':[priceA], 'amount':[amountA], 'buyDate':[srBuyA[0]], 'buyPrice':[srBuyA[1]], 'revenue':[(priceA - srBuyA[1]) * amountA]})
                            dfSellA = pd.concat([dfSellA, dfT], ignore_index = True, axis = 0)
                            remainA -= amountA
                            revenueA += (priceA - srBuyA[1]) * amountA

                        elif amountA == remainA:
                            dfT = pd.DataFrame({'date':[srA[0]], 'price':[priceA], 'amount':[amountA], 'buyDate':[srBuyA[0]], 'buyPrice':[srBuyA[1]], 'revenue':[(priceA - srBuyA[1]) * amountA]})
                            dfSellA = pd.concat([dfSellA, dfT], ignore_index = True, axis = 0)
                            remainA = 0
                            flagA += 1
                            revenueA += (priceA - srBuyA[1]) * amountA

                        else:
                            while amountA > remainA:
                                dfT = pd.DataFrame({'date':[srA[0]], 'price':[priceA], 'amount':[remainA], 'buyDate':[srBuyA[0]], 'buyPrice':[srBuyA[1]], 'revenue':[(priceA - srBuyA[1]) * remainA]})
                                dfSellA = pd.concat([dfSellA, dfT], ignore_index = True, axis = 0)
                                amountA -= remainA




                                flagA += 1




                                srBuyA = dfBuyA.iloc[flagA]
                                remainA = srBuyA[2]
                                revenueA += (priceA - srBuyA[1]) * remainA

                                if amountA < remainA:
                                    dfT = pd.DataFrame({'date':[srA[0]], 'price':[priceA], 'amount':[amountA], 'buyDate':[srBuyA[0]], 'buyPrice':[srBuyA[1]], 'revenue':[(priceA - srBuyA[1]) * remainA]})
                                    dfSellA = pd.concat([dfSellA, dfT], ignore_index = True, axis = 0)
                                    remainA -= amountA
                                    revenueA += (priceA - srBuyA[1]) * remainA
                                    break

                        amountB = ((amountA * priceA) + cashBalance) // priceB

                        stockBalanceB += amountB  ######################################## buy tickerB

                        dfT = pd.DataFrame({'date':[srB[0]], 'price':[priceB], 'amount':[amountB]})
                        dfBuyB = pd.concat([dfBuyB, dfT], ignore_index = True, axis = 0)

                        cashBalance = (amountA * priceA + cashBalance) % priceB

                        while (((amountA * priceA) + (amountB * priceB)) * fee) > cashBalance:  # fee
                            stockBalanceA -= 1                                                  # fee
                            cashBalance += priceA                                               # fee

                        cashBalance -= ((amountB * priceB) + (amountA * priceA)) * fee          # fee
                        sumFee += ((amountB * priceB) + (amountA * priceA)) * fee               # fee
                        print(sumFee)



                        
                        balance = balanceA + balanceB + cashBalance

                    elif ((balanceB / balance) - proportionB) > t:  ######################################## sell tickerB
                        amountB = ((balanceB - (balance * proportionB)) // priceB) + 1
                        amountB *= a
                        amountB = int(amountB)

                        if amountB > stockBalanceB:
                            amountB = stockBalanceB

                        stockBalanceB -= amountB

                        if onceB:
                            srBuyB = dfBuyB.iloc[flagB]
                            remainB = srBuyB[2]
                            onceB = False

                        if amountB < remainB:
                            dfT = pd.DataFrame({'date':[srB[0]], 'price':[priceB], 'amount':[amountB], 'buyDate':[srBuyB[0]], 'buyPrice':[srBuyB[1]], 'revenue':[(priceB - srBuyB[1]) * amountB]})
                            dfSellB = pd.concat([dfSellB, dfT], ignore_index = True, axis = 0)
                            remainB -= amountB
                            revenueB += (priceB - srBuyB[1]) * amountB

                        elif amountB == remainB:
                            dfT = pd.DataFrame({'date':[srB[0]], 'price':[priceB], 'amount':[amountB], 'buyDate':[srBuyB[0]], 'buyPrice':[srBuyB[1]], 'revenue':[(priceB - srBuyB[1]) * amountB]})
                            dfSellB = pd.concat([dfSellB, dfT], ignore_index = True, axis = 0)
                            remainB = 0
                            flagB += 1
                            revenueB += (priceB - srBuyB[1]) * amountB

                        else:
                            while amountB > remainB:
                                dfT = pd.DataFrame({'date':[srB[0]], 'price':[priceB], 'amount':[remainB], 'buyDate':[srBuyB[0]], 'buyPrice':[srBuyB[1]], 'revenue':[(priceB - srBuyB[1]) * remainB]})
                                dfSellB = pd.concat([dfSellB, dfT], ignore_index = True, axis = 0)
                                amountB -= remainB


                                flagB += 1
                                # print(dfBuyB.last_valid_index())
                                # need to fix

                                # if dfBuyB.last_valid_index() < flagB:
                                #     flagB -= 1
                                #     break


                                # print('=====>', flagB)
                                print(dfBuyB)
                                print(dfSellB)



                                srBuyB = dfBuyB.iloc[flagB]
                                remainB = srBuyB[2]
                                revenueB += (priceB - srBuyB[1]) * remainB

                                if amountB < remainB:
                                    dfT = pd.DataFrame({'date':[srB[0]], 'price':[priceB], 'amount':[amountB], 'buyDate':[srBuyB[0]], 'buyPrice':[srBuyB[1]], 'revenue':[(priceB - srBuyB[1]) * amountB]})
                                    dfSellB = pd.concat([dfSellB, dfT], ignore_index = True, axis = 0)
                                    remainB -= amountB
                                    revenueB += (priceB - srBuyB[1]) * amountB
                                    break

                        amountA = (amountB * priceB + cashBalance) // priceA

                        stockBalanceA += amountA  ######################################## buy tickerA

                        dfT = pd.DataFrame({'date':[srA[0]], 'price':[priceA], 'amount':[amountA]})
                        dfBuyA = pd.concat([dfBuyA, dfT], ignore_index = True, axis = 0)

                        cashBalance = (amountB * priceB + cashBalance) % priceA

                        while (((amountB * priceB) + (amountA * priceA)) * fee) > cashBalance:  # fee
                            stockBalanceB -= 1                                                  # fee
                            cashBalance += priceB                                               # fee

                        cashBalance -= ((amountB * priceB) + (amountA * priceA)) * fee          # fee
                        sumFee += ((amountB * priceB) + (amountA * priceA)) * fee               # fee
                        print(sumFee)




                        balance = balanceA + balanceB + cashBalance

                    if (balance / capital) > maxYield:
                        maxYield = balance / capital
                        maxDate = srA[0]

                    # if log:
                    #     print(srA[0], int(stockBalanceA), ',' ,int(stockBalanceB), ',' ,int(maxYield))

                if log:
                    print(tickerA)
                    print(dfSellA)
                    print()
                    print(tickerA)
                    print(dfTaxA)
                    print()
                    print(tickerB)
                    print(dfSellB)
                    print()
                    print(tickerB)
                    print(dfTaxB)
                    print()
                    print('sumFee', int(sumFee))
                    print()
                    print('revenueA', revenueA)
                    print('revenueB', revenueB)
                    print('revenue', revenueA + revenueB)
                    print()
                    print('max', maxDate, int(maxYield))
                    print()

                print("%4.2f"%(a), "%4.2f"%(p), "%4.2f"%(t), str(int(maxYield)) + 'x')
                print()

                balanceA = priceA * stockBalanceA
                balanceB = priceB * stockBalanceB
                balance = balanceA + balanceB + cashBalance

                dfT = pd.DataFrame({'virtualAsset':["%5.2f"%(a)], 'tickerA':["%5.2f"%(p)], 'tickerB':["%5.2f"%(proportionB)], 'threshold':["%5.2f"%(t)], 'maxYield':["%4d"%(maxYield)]})
                dfO = pd.concat([dfO, dfT], ignore_index = True, axis = 0)

    dfO.to_csv(tickerA + "_" + tickerB + "_rebalanced.csv", index=False)


def sort(tickerA, tickerB):
    df = pd.read_csv(tickerA + "_" + tickerB + "_rebalanced.csv")
    df.sort_values(by=['maxYield'], inplace=True, ascending=False)
    df.to_csv(tickerA + "_" + tickerB + "_sorted.csv", index=False)
    sr = df.iloc[0]
    print(tickerA, sr[1], '  ', tickerB, sr[2], '  ', 'virtualAsset', sr[0], '  ', 'threshold', sr[3], '  ', 'maxYield', str("%4d"%(sr[4])) + 'x')
    print()


def main(tickerA, tickerB):
    pathA = "D:/soxlVr/" + tickerA + "_" + tickerB + "_synced.csv"
    pathB = "D:/soxlVr/" + tickerB + "_" + tickerA + "_synced.csv"
    # pathA = "C:/dell/python/backtesting/soxlVr/" + tickerA + "_" + tickerB + "_synced.csv"
    # pathB = "C:/dell/python/backtesting/soxlVr/" + tickerB + "_" + tickerA + "_synced.csv"

    if (os.path.isfile(pathA)==False) or (os.path.isfile(pathB)==False):
        sync(tickerA, tickerB)
        sync(tickerB, tickerA)

    else:
        print('synced')
        print()

    rebal(tickerA, tickerB)

    sort(tickerA, tickerB)


tickerA = 'TQQQ'
tickerB = 'TMF'


main(tickerA, tickerB)
