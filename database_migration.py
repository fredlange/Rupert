"""
This file contains functions to migrate all stock data from CSV data storage to SQLite
Run this file as it is and make sure to direct to the correct folders
"""

import sqlite3
import pandas as pd
import os
import yahoo_data_handler as ydh


# Structure: FOLDER/stockname/date.csv
FOLDER = "yahoo_data"


conn = sqlite3.connect('data/StockData.db')
c = conn.cursor()
count = 0
issues = []
try:
    for stock in os.listdir(FOLDER):
        print("-- \n Migrating", stock)

        # Get full data from CSV
        full_data = ydh.getDataFrame_prototype(stock, full_data=True, complete_data=True)
        if full_data == None:
            print("incomplete data in CSV storage. Skipping", stock)
            issues.append(stock)
            continue

        ccd = pd.concat(full_data)
        del ccd['DATETIME'], ccd['TIMEconv'], ccd['TIME'], ccd['DATE']
        ccd.reset_index(inplace=True)

        # Convert dataframe into a tuple
        ccd['STOCK'] = stock
        ccd['ID'] = None
        subset = ccd[['ID', 'STOCK','TIME_ID', 'CLOSE', 'HIGH',
                                     'LOW', 'OPEN', 'VOLUME']]
        tuples = [tuple(x) for x in subset.values]

        # Append tuples to SQL
        c.executemany('INSERT INTO yahooData VALUES (?,?,?,?,?,?,?,?)', tuples)
        conn.commit()

        # Verify the number of entries
        expectedNrEntries = len(ccd)
        appendedNrEntries = c.execute("SELECT * FROM yahooData WHERE stock=?", (stock,))
        appendedNrEntries = len(appendedNrEntries.fetchall())
        if expectedNrEntries != appendedNrEntries:
            c.execute('DELETE FROM yahooData WHERE stock=?', (stock,))
            conn.commit()
            errorMsg = "ERROR %s: Entries does NOT match. \n" % stock
            errorMsg += "Stock data has been removed"
            print(errorMsg)
            issues.append(stock)
        else:
            print("Migration of %s completed successfully" % stock)

    print("MIGRATION IS COMPLETED")
    issues_str = "\n".join(issues)
    print("ISSUES \n", issues_str)

# If there are other files that are not folders
# then simply ignore them, they are not valid data
except NotADirectoryError:
    pass

conn.close()
