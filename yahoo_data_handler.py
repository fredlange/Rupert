"""
This file only handles data gathers from yahoo finance.
This file is not suppose to work with any other kind of data.
WARNING: ONLY FOR DEMONSTRATION PURPOSE DO NOT USE YAHOO AS A DATA SOURCE
"""
import urllib.request
import time
import os
import pandas as pd
import numpy as np
import datetime
import pytz
import sqlite3
import RupertMail

def download_data(stock):
    """
    Download 10 day data for 'stock'
    """
    date = time.strftime("%Y%m%d", time.localtime())
    file_path = 'yahoo_data/'+stock+'/'+date+'.csv'
    try:
        if not os.path.isfile(file_path):   # If data does not exist, pull it
            print("Data does not exists, pulling data for:", stock)
            urlToVisit = 'http://chartapi.finance.yahoo.com/instrument/1.0/'+stock+'/chartdata;type=quote;range=10d/csv'
            pull_data = pd.read_csv(urlToVisit, header=27, index_col=0)
            try: os.mkdir('yahoo_data/' + str(stock))
            except FileExistsError: pass
            pull_data.to_csv(file_path, header=True)
            print('Sleeping to avoid DDoS')
            time.sleep(0.5)

    except pd.io.common.CParserError:
        print('ERROR: Stock does not exists in yahoo database')

    except OSError as msg:
        print(msg)

def collect_batch_data(stocklist):
    import RupertCore as rc
    print("Collecting stock data in batch")
    batch = rc.batch_stock('Stocklists/'+stocklist)
    for i in batch:
        download_data(i)
    print("Batch collecting...DONE")


def getDataFrame_prototype(stock, start_date=False, look_back=10, full_data = False, complete_data=False):
    """ PROTOTYPE
    Get list of pandas dataframes containing 'look_back' number of days from (TBA) 'start_date' date.

    parameters:
    stock: select a stock (required)
    start_date: str(YYMMDD) with starting date (default: False, assumes todays date)
    look_back: select int number of days backwards to include in separate data frames
    full_data: default False. Return list of day-separeted pandas data frames
    complete_data: default False. Return original data rather than selected data.
    """
    data_folder = 'yahoo_data/'
    current_date = time.strftime("%Y%m%d", time.localtime())
    file_path = data_folder+stock+'/'+current_date+'.csv'

    # If data does not exist, pull it
    try:
        if not os.path.isfile(file_path):
            print("Data does not exists, pulling data for:", stock)
            urlToVisit = 'http://chartapi.finance.yahoo.com/instrument/1.0/'+stock+'/chartdata;type=quote;range=10d/csv'
            pull_data = pd.read_csv(urlToVisit, header=27, index_col=0)
            try: os.mkdir('yahoo_data/' + str(stock))
            except FileExistsError: pass
            pull_data.to_csv(file_path, header=True)
            print('Sleeping to avoid DDoS')
            time.sleep(0.5)

        # Create a list of all data sets and store them in separate pandas data frames.
        data_sets = os.listdir(data_folder+stock)
        data_frames_array = [pd.read_csv(data_folder+stock+'/'+dset,
                                         names=['TIME_ID', 'CLOSE','HIGH','LOW','OPEN','VOLUME'],
                                         index_col = 'TIME_ID'
                                         ) for dset in data_sets]

        # Create empty data frame and then append all previous data sets into it
        cdf = pd.DataFrame()
        for i in data_frames_array:
            cdf = cdf.combine_first(i)

        # Split unix time into DATE and CLOCK columns
        cdf['TIMEconv'] = cdf.index
        cdf['DATETIME'] = pd.to_datetime(cdf['TIMEconv'], unit='s', utc=True)
        bridge_var = pd.DatetimeIndex(cdf['DATETIME'])
        cdf['DATE'] = bridge_var.date
        cdf['TIME'] = bridge_var.time

        # Clean up data frame from unused labels
        if not complete_data:
            del cdf['DATETIME'], cdf['TIMEconv'], cdf['OPEN'], cdf['VOLUME'], cdf['LOW'], cdf['HIGH']

        # Split data frame into smaller date specific frames
        dates = pd.Series.unique(cdf['DATE'])
        data_frames_final = [cdf.loc[cdf['DATE'] == date] for date in dates]
        if start_date == False and full_data == False:
            return data_frames_final[-look_back:]   # look_back is number of days to return (default 10)

        elif start_date == True:
            print("ERROR: Specifing DATE functionality is not ready.")
            print("Use default settings")

        elif full_data == True:
            return data_frames_final

    # If the stock is not found in yahoo
    except pd.io.common.CParserError:
        print('ERROR: Stock does not exists in yahoo database')

    except OSError as msg:
        print("OSError:", msg)


## DATABASE DEPENDENT FUNCTIONS

def getStocklist():
    """
    Return list of stocks from database.
    Note: Should probably go in RupertCore.py
    """
    conn = sqlite3.connect("data/StockData.db")
    c = conn.cursor()
    c.execute("SELECT StockTicker FROM stocklist")
    listOfStocks = c.fetchall() # Contains a list of tuples
    stockList = [ticker[0] for ticker in listOfStocks]  # Extract from tuple
    conn.close()
    return stockList

