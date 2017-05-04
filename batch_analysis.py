## BATCH ANALYSIS
from yahoo_data_handler import *
from RupertCore import *
import RupertStat as rstat
import datetime
import os
import pandas as pd
import pickle
import experimental_mandate_method as Exp_td


def batch_analysis(stocks, section=10):
    """
    Analyze a complete list of stocks 'stocks' using all available data.
    >>> batch_analysis(['TOBII.ST'])
    TODO: Logging function...
    """

    array = {
        'STOCK':[],
        'MEAN':[],
        'R#':[],
        'TIME':[],
        'STDDEV':[],
        'PRED':[],
        'VECT':[],
        'MAN_TIME':[],
        'MAN_STD':[],
        'MAN_PRED':[],
        }

    print("BATCH ANALYSIS USING: \n", stocks)

    for stock in stocks:
        try:
            # Find the number of data sets for a stock
            data_folder = 'yahoo_data/'
            n_data_sets = len(os.listdir(data_folder + stock))

            # Perform analysis on each section
            for i in range(n_data_sets):
                print("\nANALYSING SET",i)

                # Fetch algorithms
                mean, Rn = rstat.lambda_stat(stock, section, i + section)
                time_avg, stddev = rstat.mean_method(stock, section, i + section)
                mandate_time, mandate_std = Exp_td.mandate_method(stock, section, i + section)

                array['STOCK'].append(stock)

                # append lambda stat
                array['MEAN'].append(mean)
                array['R#'].append(Rn)

                # append mean method
                array['TIME'].append(time_avg)
                array['STDDEV'].append(stddev)

                # Append mandate method
                array['MAN_TIME'].append(mandate_time)
                array['MAN_STD'].append(mandate_std)

                # Make prediction (mean method)
                time_conv = (time_avg-9)*60/5
                std_dev_conv = stddev*60/5
                interval = (time_conv - 0.05, time_conv + 0.05) # Fixed interval

                # Make prediction (mandate method)
                man_time_conv = (mandate_time-9)*60/5
                man_std_dev_conv = mandate_std*60/5

                man_interval = (man_time_conv - 0.05, man_time_conv + 0.05) # Fixed interval

                ## Evaluate prediction
                data = getDataFrame_prototype(stock, full_data=True)[i + section + 1]
                vectors = vectorAppend(data['CLOSE'].values, data['TIME'].values, section +1)
                obj = [data_vectors(i[0],i[1],i[2],i[3],i[4],i[5]) for i in vectors]

                # Filter to only interesting vectors
                # TODO: Replace with numpy
                x_begin = [vect._xID if vect._lambda > 0.01 else None for vect in obj]
                try:
                    while True: x_begin.remove(None)
                except: pass

                # Evaluate mean method predictions
                count=0
                for i in x_begin:
                    if interval[0] < i <interval[1]:
                        count += 1
                array['PRED'].append(count)

                # Evaluate mandate method predictions
                man_count=0
                for i in x_begin:
                    if man_interval[0] < i <man_interval[1]:
                        man_count+= 1

                array['MAN_PRED'].append(man_count)

                # Count the total number of rupert vectors
                array['VECT'].append(len(x_begin))

        except Exception as msg:
            log_event("ERROR (batch_analysis): " + stock + ": " + str(msg))

    # Create DataFrame
    df = pd.DataFrame(array)

    df['PRED TRUE'] = np.where((df['PRED'] > 0) & (df['VECT'] > 0), 1, 0)
    df['OPPORTUNITY'] = np.where((df['PRED'] == 0) & (df['VECT'] > 0), 1, 0)
    df['MAN PRED TRUE'] = np.where((df['MAN_PRED'] > 0) & (df['VECT'] > 0), 1, 0)

    # Create pickle
    date = time.strftime("%Y%m%d", time.localtime())
    file_path = 'pickle/batch_analysis/'+date+'.p'
    pickle.dump(df, open(file_path, 'wb'))

    # If the analysis is small and can be redone easily, remove the pickle.
    # For larger analysis, we keep the pickle so we dont have to redo it.
    if len(stocks) == 1:
        os.remove(file_path)

    return df

