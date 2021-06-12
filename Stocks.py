#-------------------------------------------------------------------------------
# Name:        Stocks
# Purpose: Provide easy access to fundamentals and technical data for DD
#
# Author:      John Eichenberger
#
# Created:     11/06/2021
# Copyright:   (c) John Eichenberger 2020
# Licence:     GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
#-------------------------------------------------------------------------------

# !pip install yfinance
# !pip install matplotlib
# !pip install yahoofinancials

from yahoofinancials import YahooFinancials as yf
import matplotlib.pyplot as mplt
from matplotlib import style as mpstyle

import glob, re, os, sys, time

from math import log, floor

def big_number(number):
    """ Format a big number as a short string with a unit postfix """
    units = ['', 'K', 'M', 'G', 'T', 'P']
    k = 1000.0
    try:
        magnitude = int(floor(log(number, k)))
        return '%.2f%s' % (number / k**magnitude, units[magnitude])
    except:
        return '0'

def main(ticker):
    """ Display stock data for one ticker """
    stock = yf(ticker)


    data = stock.get_stock_price_data()[ticker]
    if data == None:
        print("{} not found".format(ticker))
        return

    # Display common values
    print("{}:{} ({}) {}".format(data['symbol'], data['exchangeName'], data['quoteType'], data['shortName']))

    marketCAP = data['marketCap'] # Not displayed yet

    # Current prices
    print('Yesterday:{}  '.format(data['regularMarketPreviousClose']), end='');
    if data['quoteType'] == 'MUTUALFUND':
        print('Today:{}  '.format(data['regularMarketPrice']))
        return

    if data['preMarketPrice'] != None:
        print('Pre-Market:{}  '.format(data['preMarketPrice']), end='')

    if data['postMarketPrice'] != None:
        print('Open:{}  Close:{}  Post-Market:{}  High:{}  Low:{}'.format(
            data['regularMarketOpen']
            , data['regularMarketPrice']
            , data['postMarketPrice']
            , data['regularMarketDayHigh']
            , data['regularMarketDayLow']))
    else:
        print('Open:{}  Current:{}  '.format(data['regularMarketOpen']
            , data['regularMarketPrice']))

    # compare volumes, is volume increasing or decreasing
    try:
        print('Volume:{:,}  10DayAve:{:,}  3MonthAve:{:,}'.format(
            data['regularMarketVolume']
            , data['averageDailyVolume10Day']
            , data['averageDailyVolume3Month']
            ))
    except:
        print('Volume:{:,}'.format(data['regularMarketVolume']))

    if data['volume24Hr'] != None:
        print('Volume24Hr:{}  VolAll:{}'.format(
        data['volumeAllCurrencies']
        , data['volume24Hr']
        ))

    # for quoteType == 'OPTION'
    # 'strikePrice': None
    # 'underlyingSymbol': None,
    # 'expireDate'
    # 'openInterest'

    if data['quoteType'] != 'EQUITY':
        return

    data = stock.get_stock_earnings_data()
    if data[ticker] == None:
        print("Index and ETF funds have no earnings")
    else:
        print()
        print('EPS earnings:')
        earnings = data[ticker]['earningsData']
        for q in earnings['quarterly']:
            print("{}".format(q['date']),end='\t\t')
        try:
            currentQ = earnings['currentQuarterEstimateDate'] + \
                earnings['currentQuarterEstimateYear']
        except:
            currentQ = "NextQ"
        print(currentQ)

        # formatting uses an inconsistent number of columns
        for q in earnings['quarterly']:
            actual = q['actual']
            estimate = actual - q['estimate']
            print("{0:1.2f}({1:+1.2f})".format(actual, estimate),end='\t')
        print("{0:+1.2f}".format(earnings['currentQuarterEstimate']))

        print()
        print('Revenue:')
        financials = data[ticker]['financialsData']
        for q in financials['yearly']:
            print("{0:<8}".format(q['date']),end='')
        for q in financials['quarterly']:
            print("{0:<8}".format(q['date']),end='')
        print()

        for q in financials['yearly']:
            print("{0:<8}".format(big_number(q['revenue'])), end='')
        for q in financials['quarterly']:
            print("{0:<8}".format(big_number(q['revenue'])), end='')
        print()

        print()
        print('Earnings:')
        financials = data[ticker]['financialsData']
        for q in financials['yearly']:
            print("{0:<8}".format(q['date']),end='')
        for q in financials['quarterly']:
            print("{0:<8}".format(q['date']),end='')
        print()

        for q in financials['yearly']:
            print("{0:<8}".format(big_number(q['earnings'])), end='')
        for q in financials['quarterly']:
            print("{0:<8}".format(big_number(q['earnings'])), end='')
        print()


    # data = stock.get_financial_stmts('quarterly', 'income')
    # data = stock.get_financial_stmts('quarterly', 'balance')
    #   commonStock
    # data = stock.get_financial_stmts('quarterly', 'cash')
    #   netIncome
    # data = stock.get_financial_stmts('annual', 'balance')
    # lots of data, but maybe nothing I care about yet?

    # stock.get_summary_data() -- I might even want to use this instead of get_stock_price_data, well... not quite
    # 'beta'
    # 'dividendRate'
    # 'dividendYield'
    # 'exDividendDate'
    # 'fiftyDayAverage'
    # 'fiftyTwoWeekHigh'
    # 'fiftyTwoWeekLow'
    # 'forwardPE'
    # 'marketCap' (again)
    # 'twoHundredDayAverage'

    #     get_num_shares_outstanding(price_type=’current’)
    #        price_type can also be set to ‘average’ to calculate the shares outstanding with the daily average price.

""" Functions to explore
    get_historical_price_data(start_date, end_date, time_interval)
        This method will pull historical pricing data for stocks, currencies, ETFs, mutual funds, U.S. Treasuries, cryptocurrencies, commodities, and indexes.
        start_date should be entered in the ‘YYYY-MM-DD’ format and is the first day that data will be pulled for.
        end_date should be entered in the ‘YYYY-MM-DD’ format and is the last day that data will be pulled for.
        time_interval can be either ‘daily’, ‘weekly’, or ‘monthly’. This variable determines the time period interval for your pull.
        Data response includes relevant pricing event data such as dividends and stock splits.

    get_research_and_development()
    get_pe_ratio()

    get_interest_expense()
    get_50day_moving_avg()
    get_200day_moving_avg()
    get_beta()
    get_book_value()
    get_ebit()
    get_key_statistics_data()
"""

if __name__ == '__main__':
    for arg in sys.argv[1:]:
        main(arg.upper())