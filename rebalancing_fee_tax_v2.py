"""
rebalancing: TQQQ, TMF
fee 0.07 %
tax 20 + 2 %
when no fee, no tax: 2010-2022 1.0 89:11 2% x134 (max x196 55.2%Y)
noticeable: 2010-2022 1.5 89:11 5% x166 (max x207 55.9%Y)
rebalancing price: close
start date: 2010.2.18. (highest close price of the month)
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
    dfO = pd.DataFrame(columns = ['V_Asset', 'tickerA', 'tickerB', 'threshold', 'maxYield'])

    # F_Rate = 0
    T_Rate = 0
    F_Rate = 0.0007  # fee rate
    # T_Rate = 0.2 + 0.02  # tax rate

    V_Asset     = [(1/100) * x for x in range(50, 201, 5)]
    proportionA = [(1/100) * x for x in range(60, 91, 5)]
    threshold   = [(1/1000) * x for x in range(1, 41)]

    capital    = 100000
    S_BalanceA = 0  # stock balance
    S_BalanceB = 0
    balanceA   = 0
    balanceB   = 0
    balance    = 0
    B_Flag     = False  # break flag


    # log = (len(V_Asset) == 1) and (len(proportionA) == 1) and (len(threshold) == 1)
    log = False

    maxYield = balance / capital
    aa, pp, tt, Yield= 0, 0, 0, 0
    Date = '1900-01-01'

    for a in V_Asset:

        for p in proportionA:
            proportionB = 1 - p

            for t in threshold:

                if (p > 0.5) and ((p + (t * a)) >= 1):
                    print('break: p + (t * a) >=', "%4.2f"%(p + (t * a)))
                    B_Flag = True
                    break

                if (proportionB > 0.5) and ((proportionB + (t * a)) >= 1):
                    print('break: proportionB + (t * a) >=', "%4.2f"%(proportionB + (t * a)))
                    B_Flag = True
                    break

                C_Balance = capital  # cash balance
                srA = dfA.iloc[0]
                srB = dfB.iloc[0]

                quantityA = (C_Balance * p) / (srA[4] * (1 + F_Rate))
                S_BalanceA = int(quantityA)
                feeA = (srA[4] * S_BalanceA) * F_Rate
                C_Balance -= (srA[4] * S_BalanceA) * (1 + F_Rate)

                quantityB = C_Balance / (srB[4] * (1 + F_Rate))
                S_BalanceB = int(quantityB)
                feeB = (srB[4] * S_BalanceB) * F_Rate
                C_Balance -= (srB[4] * S_BalanceB) * (1 + F_Rate)

                balance = (srA[4] * S_BalanceA) + (srB[4] * S_BalanceB) + C_Balance

                dfBuyA = pd.DataFrame({'date':[srA[0]], 'price':[srA[4]], 'quantity':[S_BalanceA], 'amount':[srA[4] * S_BalanceA], 'fee':[feeA]})
                dfBuyB = pd.DataFrame({'date':[srB[0]], 'price':[srB[4]], 'quantity':[S_BalanceB], 'amount':[srB[4] * S_BalanceB], 'fee':[feeB]})

                dfSellA = pd.DataFrame(columns = ['date', 'price', 'quantity', 'dateBought', 'priceBought', 'amount', 'fee', 'revenue'])
                dfSellB = dfSellA

                dfTaxA = pd.DataFrame(columns = ['year', 'revenue', 'tax', 'profit'])
                dfTaxB = dfTaxA

                flagA = 0
                flagB = 0
                remainA = 0
                remainB = 0
                revenueA = 0
                revenueB = 0
                yieldNow = 0

                onceA = True
                onceB = True

                for i in range(1, len(dfA)):
                    if B_Flag:
                        break

                    if (quantityA < 0) or (quantityB < 0):
                        print('minus')

                    srA = dfA.iloc[i]
                    srB = dfB.iloc[i]

                    if i == 1:  # tax =======================================
                        previousPeriodA = (pd.Period(srA[0], freq='Y'))
                        previousPeriodB = (pd.Period(srB[0], freq='Y'))

                    if pd.Period(srA[0], freq='Y') != previousPeriodA:  # tax tickerA =======================================
                        sumTax = (revenueA - 2500) * T_Rate
                        if sumTax < 0:
                            sumTax = 0
                        dfT = pd.DataFrame({'year':[previousPeriodA], 'revenue':[revenueA], 'tax':[sumTax], 'profit':[revenueA - sumTax]})
                        dfTaxA = pd.concat([dfTaxA, dfT], ignore_index = True, axis = 0)

                        while C_Balance < ((balanceA / balance) * sumTax):
                            S_BalanceA -= 1
                            C_Balance += srA[4] * (1 - F_Rate)

                        C_Balance -= (balanceA / balance) * sumTax
                        previousPeriodA = pd.Period(srA[0], freq='Y')

                    if pd.Period(srB[0], freq='Y') != previousPeriodB:  # tax tickerB =======================================
                        sumTax = (revenueB - 2500) * T_Rate
                        if sumTax < 0:
                            sumTax = 0
                        dfT = pd.DataFrame({'year':[previousPeriodB], 'revenue':[revenueB], 'tax':[sumTax], 'profit':[revenueB - sumTax]})
                        dfTaxB = pd.concat([dfTaxB, dfT], ignore_index = True, axis = 0)

                        while C_Balance < ((balanceB / balance) * sumTax):
                            S_BalanceB -= 1
                            C_Balance += srB[4] * (1 - F_Rate)

                        C_Balance -= (balanceB / balance) * sumTax
                        previousPeriodB = pd.Period(srB[0], freq='Y')

                    balanceA = srA[4] * S_BalanceA
                    balanceB = srB[4] * S_BalanceB
                    balance = balanceA + balanceB + C_Balance

                    if (((balanceA / balance) - p) * 2) > t:  # sell tickerA, buy tickerB =======================================
                        quantityA = int(((balanceA - (balance * p)) / srA[4]) * (1 + F_Rate) * a) + 1  # sell tickerA =======================================

                        if quantityA > S_BalanceA:
                            quantityA = S_BalanceA

                        S_BalanceA -= quantityA
                        feeA = (srA[4] * quantityA) * F_Rate
                        C_Balance = C_Balance + (srA[4] * quantityA) - feeA

                        if onceA:
                            srBuyA = dfBuyA.iloc[flagA]
                            remainA = srBuyA[2]
                            onceA = False

                        while quantityA > remainA:
                            remainQuantityA = quantityA - remainA
                            quantityA = remainA

                            amount = srA[4] * quantityA
                            revenueA = (srA[4] - srBuyA[1]) * quantityA - feeA

                            dfT = pd.DataFrame({'date':[srA[0]], 'price':[srA[4]], 'quantity':[quantityA], 'dateBought':[srBuyA[0]], 'priceBought':[srBuyA[4]], 'amount':[amount], 'fee':[feeA], 'revenue':[revenueA]})
                            dfSellA = pd.concat([dfSellA, dfT], ignore_index = True, axis = 0)

                            quantityA = remainQuantityA

                            flagA += 1
                            if dfBuyA.last_valid_index() < flagA:
                                    B_Flag = True
                                    break

                            srBuyA = dfBuyA.iloc[flagA]
                            remainA = srBuyA[2]

                        if quantityA < remainA:
                            remainA -= quantityA

                        if quantityA == remainA:
                            flagA += 1
                            if dfBuyA.last_valid_index() < flagA:
                                    B_Flag = True
                                    break

                            srBuyA = dfBuyA.iloc[flagA]
                            remainA = srBuyA[2]

                        amount = srA[4] * quantityA
                        revenueA = (srA[4] - srBuyA[1]) * quantityA - feeA

                        dfT = pd.DataFrame({'date':[srA[0]], 'price':[srA[4]], 'quantity':[quantityA], 'dateBought':[srBuyA[0]], 'priceBought':[srBuyA[4]], 'amount':[amount], 'fee':[feeA], 'revenue':[revenueA]})
                        dfSellA = pd.concat([dfSellA, dfT], ignore_index = True, axis = 0)

                        # print(srA[0], balance)

                        quantityB = int(C_Balance / (srB[4] * (1 + F_Rate)))  # buy tickerB =======================================
                        # print('C_Balance buy tickerB', C_Balance)
                        S_BalanceB += quantityB
                        amount = srB[4] * quantityB
                        feeB = (srB[4] * quantityB) * F_Rate
                        C_Balance = C_Balance - (srB[4] * quantityB) - feeB

                        dfT = pd.DataFrame({'date':[srB[0]], 'price':[srB[4]], 'quantity':[quantityB], 'amount':[amount], 'fee':[feeB]})
                        dfBuyB = pd.concat([dfBuyB, dfT], ignore_index = True, axis = 0)



                    if (((balanceB / balance) - proportionB) * 2) > t:  # sell tickerB, buy tickerA =======================================
                        quantityB = int(((balanceB - (balance * proportionB)) / srB[4]) * (1 + F_Rate) * a) + 1  # sell tickerB =======================================

                        if quantityB > S_BalanceB:
                            quantityB = S_BalanceB

                        S_BalanceB -= quantityB
                        feeB = (srB[4] * quantityB) * F_Rate
                        C_Balance = C_Balance + (srB[4] * quantityB) - feeB

                        if onceB:
                            srBuyB = dfBuyB.iloc[flagB]
                            remainB = srBuyB[2]
                            onceB = False

                        while quantityB > remainB:
                            remainQuantityB = quantityB - remainB
                            quantityB = remainB

                            amount = srB[4] * quantityB
                            revenueB = (srB[4] - srBuyB[1]) * quantityB - feeB

                            dfT = pd.DataFrame({'date':[srB[0]], 'price':[srB[4]], 'quantity':[quantityB], 'dateBought':[srBuyB[0]], 'priceBought':[srBuyB[4]], 'amount':[amount], 'fee':[feeB], 'revenue':[revenueB]})
                            dfSellB = pd.concat([dfSellB, dfT], ignore_index = True, axis = 0)

                            quantityA = remainQuantityB

                            flagB += 1
                            if dfBuyB.last_valid_index() < flagB:
                                    B_Flag = True
                                    break

                            srBuyB = dfBuyB.iloc[flagB]
                            remainB = srBuyB[2]

                        if quantityB < remainB:
                            remainB -= quantityB

                        if quantityB == remainB:
                            flagB += 1
                            if dfBuyB.last_valid_index() < flagB:
                                    B_Flag = True
                                    break

                            srBuyB = dfBuyB.iloc[flagB]
                            remainB = srBuyB[2]

                        amount = srB[4] * quantityB
                        revenueB = (srB[4] - srBuyB[1]) * quantityB - feeB

                        dfT = pd.DataFrame({'date':[srB[0]], 'price':[srB[4]], 'quantity':[quantityB], 'dateBought':[srBuyB[0]], 'priceBought':[srBuyB[4]], 'amount':[amount], 'fee':[feeB], 'revenue':[revenueB]})
                        dfSellB = pd.concat([dfSellB, dfT], ignore_index = True, axis = 0)

                        # print(srA[0], balance)

                        quantityA = int(C_Balance / (srA[4] * (1 + F_Rate)))  # buy tickerA =======================================
                        S_BalanceA += quantityA
                        amount = srA[4] * quantityA
                        feeA = (srA[4] * quantityA) * F_Rate
                        C_Balance = C_Balance - (srA[4] * quantityA) - feeA

                        dfT = pd.DataFrame({'date':[srA[0]], 'price':[srA[4]], 'quantity':[quantityA], 'amount':[amount], 'fee':[feeA]})
                        dfBuyA = pd.concat([dfBuyA, dfT], ignore_index = True, axis = 0)

                    balanceA = srA[4] * S_BalanceA
                    balanceB = srB[4] * S_BalanceB
                    balance = balanceA + balanceB + C_Balance

                    # print(srA[0], ', ', int(balance))

                    Yield = balance / capital
                    if i == (len(dfA) - 1):
                        yieldNow = Yield
                    sumFee = dfBuyA['fee'].sum() + dfBuyB['fee'].sum() + dfSellA['fee'].sum() + dfSellB['fee'].sum()
                if log:
                    print(dfBuyA)
                    print(dfBuyB)
                    print(dfSellA)
                    print(dfSellB)
                    print(dfTaxA)
                    print(dfTaxB)
                    print('sumFee', int(sumFee))
                    print('yieldNow', "%5.1f"%(yieldNow))

                if not log:
                    print('a', a, 'p', p, 't', t, 'Yield', "%5.1f"%(Yield))

                if (Yield > maxYield) or (int(Yield) == 0):
                    maxYield = Yield
                    aa, pp, tt = a, p, t
                    Date = srA[0]

                dfT = pd.DataFrame({'V_Asset':["%5.2f"%(a)], 'tickerA':["%5.2f"%(p)], 'tickerB':["%5.2f"%(proportionB)], 'threshold':["%5.2f"%(t)], 'maxYield':["%5.1f"%(maxYield)]})
                dfO = pd.concat([dfO, dfT], ignore_index = True, axis = 0)

    dfO.to_csv(tickerA + "_" + tickerB + "_rebalanced.csv", index=False)
    print('a', aa, 'p', pp, 't', tt, Date, 'maxYield', "%5.1f"%(maxYield))


def sort(tickerA, tickerB):
    df = pd.read_csv(tickerA + "_" + tickerB + "_rebalanced.csv")
    df.sort_values(by=['maxYield'], inplace=True, ascending=False)
    df.to_csv(tickerA + "_" + tickerB + "_sorted.csv", index=False)
    print()
    pass


def main(tickerA, tickerB):
    # pathA = "D:/soxlVr/" + tickerA + "_" + tickerB + "_synced.csv"
    # pathB = "D:/soxlVr/" + tickerB + "_" + tickerA + "_synced.csv"
    pathA = "D:/_soxlVr/test/" + tickerA + "_" + tickerB + "_synced.csv"
    pathB = "D:/_soxlVr/test/" + tickerB + "_" + tickerA + "_synced.csv"
    # pathA = "C:/dell/python/backtesting/soxlVr/" + tickerA + "_" + tickerB + "_synced.csv"
    # pathB = "C:/dell/python/backtesting/soxlVr/" + tickerB + "_" + tickerA + "_synced.csv"

    print(tickerA, tickerB)

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
