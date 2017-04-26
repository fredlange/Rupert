# Find time density by voting for starting values...

from yahoo_data_handler import *
#from RupertCore import *
import RupertCore as rc
import pandas as pd
import matplotlib.pyplot as plt

def mandate_method(stock, section=10, from_day=False):
    """
    experimental function using a mandate method to determine best investent time.
    """
    print("*experimental* Finding time using mandate method distribution of", stock, "with", section, "sections")

    ## Gather data
    if from_day == False:
        data, data_dict = rc.data_sectionalized(stock, section)
        obj = [rc.data_vectors(i[0],i[1],i[2],i[3],i[4],i[5]) for i in data]
    else:
        data, data_dict = rc.data_sectionalized(stock, section, from_day)
        obj = [rc.data_vectors(i[0],i[1],i[2],i[3],i[4],i[5]) for i in data]

    start_density = []
    for i in data_dict.keys():
        # Only get the interesting xID's mark rest as outliers.
        xID = np.array([vect._xID if vect._lambda > 0.01 and vect._ds == i else 99999999999 for vect in obj])
        xID = xID[xID < 99999999999].tolist()   # Remove outliers
        start_density.append(xID)

    vote = {'x':[],'n':[]}

    for i in data_dict.keys():
        if len(start_density[i]) > 0: # Ignore empty sections
            for j in start_density[i]:
                if j not in vote['x']:
                    vote['x'].append(j)
                    vote['n'].append(start_density[i].count(j))

    df = pd.DataFrame(vote)

    # Find winner
    largest = int(df['n'].max())
    arr = df.loc[df['n'] == largest]

    # If multiple winners, make a mean
    selected_time = arr['x'].mean()
    time_std = arr['x'].std()

    # Convert to time, assuming 5 min per tick.
    converted_time = round((selected_time * 5)/60 + 9, 2)
    converted_std = round((time_std * 5) / 60 , 2)

    return converted_time, converted_std
