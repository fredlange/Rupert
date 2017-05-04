import RupertCore as rc
import numpy as np

def lambda_stat(stock, section, from_day=False):
    """
    Initial analysis to find the existance of interesting vectors in dataset.
    """
    print("\nFinding lambda statistic of", stock, "with", section, "sections")

    if from_day == False:
        data, data_dict = rc.data_sectionalized(stock, section)
    else:
        data, data_dict = rc.data_sectionalized(stock, section, from_day)
    obj = [rc.data_vectors(i[0],i[1],i[2],i[3],i[4],i[5]) for i in data]

    print("Calculating statistics...")
    final_result = []
    for i in data_dict.keys():
        slopes = np.array([vect._lambda if vect._ds == i else 0 for vect in obj])

        tot_slopes = slopes.size
        pos_slopes = (slopes > 0).sum()
        neg_slopes = (slopes < 0).sum()
        rup_slopes = (slopes > 0.01).sum()

        rup_stat = round(rup_slopes / tot_slopes * 1000, 2)
        pos_stat = round(pos_slopes / tot_slopes * 10, 2)
        neg_stat = round(neg_slopes / tot_slopes * 10, 2)

        if rup_stat > 0:
            final_result.append(rup_stat)

    # Calculate mean slope of rupert vectors
    mean_rupert_slope = sum(final_result) / section

    # Calculate rupert-number as the average probability of
    # existance of a rupert vector on some day
    R = len(final_result) / section

    return mean_rupert_slope, R


def mean_method(stock, section, from_day=False):
    """
    Statistical analysis to find the mean of vector starting points
    """
    print("Finding time density distribution of", stock, "with", section, "sections")

    if from_day == False:
        data, data_dict = rc.data_sectionalized(stock, section)
    else:
        data, data_dict = rc.data_sectionalized(stock, section, from_day)
    obj = [rc.data_vectors(i[0],i[1],i[2],i[3],i[4],i[5]) for i in data]

    start_density = []
    for i in data_dict.keys():
        # Only get the interesting xID's mark rest as outlier.
        xID = np.array([vect._xID if vect._lambda > 0.01 and vect._ds == i else 99999999999 for vect in obj])
        xID = xID[xID < 99999999999].tolist()   # Remove outrunners
        start_density.append(xID)

    ## Find time distribution
    mean,stddev = [],[]
    for i in data_dict.keys():
        if len(start_density[i]) > 0:   # Ignore empty sections
            start_density_np = np.array(start_density[i])
            mean.append(np.mean(start_density_np))
            stddev.append(np.std(start_density_np))

    # Convert xIDs to approximate time.
    mean_time = round(9 + np.mean(np.array(mean)) * 5 / 60,1) # Assume 5 min on each tick
    std_time = round(np.mean(np.array(stddev)) * 5 / 60,1)

    print("Time density distribution...DONE")
    return mean_time, std_time
