import time
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from pytz import timezone





connection_attempts = 5





financial_features_names = ["Enterprise Value",
                            "Trailing P/E",
                            "Price/Sales",
                            "Price/Book",
                            "Enterprise Value/Revenue",
                            "Enterprise Value/EBITDA",
                            "Beta",
                            "Trailing Annual Dividend Yield",
                            "Profit Margin",
                            "Operating Margin",
                            "Return on Assets",
                            "Return on Equity",
                            "Revenue",
                            "Gross Profit",
                            "EBITDA",
                            "Total Cash",
                            "Total Debt",
                            "Total Debt/Equity",
                            "Operating Cash Flow"
                            ]

financial_websites = ["https://www.forbes.com/",
                      "https://www.marketwatch.com/",
                      "https://www.wsj.com/news/economy",
                      #"https://bloomberg.com/",
                      "https://www.reuters.com/",
                      "https://finance.yahoo.com/",
                      #"https://www.investopedia.com/",
                      "https://money.cnn.com/",
                      "https://cnbc.com/",
                      "https://ibtimes.com/",
                      #"https://seekingalpha.com/",
                      "https://fortune.com/",
                      "https://economist.com/",
                      "https://ft.com/",
                      "https://www.morningstar.com/news/",
                      "https://thestreet.com/",
                      #"https://nasdaq.com/",
                      "https://moneymorning.com/",
                      "https://business-standard.com/",
                      "https://kiplinger.com/"
                      ]



def wait_for_stock_market_open():
    # NYSE opens at 09:30 in the morning
    print("Waiting for the stock market to open...\n")
    new_york_timezone = timezone("US/Eastern")
    the_time = datetime.now(new_york_timezone)
    current_hour = float(the_time.strftime('%H'))
    current_minute = float(the_time.strftime('%M'))


    the_time = datetime.now(new_york_timezone)
    current_hour = float(the_time.strftime('%H'))

    while current_hour >= 9:
        time.sleep(60)
        the_time = datetime.now(new_york_timezone)
        current_hour = float(the_time.strftime('%H'))

    while current_hour < 9:
        time.sleep(60)
        the_time = datetime.now(new_york_timezone)
        current_hour = float(the_time.strftime('%H'))

    return



def wait_for_stock_market_close():
    # NYSE closes at 16:00 in the afternoon
    print("Waiting for the stock market to close...\n")
    new_york_timezone = timezone("US/Eastern")
    the_time = datetime.now(new_york_timezone)
    current_hour = float(the_time.strftime('%H'))

    # Waits for the (american) stock market to close
    while current_hour < 17:
        time.sleep(60)
        the_time = datetime.now(new_york_timezone)
        current_hour = float(the_time.strftime('%H'))

    return



def fix_number_format(x):
    try:
        return float(x)
    except ValueError:
        x = x.replace(',', '')
        if x[-1] == '%':
            return x[:-1]
        else:
            y = float(x[:-1])
            if x[-1] == 'M':
                y *= 1e6
            elif x[-1] == 'B':
                y *= 1e9
            elif x[-1] == 'T':
                y *= 1e12
            return y



def get_news_sentiments():
    sentiment_results = np.zeros(0)
    for url in financial_websites:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text()
        text = text.lower()

        positive_words_occurence = 0
        negative_words_occurence = 0
        for n in range(len(positive_words_list)):
            positive_words_occurence += len(re.findall(positive_words_list[n], text))
        for n in range(len(negative_words_list)):
            negative_words_occurence += len(re.findall(negative_words_list[n], text))
        sentiment_results = np.append(sentiment_results, [positive_words_occurence, negative_words_occurence])

        time.sleep(1)

    return sentiment_results






def get_financial_data(ticker):
    financial_data = np.zeros(len(financial_features_names) + len(sector_numbers))
    url = 'https://finance.yahoo.com/quote/' + ticker + '/key-statistics?p=' + ticker
    numbers = pd.read_html(url)

    # Eterprise Value
    financial_data[0] = fix_number_format(numbers[0][1][1])

    # Trailing P/E
    financial_data[1] = fix_number_format(numbers[0][1][2])

    # Price/Sales
    financial_data[2] = fix_number_format(numbers[0][1][5])

    # Price/Book
    financial_data[3] = fix_number_format(numbers[0][1][6])

    # Enterprise Value/Revenue
    financial_data[4] = fix_number_format(numbers[0][1][7])

    # Enterprise Value/EBITDA
    financial_data[5] = fix_number_format(numbers[0][1][8])

    # Beta
    financial_data[6] = fix_number_format(numbers[1][1][0])

    # Trailing Annual Dividend Yield
    financial_data[7] = fix_number_format(numbers[1][1][3])

    # Profit Margin
    financial_data[8] = fix_number_format(numbers[5][1][0])

    # Operating Margin
    financial_data[9] = fix_number_format(numbers[5][1][1])

    # Return on Assets
    financial_data[10] = fix_number_format(numbers[6][1][0])

    # Return on Equity
    financial_data[11] = fix_number_format(numbers[6][1][1])

    # Revenue
    financial_data[12] = fix_number_format(numbers[7][1][0])

    # Gross Profit
    financial_data[13] = fix_number_format(numbers[7][1][3])

    # EBITDA
    financial_data[14] = fix_number_format(numbers[7][1][4])

    # Total Cash
    financial_data[15] = fix_number_format(numbers[8][1][0])

    # Total Debt
    financial_data[16] = fix_number_format(numbers[8][1][2])

    # Total Debt/Equity
    financial_data[17] = fix_number_format(numbers[8][1][3])

    # Operating Cash Flow
    financial_data[18] = fix_number_format(numbers[9][1][0])

    # Sector
    financial_data[19 + sector_numbers[company_sectors[ticker]]] = 1

    return financial_data



