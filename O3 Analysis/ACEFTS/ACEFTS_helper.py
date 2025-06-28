import numpy as np
import pandas as pd
from matplotlib import rcParams
from matplotlib import pyplot as plt
import xarray as xr
rcParams["font.size"] = 15
########################################################################################
#open file

f = xr.open_dataset(r"C:\Users\salla\Onedrive(uoft acc)\OneDrive - University of Toronto\Desktop\School Information\NSERC\NSERC\ACEFTS\ACEFTS_L2_v5p3_O3.nc")

#get orbit num and sunrise/sunset num
orbits  = f.variables["orbit"][:].values.astype(int)
ss  = f.variables["sunset_sunrise"][:].values.astype(int)

#get orbit num and sunrise/sunset num for flags
flag_file = r"C:\Users\salla\Onedrive(uoft acc)\OneDrive - University of Toronto\Desktop\School Information\NSERC\NSERC\ACEFTS\ACEFTS_L2_v5p3_flags_Apr2025\ACEFTS_L2_v5p3_flags_O3.nc"
f_flags     = xr.open_dataset(flag_file)
flags       = f_flags["quality_flag"][:]
orbits_flags    = f_flags.variables["orbit"][:].values.astype(int)
ss_flags    = f_flags.variables["sunset_sunrise"][:].values.astype(int)

#get flags for only the unique orbit num and sunrise/sunset combinations
combined_flags = np.column_stack((orbits_flags, ss_flags))
unique_flags, returned_index, returned_counts = np.unique(combined_flags, axis=0, return_index = True, return_counts = True)
returned_index = returned_index[returned_counts == 1]
unique_flags = combined_flags[np.sort(returned_index)]

#dataframe of flags and indices
flag_matcher = pd.DataFrame({
    "matcher_col": [tuple(row) for row in unique_flags],
    "flag_idx": np.sort(returned_index)
})
flag_matcher.set_index("matcher_col", inplace = True)

#dataframe of data and indices
matcher = pd.DataFrame()
matcher["matcher_col"] = [tuple(row) for row in np.column_stack((orbits, ss))]
matcher.reset_index(inplace = True)
matcher.set_index("matcher_col", inplace = True)

matched = pd.merge(matcher, flag_matcher, how = "inner", left_index = True, right_index = True)
matched = matched.sort_values("index")
flags = flags[matched["flag_idx"], :].T
valid_indices = matched["index"].values

f = f.isel(index = valid_indices)

time = pd.to_datetime({"year": f.variables["year"], "month": f.variables["month"], "day": f.variables["day"], "hour": f.variables["hour"]})

f = (f.assign_coords(
    time=("index", time),
    latitude = ("index", f.variables["latitude"]),
    longitude = ("index", f.variables["longitude"])
    )     
    .swap_dims({"index": "time"})
    .sortby("time"))
########################################################################################
sorted_time = f.time

flags_sorted = (
    flags
    .assign_coords(time=("index", time))
    .swap_dims({"index": "time"})
    .sel(time=sorted_time)
)
########################################################################################
O3_vmr = f["O3"].T.where(flags_sorted == 0)


def get_vmr():
    return O3_vmr


def get_density():
    return O3_vmr * (get_pressure()/(8.3145 * get_temperature()))


def get_column(min_alt = f.altitude.min(), max_alt = f.altitude.max()):
    O3_density = get_density()
    return (O3_density * 1000).sel(altitude = slice(min_alt, max_alt)).sum(dim = "altitude") * 6.022e23


def get_column_DU(min_alt = f.altitude.min(), max_alt = f.altitude.max()):
    column = get_column(min_alt, max_alt)
    return column / 2.687e20


def get_temperature():
    return f["temperature"][:].T.where(flags_sorted == 0)


def get_pressure():
    return f["pressure"][:].T.where(flags_sorted == 0)


def get_time_filtered_vmr(o3, dt1 = "2006-01-01", dt2 = "2020-12-31"):
    return o3.sel(time = slice(dt1, dt2))


def get_zone_filtered_vmr(o3, lat1 = -90, lat2 = 90, long1 = -200, long2 = 200):
    return o3.where(((o3.latitude >= lat1) & (o3.latitude <= lat2) & (o3.longitude >= long1) & (o3.longitude <= long2)), drop = True)


def get_lat(o3):
    return o3["latitude"]


def get_long(o3):
    return o3["longitude"]