def collectStreamData(stock):
    """
    Connect to yahoo api and return pandas df of stock information.
    """
    try:
        urlToVisit = 'http://chartapi.finance.yahoo.com/instrument/1.0/%s/chartdata;type=quote;range=1d/csv' % (stock)
        return pd.read_csv(urlToVisit, header=16, names=['time','close', 'high', 'low', 'open', 'volume'])
    except pd.io.common.CParserError:
        print("Stock ticker cannot be found:", stock)


def addDataToDatabase():
    """
    Download all data more recent than the data present in the database.
    """
    stockList = getStocklist()
    main_startTime = time.time()
    issues = ['ISSUES']

    try:
        conn = sqlite3.connect("data/StockData.db")
        c = conn.cursor()
        count = 0 ; noUpdateRequiredCount = 0
        for stock in stockList:
            dataList = []
            try:
                remoteDataStream = collectStreamData(stock)
                remoteDataStream['stock'] = stock
                remoteDataStream['id'] = None
                subset = remoteDataStream[['id', 'stock','time', 'close', 'high',
                                            'low', 'open', 'volume']]
                dataList = [tuple(x) for x in subset.values]

            except TypeError:   # raised if no data is available
                pass


            # Find latest tick data in database
            c.execute("SELECT time FROM yahooData WHERE stock=? ORDER BY time DESC LIMIT 1", (stock,))

            # Slight hack because some queryes come back as None raising TypeError
            # This may occour if the stock is unprecent in the database
            # either cause its a new stock or the stock ticker has been changed
            try: lastEntry = c.fetchone()[0]
            except TypeError: lastEntry = 0

            # Find latest tick data in the new set of data
            if dataList:
                currentLatestEntry = float(dataList[-1][2])
            else:
                currentLatestEntry = 0
                msg = "No online data was found for " + str(stock)
                issues.append(msg)
                print(msg)

            # Check if the latest information is more recent than the stored data.
            # If so, insert data into database
            if currentLatestEntry > lastEntry:
                print("Downloading %s rows of data for %s" % (len(dataList), stock))
                c.executemany('INSERT INTO yahooData VALUES (?,?,?,?,?,?,?,?)', dataList)
                count += 1  # Keep track on how many stocks updated

            elif currentLatestEntry == lastEntry:
                print("No update required for %s" % stock)
                noUpdateRequiredCount += 1

            conn.commit()
            print(stock, "step complete\n ---")

        conn.close()

    except urllib.error.HTTPError as msg:
        issues.append(msg)

    totalTime = str(round(time.time() - main_startTime, 1))
    msg = """
    RUPERT
    Downloading complete. Connection to db is closed.

    Total time elapsed: %s seconds
    Total number of updated stocks: %s / %s
    Total number of stocks already up-to-date: %s
    """ % (totalTime, str(count), str(len(stockList)), str(noUpdateRequiredCount))
    print(msg)
    issues_str = "\n".join(issues)
    print(issues_str)
    RupertMail.sendEmailToAdmin("Download complete", msg + issues_str)


def getStockData(stock, fromDate=False, fullData=False, lookBack=10, legacy=False, unsplit=False):
    """
    Return list of pandas dataframe with 'lookBack' number of dataframes (one for each day)
    NOTICE: This functions reads from database. Not CSV
    fromDate: Default False <=> Using latest data
    fullData: Default False = Use all avalable data
    lookBack: Select number of days to return data fromDate
    legacy: modify function to work with older functions
    unsplit: Return a single dataframe rather than one dataframe for each day
    """
    #import RupertCore as rc
    conn = sqlite3.connect('data/StockData.db')
    query = "SELECT * FROM yahooData WHERE stock='%s'" % (stock,)
    df = pd.read_sql(query, conn)
    conn.close()

    # Convert UNIXTIME into readable date, save in 'date', 'time' cols
    df['datetime'] = pd.to_datetime(df['time'], unit='s', utc=True)
    df['date'] = pd.DatetimeIndex(df['datetime']).date
    df['clock'] = pd.DatetimeIndex(df['datetime']).time
    del df['datetime']

    # Create list of date where data exists
    dates = df['date'].unique().tolist()

    # Remove unwanted data unless full data is requested
    if fullData == False:
        dates = dates[-lookBack:]
        df.drop(df[df.date < dates[0]].index, inplace=True)

    # Remove unwanted columns
    del df['ID']; del df['stock']; del df['open']; del df['high'];
    del df['low']; del df['volume'];

    # Split dataframe into one dataframe per day. Store in list.
    final_df_array = [df.loc[df.date==date] for date in dates]

    if legacy:
        for df in final_df_array:
            df.columns = ['TIME_ID', 'CLOSE','DATE', 'TIME']
            df.set_index(['TIME_ID'], inplace=True)

    return final_df_array


if __name__ == "__main__":
    pass
