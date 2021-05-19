import time
import numpy as np
import pandas as pd
from pandas_datareader import data as pdr
import yfinance as yf
yf.pdr_override()
import simfin as sf
from simfin.names import *
import pickle





# Gather a list of S&P500 companies
sector_numbers = {} # Sector-number for one-hot encoding 'Information Technology': 2,
company_tickers = [] # List of company tickers 'MSFT'
company_sectors = {} # Contains which sector each company belongs to 'MSFT': 'Information Technology',

numbers = pd.read_html("https://en.m.wikipedia.org/wiki/List_of_S%26P_500_companies#S&P_500_component_stocks")
for n in range(len(numbers[0].index)):
    company_tickers.append(numbers[0]["Symbol"][n])
    if numbers[0]["GICS Sector"][n] not in sector_numbers.keys():
        sector_numbers[numbers[0]["GICS Sector"][n]] = len(sector_numbers)
    company_sectors[numbers[0]["Symbol"][n]] = numbers[0]["GICS Sector"][n]

# These ones are wrong on Wikipeda
company_tickers[company_tickers.index("BF.B")] = "BF-B"
company_sectors["BF-B"] = company_sectors.pop("BF.B")

company_tickers[company_tickers.index("BRK.B")] = "BRK-B"
company_sectors["BRK-B"] = company_sectors.pop("BRK.B")







# Get fundamental data on companies
sf.set_api_key('free')
sf.set_data_dir('~/simfin_data/')

successful_companies = [] # List of tickers that have the data we need
financial_data = sf.load(dataset='income', variant='annual', market='us', index=['Ticker'])

for ticker in company_tickers:
    try:
        df = financial_data.loc[ticker][-10:][['Revenue', 'Net Income', 'Gross Profit', 'Operating Expenses', 'Fiscal Year']]
        if df['Fiscal Year'][0] == 2010:
            successful_companies.append(ticker)
    except:
        continue

#print("sf", len(successful_companies)) # 376






# Get historical data for all companies
new_successful_companies = []
for ticker in successful_companies:
    try:
        stock_info = pdr.get_data_yahoo(ticker, start="2010-01-04", end="2020-01-01") #yf.Ticker(ticker)
        new_successful_companies.append(ticker)
    except:
        continue

successful_companies = new_successful_companies.copy()
#print("yf", len(successful_companies)) # 376


# A test run to double check it valid data for the companies exist
x = np.zeros((len(successful_companies), 2516, 6))
#y = np.zeros((len(successful_companies), 2516))

new_successful_companies = []
for n in range(len(successful_companies)):
    stock_info = pdr.get_data_yahoo(successful_companies[n], start="2010-01-04", end="2020-01-01") #yf.Ticker(ticker)
    stock_info = stock_info.to_numpy()
    if np.shape(stock_info)[0] == 2516:
        if np.shape(stock_info)[1] == 6:
            new_successful_companies.append(successful_companies[n])

successful_companies = new_successful_companies.copy()




x = np.zeros((len(successful_companies), 2516, 6))
#y = np.zeros((len(successful_companies), 2516))
#print(np.shape(x)) # 345, 2516, 6

for n in range(len(successful_companies)):
    stock_info = pdr.get_data_yahoo(successful_companies[n], start="2010-01-04", end="2020-01-01") #yf.Ticker(ticker)
    stock_info = stock_info.to_numpy()
    x[n, :, :] = stock_info

#print(np.shape(x)) # 345, 2516, 6

pickle.dump(x, open("Data/Datasets/all_companies_historical_data.pkl", "wb"))
pickle.dump(successful_companies, open("Data/Datasets/list_of_companies.pkl", "wb"))








# Get financial data
list_of_companies = successful_companies.copy()
all_companies_financial_data = np.zeros((len(list_of_companies), 2516, 4))

sf.set_api_key('free')
sf.set_data_dir('~/simfin_data/')
financial_data = sf.load(dataset='income', variant='annual', market='us', index=['Ticker'])
for n in range(len(list_of_companies)):
    company_financial_data = financial_data.loc[list_of_companies[n]][-10:][['Revenue', 'Net Income', 'Gross Profit', 'Operating Expenses', 'Fiscal Year']]
    company_financial_data = company_financial_data.to_numpy()
    company_financial_data = company_financial_data[:, :4]

    stock_info = pdr.get_data_yahoo(list_of_companies[n], start="2010-01-04", end="2020-01-01")

    days_counted = 0
    for year in range(2010, 2020):
        yearly_historical_data = stock_info.loc[str(year) + '0101':str(year) + '1231']
        yearly_historical_data = yearly_historical_data.to_numpy()

        all_companies_financial_data[n, days_counted:days_counted+np.shape(yearly_historical_data)[0], :] = company_financial_data[year-2010, :]
        days_counted += np.shape(yearly_historical_data)[0]

pickle.dump(all_companies_financial_data, open("Data/Datasets/all_companies_financial_data.pkl", "wb"))





# Import VIX historical data
vix_data = pd.read_csv('Data/^VIX.csv')
vix_data = vix_data.to_numpy()
vix_data = vix_data[:, 1:-1]
np.savetxt('Data/Datasets/vix_data.csv', vix_data)


# Import S&P500 historical data
SP500_data = pd.read_csv(r'Data/SP 500 GSPC.csv')
SP500_data = SP500_data.to_numpy()
SP500_data = SP500_data[20593:23109, 1:]
np.savetxt('Data/Datasets/SP500_data.csv', SP500_data)




















# Collect index data
vix_data = pd.read_csv('Data/Datasets/vix_data.csv')
SP500_data = pd.read_csv('Data/Datasets/SP500_data.csv')

# Load company historical data
all_companies_historical_data = pickle.load(open("Data/Datasets/all_companies_historical_data.pkl", "rb"))
all_companies_financial_data = pickle.load(open("Data/Datasets/all_companies_financial_data.pkl", "rb"))
list_of_companies = pickle.load(open("Data/Datasets/list_of_companies.pkl", "rb"))




# Placeholder
