# Rupert Analytics
Using machine learning to determine daily growth in stocks.
Rupert answers the question "If I want to make a 1% ROI today. What should I by and when?" it will also provide you with the accuracy of its prediction.

## Notice: This is an early prototype that is outdated. Any trades are on your own risk!

Default stocklist is OMX-ST-30 (30 greatest companies on Stockholm Stock Exchange)
Feel free to add whatever stock tickers you want.

## Notice: You need to setup your own datastorage.
Currently Rupert is using Yahoo chart api for demonstation only. This is not OK to use in any situation. Use on your own risk.
You need to make your on data handler to download and send data as a pandas dataframe to calculating classes.


## Run
Clone the entire repository.

Create two folders in root: "yahoo_data" and "reports"

Then execute RupertDaily.py using Python3. The script needs to run for atleast 20 days (it will download data daily) before running a report using RupertCron.py.

For demonstration purposes a default training data is supplied using maximum of 10 days data. This is not ideal and will not give the best result but will allow for the program to run.
If you add any other stock tickers than OMX-ST-30 you need to run batch_analysis.py to generate training data using atleast 50+ days of data.
Rupert will not download dependancies you will have to do that yourself using PIP or similar.


