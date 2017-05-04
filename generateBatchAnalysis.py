## Cronjob
import RupertCore as rc
import batch_analysis as ba
import pickle
import pandas as pd

def generateBatchAnalysis():
    """
    Run batch analysis and generate a pickle to store the result
    """
    stocks = rc.batch_stock('Stocklists/OMX-ST-30.txt')
    #stocks = ['NOKI.ST', 'TOBII.ST']

    # Find the number of sections which gives best result
    # The interval may be changed depending on how much data is available
    df = ba.batch_variate_section_analysis(stocks, sect_int = (4,13))
    df.set_index(['STOCK'], inplace=True)

    # Define learning array
    learning_df = {'STOCK':[], 'SECTION':[], 'EPSILON':[]}

    # Find epsilon for each stock using optimized section
    for stock in stocks:
        try:
            section = int(df.loc[stock]['SECTION'])

            pob_df = ba.performance_of_batch([stock], section)
            list_df = pob_df.values.tolist()[0]

            learning_df['STOCK'].append(stock)
            learning_df['SECTION'].append(section)
            if list_df[5] != 0:
                learning_df['EPSILON'].append(list_df[2] / list_df[5] - list_df[3])
            else:
                learning_df['EPSILON'].append(9999999999999)
                rc.log_event(stock + ' zero standard deviation')

        # Ignore stock if in stocklist but cannot be calculated due to some issues.
        # TODO: Dont do this...
        except KeyError:
            pass


    print("Raw array \n", learning_df)

    df = pd.DataFrame(learning_df)

    print("Pre dump \n", df)
    pickle.dump(df, open('pickle/learning/current_set.p', 'wb'))

    print("Loading from pickle...")
    loaded_df = pickle.load(open('pickle/learning/current_set.p', 'rb'))

    print("Loaded df \n", loaded_df)
