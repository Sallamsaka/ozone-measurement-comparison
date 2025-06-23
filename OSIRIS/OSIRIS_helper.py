import numpy as np
from matplotlib import rcParams
from matplotlib import pyplot as pl
import xarray as xr
rcParams["font.size"] = 15

directory = r'C:\Users\salla\Onedrive(uoft acc)\OneDrive - University of Toronto\Desktop\School Information\NSERC\NSERC\OSIRIS'

path = directory + r'\*.nc'

f = xr.open_mfdataset(
    path,
    combine="nested",
    concat_dim="profile_id",
    parallel=True,
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


def get_column(min_alt = f.altitude.min(), max_alt = f.altitude.max()):
    return (O3_density * 1000).sel(altitude = slice(min_alt, max_alt)).sum(dim = "altitude") * 6.022e23


def get_column_DU(min_alt = f.altitude.min(), max_alt = f.altitude.max()):
    return get_column(min_alt, max_alt) / 2.687e20


def get_time_filtered_vmr(o3, dt1 = "2006-01-01", dt2 = "2020-12-31"):
    return o3.sel(time = slice(dt1, dt2))


def get_zone_filtered_vmr(o3, lat1 = -90, lat2 = 90, long1 = -200, long2 = 200):
    return o3.where(((o3.latitude >= lat1) & (o3.latitude <= lat2) & (o3.longitude >= long1) & (o3.longitude <= long2)), drop = True)


def get_lat(o3):
    return o3["latitude"]


def get_long(o3):
    return o3["longitude"]
