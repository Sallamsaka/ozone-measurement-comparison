import numpy as np
from matplotlib import rcParams
from matplotlib import pyplot as pl
import xarray as xr
from file_paths import PARENT_FOLDER
rcParams["font.size"] = 15

directory = PARENT_FOLDER + r'\OSIRIS'

path = directory + r'\*.nc'

f = xr.open_mfdataset(
    path,
    combine="nested",
    concat_dim="profile_id",
    # parallel=True,
    decode_cf=True
)

#Promote `time` from a 1D coordinate to a real dimension
f = f.swap_dims({"profile_id": "time"})

# Sort dataset by time to enable fast slicing
f = f.sortby("time")

# check the .where stuff
O3_density = f["ozone_concentration"].T


def get_vmr():
    return O3_density * 8.3145 * get_temperature() / (get_pressure() * 100)


def get_temperature():
    return f["temperature"].T


def get_pressure():
    return f["pressure"].T


def get_density():
    return O3_density


def get_column(min_alt=None, max_alt=None):

    da = (get_density() * 1000).sel(altitude=slice(min_alt, max_alt))
    
    valid_mask = ~da.isnull().any(dim='altitude')
    
    pre_partial_column = da * 6.022e23
    partial_column = pre_partial_column.sum(dim="altitude", skipna=False)
    
    partial_column = partial_column.where(valid_mask)
    
    return partial_column


def get_column_DU(min_alt=None, max_alt=None):
    column = get_column(min_alt, max_alt)
    return column / 2.687e20


def get_time_filtered_vmr(o3, dt1 = "2006-01-01", dt2 = "2020-12-31"):
    return o3.sel(time = slice(dt1, dt2))


def get_zone_filtered_vmr(o3, lat1 = -90, lat2 = 90, long1 = -200, long2 = 200):
    return o3.where(((o3.latitude >= lat1) & (o3.latitude <= lat2) & (o3.longitude >= long1) & (o3.longitude <= long2)), drop = True)


def get_lat(o3):
    return o3["latitude"]


def get_long(o3):
    return o3["longitude"]
