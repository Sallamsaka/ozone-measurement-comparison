import pandas as pd
import numpy as np
import numpy.ma as ma
from netCDF4 import Dataset
from matplotlib import pyplot as plt
f = Dataset("ACEFTS_L2_v5p3_O3.nc", "r")

O3 = f["O3"][:].T
altitude = f["altitude"][:]
latitude = f["latitude"][:]
month = f["month"][:]
cleaners = (O3 >= 10 ** (-4)) | (O3 == -888.) | (O3 == -999.)
O3 = ma.masked_where(cleaners, O3)
O3_median = ma.median(O3, axis = 1)
abs_diff = ma.abs(O3 - O3_median[:, None])
MAD = ma.median(abs_diff, axis = 1)
O3_mask =  (O3 <= (O3_median - 10*MAD)[:, None]) | (O3 >= (O3_median + 10*MAD)[:, None])
O3 = ma.masked_where(O3_mask, O3)

def idx_in_lat_range(lat1, lat2):    
    lat_condition = (latitude >= min(lat1,lat2)) & (latitude <= max(lat1,lat2))
    lat_idx_in_range = ma.where(lat_condition)[0]
    return lat_idx_in_range

def idx_in_months(*months):
    idx_in_months = []
    for m in months:
        idx_in_month = ma.where(month == m)[0]
        idx_in_months.append(idx_in_month)
    return idx_in_months

def idx_in_month_ranges(*month_ranges):
    idx_in_month_ranges = []
    for m1, m2 in month_ranges: 
        if m1 > m2: # say 11 and 5
            in_month_range = ((month >= m1) & (month <= 12)) | ((month >= 1) & (month <= m2))
            months_idx_in_range = ma.where(in_month_range)[0]
            idx_in_month_ranges.append(months_idx_in_range)
        elif m2 > m1:
            in_month_range = (month >= m1) & (month <= m2)
            months_idx_in_range = ma.where(in_month_range)[0]
            idx_in_month_ranges.append(months_idx_in_range)
    return idx_in_month_ranges

#plotting monthly O3
# x = altitude
# for i in range(len(idx_in_months(1,2))):
#     valid_idx = ma.intersect1d(idx_in_lat_range(0,90), idx_in_months(1,2)[i])
#     y = ma.mean(O3[:,valid_idx], axis = 1)
#     plt.plot(altitude, y, linewidth = 1, label = f"{idx_in_months(1,2)[i]} month")
    # plt.xlabel("Altitude")
    # plt.ylabel("O3 VMR")
    # plt.title("Mean O3")

# plotting monthly ranges
for i in range(len(idx_in_month_ranges((12,2) ,(3,5), (6,8)))):
    valid_idx = ma.intersect1d(idx_in_lat_range(0,90), idx_in_month_ranges((12,2) ,(3,5), (6,8))[i])
    y = ma.mean(O3[:,valid_idx], axis = 1)
    plt.plot(altitude, y, linewidth = 1, label = f"{[(12,2) ,(3,5), (6,8)][i]} months")
    plt.xlabel("Altitude")
    plt.ylabel("O3 VMR")
    plt.title("Mean O3")
    plt.legend()

plt.savefig("plot.png")
plt.show()

#plotting month range O3
# # get data from first line of the plot
# newx = ax.lines[0].get_ydata()
# newy = ax.lines[0].get_xdata()

# # set new x- and y- data for the line
# ax.lines[0].set_xdata(newx)
# ax.lines[0].set_ydata(newy)




f.close()