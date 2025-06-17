import xarray as xr
import numpy as np
import pandas as pd
import matplotlib as plt
# import netCDF4
from netCDF4 import Dataset
import os
import glob

directory = r'C:\Users\salla\Onedrive(uoft acc)\OneDrive - University of Toronto\Desktop\School Information\NSERC\PEARL FTIR O3\netcdf_out'

path = directory + r'\*.nc'

nc_list = glob.glob(path)

ds = xr.open_mfdataset(
    nc_list,
    combine="nested",
    concat_dim="idx",
    parallel=True,
    decode_cf=True
)

ds = ds.swap_dims({"idx": "DATETIME"})

ds = ds.sortby("DATETIME")