def get_daily_result(ticker):
    url = 'https://finance.yahoo.com/quote/' + ticker + '/history?p=' + ticker
    numbers = pd.read_html(url)
    open = numbers[0]["Open"][0]
    close = numbers[0]["Adj Close**"][0]

    daily_result = float(close) / float(open)
    daily_result -= 1
    return daily_result



def stock_market_was_open_today():
    try:
        url = 'https://finance.yahoo.com/quote/MSFT/history?p=MSFT'
        numbers = pd.read_html(url)
        last_day_open = numbers[0]["Date"][0]

        new_york_timezone = timezone("US/Eastern")
        the_time = datetime.now(new_york_timezone)
        current_date = the_time.strftime('%b %d, %Y')

        if current_date == last_day_open:
            return True
        return False
    except: # If we don't know if the stock market was open, we assume it was closed
        print("Could not determine whether stock market was open today\n")
        return False










"""
SETUP
"""

# Gather a list of S&P500 companies
numbers = pd.read_html("https://en.m.wikipedia.org/wiki/List_of_S%26P_500_companies#S&P_500_component_stocks")

sector_numbers = {}
company_tickers = []
company_sectors = {}
for n in range(len(numbers[0].index)):
    company_tickers.append(numbers[0]["Symbol"][n])
    if numbers[0]["GICS Sector"][n] not in sector_numbers.keys():
        sector_numbers[numbers[0]["GICS Sector"][n]] = len(sector_numbers)
    company_sectors[numbers[0]["Symbol"][n]] = numbers[0]["GICS Sector"][n]

# This one is wrong on Wikipeda
company_tickers[company_tickers.index("BF.B")] = "BF-B"
company_sectors["BF-B"] = company_sectors.pop("BF.B")

company_tickers[company_tickers.index("BRK.B")] = "BRK-B"
company_sectors["BRK-B"] = company_sectors.pop("BRK.B")


# Make bag of words
positive_words_list = []
negative_words_list = []
#bag_of_words = []
with open("Data/positive_words_en.txt", "r") as file:
    for line in file:
        positive_words_list.append(line[:-1])

with open("Data/negative_words_en.txt", "r") as file:
    for line in file:
        negative_words_list.append(line[:-1])










"""
MAIN LOOP
"""

while True:

    # Wait for stock market to open
    wait_for_stock_market_open()

    # Collect news sentiment data
    print("Reading today's headlines...\n")
    daily_sentiment = get_news_sentiments()

    # Get financial data
    features = np.zeros([len(company_tickers), len(financial_features_names) + len(sector_numbers) + len(daily_sentiment)])
    failed_readings = []
    print("Gathering financial data...\n")
    for ticker in company_tickers:
        successful_reading = False
        for n in range(connection_attempts):
            try:
                # Collect financial data
                company_financial_data = get_financial_data(ticker)
                company_financial_data = company_financial_data[np.logical_not(np.isnan(company_financial_data))]

                # Append the word features to the financial features
                feature_line = np.append(company_financial_data, daily_sentiment) # A single data sample

                # The features collected for this day
                # Has the shape "number of companies" x "number of features"
                features[company_tickers.index(ticker), :] = feature_line
                successful_reading = True
                break
            except:
                time.sleep(1)

        if not successful_reading:
            print("Could not gather financial data on", ticker, "\n")
            failed_readings.append(ticker)


    print(feature_line)
    print(features)

    # Wait for stock market to close
    wait_for_stock_market_close()



    # Only saves the data if the stock market was actually open
    if stock_market_was_open_today():
        # Check how the stocks went
        print("Checking how the stock market went today...\n")
        y = np.zeros([1, len(company_tickers)])

        for ticker in company_tickers:
            successful_reading = False
            for n in range(connection_attempts):
                try:
                    y[0, company_tickers.index(ticker)] = get_daily_result(ticker)
                    successful_reading = True
                    break
                except:
                    time.sleep(1)

            if not successful_reading:
                print("Could not gather daily result on", ticker, "\n")
                failed_readings.append(ticker)


        # Add the labels
        features = np.hstack((features, y.T))

        # Remove bad data
        for n in range(len(failed_readings)):
            failed_readings[n] = company_tickers.index(failed_readings[n])
        features = np.delete(features, (failed_readings), axis=0)

        # Save data
        print("Saving data...\n")
        try:
            data = np.loadtxt("Data/main_data_file.txt")
            data = np.vstack((data, features))
            np.savetxt("Data/main_data_file.txt", data)
        except:
            np.savetxt("Data/main_data_file.txt", features)

        contents = np.loadtxt("Data/main_data_file.txt")

        print("We now have", np.shape(contents)[0], "data samples\n")

    else:
        print("Stock market was not open today\nNo data recorded\n")