def performance_of_batch(stocks, section=10, export_csv = False):
    """
    Analyse the performance of a algoritm on 'stock' using all available data.
    """

    # Load dataframe from pickle
    date = time.strftime("%Y%m%d", time.localtime())
    file_path = 'pickle/batch_analysis/'+date+'.p'
    if not os.path.isfile(file_path):
        df = batch_analysis(stocks, section)
    else:
        df = pickle.load( open( file_path, "rb" ) )

    # Analyse performance of each stock
    df.set_index('STOCK', inplace=True)

    pArr = {
        "STOCK":[],
        "ACCURACY":[],  # Mean method accuracy
        "OPTIMIZE POTENTIAL":[],
        "AVG R#":[],
        "AVG STDDEV":[],
        "AVG MEAN":[],
        "EPSILON":[],
        "MAN ACCURACY":[],  # Mandate method accuracy
    }

    for i in stocks:
        try:
            new_df = df.loc[i]
            n = new_df['PRED TRUE'].size

            # Number of times to be accurate
            pred_true =(new_df['PRED TRUE'] > 0).sum()          # Mean method
            man_pred_true = (new_df['MAN PRED TRUE'] > 0).sum() # Mandate method

            # Number of missed opportunities where vector existed
            opportunity =(new_df['OPPORTUNITY'] > 0).sum()

            # Historic accuracy of prediction
            accuracy = pred_true / n            # Mean method
            man_accuracy = man_pred_true / n    # Mandate method

            # Append information to array
            pArr['STOCK'].append(i)
            pArr['ACCURACY'].append(accuracy)
            pArr['MAN ACCURACY'].append(man_accuracy)
            pArr['OPTIMIZE POTENTIAL'].append(opportunity / n)
            pArr['AVG R#'].append(new_df['R#'].mean())
            pArr['AVG STDDEV'].append(new_df['STDDEV'].mean())
            pArr['AVG MEAN'].append(new_df['MEAN'].mean())

            # Solve epsilon from rupert accuracy conjecture
            epsilon = new_df['R#'].mean() / accuracy - new_df['STDDEV'].mean()
            pArr['EPSILON'].append(epsilon)


        # Ignore KeyError as hacky workaround.
        # TODO: Dont do this...
        except KeyError:
            pass

    # Create new dataframe
    performance_df = pd.DataFrame(pArr)
    performance_df.set_index('STOCK', inplace=True)

    # Create pickle
    export_path = 'pickle/performance_of_batch/'+date+'.p'
    pickle.dump(performance_df, open(export_path, 'wb'))

    # Export as csv if asked for
    if export_csv == True:
        performance_df.to_csv('csv/performance_batch_analysis_'+date+'.csv')

    return performance_df

def variate_section_analysis(stock, sect_int):
    """
    Analyse a stock using section interval (a,b) number of
    sections and find out how many section give the optimal result.
    """
    if sect_int[0] > 5 or sect_int[1] < sect_int[0]:
        raise Exception('Interval require 4 < a =< b')

    array = {'STOCK':[],'SECTION':[], 'MAN ACCURACY':[]}
    for section in range(sect_int[0], sect_int[1] + 1):

        print("ANALYSIS", stock, "USING", section, "SECTIONS")

        result = performance_of_batch([stock], section)

        if not result.empty:
            array['STOCK'].append(stock)
            array['SECTION'].append(section)
            array['MAN ACCURACY'].append(result['MAN ACCURACY'].values[0])

    print(len(array['STOCK']))
    print(len(array['SECTION']))
    print(len(array['MAN ACCURACY']))


    df = pd.DataFrame(array)

    return df

def batch_variate_section_analysis(stocks, sect_int = (4,13), export_csv=False):
    """
    Find the number of section that provides the greatest accuracy in batch.
    """
    array = {'STOCK':[],'SECTION':[], 'MAN ACCURACY':[]}
    try:
        for stock in stocks:
            result = variate_section_analysis(stock, sect_int)
            if not result.empty:
                array['STOCK'].append(stock)
                highest = result.loc[result['MAN ACCURACY'].idxmax()]
                highest = highest.tolist()
                array['SECTION'].append(highest[1])
                array['MAN ACCURACY'].append(highest[0])

        df = pd.DataFrame(array)

        # Create pickle
        date = time.strftime("%Y%m%d", time.localtime())
        export_path = 'pickle/batch_variate_section_analysis/'+date+'.p'
        pickle.dump(df, open(export_path, 'wb'))

        if export_csv == True:
            df.to_csv('csv/batch_variate_section_analysis_'+date+'.csv')

    # TODO: Dont do this...
    except KeyError:
        pass

    return df
