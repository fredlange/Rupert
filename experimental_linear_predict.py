import quandl, math, datetime
import numpy as np
from sklearn import preprocessing, cross_validation, svm
from sklearn.linear_model import LinearRegression
from yahoo_data_handler import *
import matplotlib.pyplot as plt


def predictStockValue(stock, algoritm='LinearRegression', dataSpan=0.1):

    df = getDataFrame('ABB.ST', '20161104')

    print("STOCK INFORMATION:", stock)
    print(df.tail(), "\n\n")

    forecast_col = 'CLOSE'

    df.fillna(-99999, inplace = True)

    # Number of days to forecast
    forecast_span = int(math.ceil(dataSpan*len(df)))

    # Shift close price a certain days into future.
    df['label'] = df[forecast_col].shift(forecast_span)

    X = np.array(df.drop(['label'],1))
    X = preprocessing.scale(X)

    X_lately = X[-forecast_span:]
    X = X[:-forecast_span]

    df.dropna(inplace = True)
    y = np.array(df['label'])

    X_train, X_test, y_train, y_test = cross_validation.train_test_split(X, y, test_size=0.2)

    # Select algoritm
    if algoritm == 'LinearRegression':
        clf = LinearRegression()
    elif algoritm == 'svm':
        clf = svm.SVR()
    else:
        raise ValueError("Unknown algoritm")

    clf.fit(X_train, y_train)

    accuracy = clf.score(X_test, y_test)
    print("Accuracy:", accuracy)

    forecast_set = clf.predict(X_lately)

    last_date = df.iloc[-1].name
    last_unix = last_date.timestamp()
    one_tick = 300
    next_unix = last_unix + one_tick

    for i in forecast_set:
        next_date = datetime.datetime.fromtimestamp(next_unix)
        next_unix += one_day
        df.loc[next_date] = [np.nan for _ in range(len(df.columns)-1)]+[i]

    print("FORECAST:", forecast_span, "days")
    print("Algoritm:", algoritm)
    print(df.tail(forecast_span), "\n\n")

    df['CLOSE'].plot()
    df['label'].plot()
    plt.show()

    forecast_values = list(df[-forecast_span:])
    return forecast_values
