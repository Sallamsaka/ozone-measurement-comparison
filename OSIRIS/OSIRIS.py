import numpy as np
from matplotlib import pyplot as plt
import xarray as xr

directory = r'C:\Users\salla\Onedrive(uoft acc)\OneDrive - University of Toronto\Desktop\School Information\NSERC\OSIRIS'

path = directory + r'\*.nc'

ds = xr.open_mfdataset(
    path,
    combine="nested",
    concat_dim="profile_id",
    parallel=True,
    decode_cf=True
)

#Promote `time` from a 1D coordinate to a real dimension
ds = ds.swap_dims({"profile_id": "time"})

# Sort dataset by time to enable fast slicing
ds = ds.sortby("time")

def O3_num_density(start_time = "", end_time):
    return ds["ozone_concentration"]

def O3_vmr():
    return O3_num_density() * 8.3145 * ds["temperature"] / (ds["pressure"] * 100)

O3.sel(time=slice("2006-01-01", "2020-12-31")).mean(dim = "time").plot(y = "altitude")