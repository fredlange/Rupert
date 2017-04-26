import matplotlib.pyplot as plt
import random
from math import sqrt
import pandas as pd
import numpy as np
from yahoo_data_handler import *
import time
import sys
from os import listdir
import math
import pickle
import RupertStat as rstat

class data_vectors():
    def __init__(self, x1, x2, y1, y2, ds,xID):
        self._x1 = x1   # datetime64
        self._x2 = x2   # datetime64
        self._y1 = float(y1)
        self._y2 = float(y2)
        self._ds = int(ds) # Save the dataset where the vector was found.
        self._lambda = (self._y2 - self._y1) / self._y1
        self._xID = int(xID)

    def slope(self):
        return (self._y2 - self._y1) / (self._x2 - self._x1)

    def length(self):
        return sqrt((self._y2 - self._y1) ** 2 + (self._x2 - self._x1) ** 2)

    def x_len(self):
        return abs(self._x2 - self._x1)

    def y_len(self):
        return abs(self._y2 - self._y1)

    def lambda_coefficient(self):
        return (self._y2 - self._y1) / self._y1

def log_event(msg):
    """
    Creates a logfile in root directory
    """
    current_time = time.localtime()
    date = time.strftime("%Y%m%d", current_time)
    timestamp = str(date) + ' ' + time.strftime("%H:%M:%S", current_time)
    with open('log/'+date+'_log.csv','a') as logfile:
        logfile.write(timestamp + "," + msg + "\n")
    print("ERROR:", msg)
    print("Logfile created in log directory")

def batch_stock(filename):
    """
    Creates a list of stocks from a stocklist-file.
    """
    try:
        with open(filename, "r") as file:
            return [line.rstrip() for line in file]
    except Exception as msg:
        print(msg)

def vectorAppend(values, period, dataSet, plot=False):
    """
    Create vector patterns for each dataset
    """
    try:
        vectors = []
        x_axis = period
        dataSet = int(dataSet)

        for i in range(len(x_axis)):
            for j in range(len(x_axis)):
                if j>i:
                    vectors.append([x_axis[i],   # X1
                                    x_axis[j],   # X2
                                    values[i],   # Y1
                                    values[j],   # Y2
                                    dataSet,     # Dataset
                                    i])          # xID

        return vectors

    except Exception as msg:
        print(msg)
        return None

def data_sectionalized(stock, sections=10, from_day=False):
    try:
        if from_day == False:
            data = getStockData(stock, lookBack = sections, legacy=True)
        elif from_day >= sections:
            data = getStockData(stock, fullData = True, legacy=True)[from_day-sections:from_day]
        elif (from_day == True and from_day <= sections):
            raise Exception("From day must be shifted at least 10 days")

        vector_sets,vector_dict = [], {}

        for i in range(sections):
            close, time = data[i].CLOSE, data[i].TIME
            vector_sets.extend(vectorAppend(close.tolist(),time.tolist(), i, plot=False))
            vector_dict[i] = vectorAppend(close.tolist(),time.tolist(), i, plot=False)

        return vector_sets, vector_dict

    except Exception as msg:
        print("DATA_SECTIONALIZE: " + str(msg))


def select_latest_file(dir):
    """
    Return file path of latest created file in 'dir' directory.
    """
    files = os.listdir(dir)
    path = lambda file: dir + '/' + file
    file_tuple = [(os.path.getmtime(path(file)), path(file)) for file in files]
    latest = sorted(file_tuple, key=lambda modified: modified[0])[-1][-1]

    return latest


def evaluate_stocklist():
    """
    Evaluates all stocks in a list of stocks using lambda coefficient statistical analysis
    and time density analysis. Requires path to some stocklist.
    Creates a evaluation file for later reporting.
    """
    print("RUPERT ON THE JOB...")
    batch = batch_stock("Stocklists/OMX-ST-30.txt") # Create list of stocks

    date = time.strftime("%Y%m%d", time.localtime())
    file_path = "evaluations/RupertCore "+date+".csv"

    with open(file_path, "a") as export_file:
        export_file.write('STOCK,MEAN,R-RATIO,TIME,TIME_STD\n')
        for stock in batch:
            try:
                mean_rupert_slope, rup_num = rstat.lambda_stat(stock, 10)
                mean_time, std_time = rstat.mean_method(stock, 10)
                print("Writing to file...")
                export_file.write(str(stock)
                                  + "," + str(mean_rupert_slope)
                                  + "," + str(rup_num)
                                  + "," + str(mean_time)
                                  + "," + str(std_time)
                                  + "\n")
                print("Segment done, move onto next stock.")

            except Exception as msg:
                print("EVALUATE_STOCKLIST:", msg)
                log_event("Unable to fetch " + stock)
                pass

        print("All segments done.")

def reporting():
    print("Preparing report")
    date = time.strftime("%Y%m%d", time.localtime())
    from_path = 'evaluations/RupertCore '+date+'.csv'
    to_path = 'reports/StockReport '+date+'.csv'

    df = pd.read_csv(from_path)
    df['EVAL'] = df['R-RATIO']/(1 + df['TIME_STD'])

    df.sort_values(['EVAL'], inplace=True)
    df.to_csv(to_path, header=True)

    print(df)
    print("Report saved at:", to_path)


def unixTimeToDate(UNIXTIME):
    """
    Inputs an UNIX timestamp
    Returns int date
    Ex: unixTimeToDate(1478594163)
    Return 20161108
    """
    dt = datetime.datetime.fromtimestamp(UNIXTIME)
    return dt.strftime('%Y%m%d')
