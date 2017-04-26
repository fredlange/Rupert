import RupertCore as rc
import RupertStat as rstat
import pandas as pd
import experimental_mandate_method as Exp_mm
import pickle
import time

def runReport(stocklist):
    stocks = rc.batch_stock(stocklist)
    init_d1 = pd.read_csv('csv/batch_variate_section_analysis_20170120.csv', index_col='STOCK')
    init_d1.drop(['Unnamed: 0'], axis=1, inplace=True)
    init_d2 = pickle.load(open('pickle/performance_of_batch/20170112.p', 'rb'))
    init_data = pd.concat([init_d1, init_d2], join='inner', axis=1)
    init_data['EPSILON'] = init_data['AVG R#'] / init_data['MAN ACCURACY'] - init_data['AVG STDDEV']


    array = {'STOCK': [],'R#':[], 'Rmean':[] , 'MAN PRED':[], 'SIGMA':[], 'EPSILON':[], 'AVG ACC':[]}

    for stock in stocks:

        try:
            df = init_data.loc[stock]
            sec = int(df['SECTION'])
            Rm, Rn = rstat.lambda_stat(stock, sec)
            mean_pred, sigma = rstat.mean_method(stock, sec)
            pred = Exp_mm.mandate_method(stock, sec)[0]

            array['STOCK'].append(stock)
            array['R#'].append(Rn)
            array['Rmean'].append(Rm)
            array['MAN PRED'].append(pred)
            array['SIGMA'].append(sigma)
            array['EPSILON'].append(df['EPSILON'])
            array['AVG ACC'].append(df['MAN ACCURACY'])

        except Exception as msg:
            print('ERROR:', stock, msg)

    result = pd.DataFrame(array)
    result.set_index('STOCK', inplace=True)
    result['ACC'] = result['R#'] / (result['EPSILON'] + result['SIGMA'])
    result.sort_values('ACC', inplace=True)

    date = time.strftime("%Y%m%d", time.localtime())
    result.to_csv('reports/RupertReport'+date+'.csv')

    print(result)
