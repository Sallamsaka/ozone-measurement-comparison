import xarray as xr
import numpy as np
# import pandas as pd
import glob
from file_paths import PARENT_FOLDER
directory = PARENT_FOLDER + r'\PEARL_FTIR\netcdf_out'

path = directory + r'\*.nc'

nc_list = glob.glob(path)

f = xr.open_mfdataset(
    nc_list,
    combine="nested",
    concat_dim="idx",
    parallel=True,
    decode_cf=True
)

f = f.swap_dims({"idx": "DATETIME"})

f = f.sortby("DATETIME")

alt_boundaries = f["ALTITUDE.BOUNDARIES"][0].values

alt_boundaries_flat = np.mean(alt_boundaries, axis = 0)

f = f.assign_coords(altitude1 = ("altitude1", alt_boundaries_flat))
f = f.sortby("altitude1")

O3_vmr = f["O3.MIXING.RATIO.VOLUME_ABSORPTION.SOLAR"] * 1e-6
latitude = 80.05
longitude = -86.42
altitude = O3_vmr["altitude1"]

O3_column = f["O3.COLUMN.PARTIAL_ABSORPTION.SOLAR"]
O3_column_DU = O3_column / 2.687e20

def get_vmr():
    return O3_vmr


def get_temperature():
    return f["TEMPERATURE_INDEPENDENT"]


def get_pressure():
    return f["PRESSURE_INDEPENDENT"] * 100


def get_density():
    return O3_vmr * get_pressure()/(1.380649e-23 * get_temperature())


def get_column(min_alt=None, max_alt=None):
    if min_alt is None or max_alt is None:
        raise ValueError("Both min_alt and max_alt must be provided")
    if min_alt > max_alt:
        min_alt, max_alt = max_alt, min_alt
        
    alt_boundaries = f["ALTITUDE.BOUNDARIES"][0]
    lower_bounds = alt_boundaries[1].values
    upper_bounds = alt_boundaries[0].values
    layer_thickness = upper_bounds - lower_bounds
    
    alt_min = np.min(lower_bounds)
    alt_max = np.max(upper_bounds)
    min_alt_clamped = max(min_alt, alt_min)
    max_alt_clamped = min(max_alt, alt_max)

    min_mask = (lower_bounds <= min_alt_clamped) & (min_alt_clamped < upper_bounds)
    max_mask = (lower_bounds < max_alt_clamped) & (max_alt_clamped <= upper_bounds)
    
    if not np.any(min_mask):
        print(alt_min, min_alt, min_alt_clamped)
        raise ValueError(f"min_alt {min_alt}km outside profile range after clamping")
    else:
        min_idx = np.where(min_mask)[0][0]

    if not np.any(max_mask):
        raise ValueError(f"max_alt {max_alt}km outside profile range after clamping")
    else:
        max_idx = np.where(max_mask)[0][0]

    min_proportion = (upper_bounds[min_idx] - min_alt_clamped) / layer_thickness[min_idx]
    max_proportion = (max_alt_clamped - lower_bounds[max_idx]) / layer_thickness[max_idx]
    
    O3_density = get_density()

    pre_partial_column = xr.zeros_like(O3_density)
    
    if min_idx == max_idx:
        proportion = (max_alt_clamped - min_alt_clamped) / layer_thickness[min_idx]
        pre_partial_column[{"altitude1": min_idx}] = ((f["O3.COLUMN.PARTIAL_ABSORPTION.SOLAR"] * 10000).isel(altitude1=min_idx)
            * proportion
        )
    else:
        pre_partial_column[{"altitude1": min_idx}] = (
            O3_density.isel(altitude1=min_idx) 
            * layer_thickness[min_idx]
            * 1000 
            * min_proportion
        )
        
        if max_idx - min_idx > 1:
            mid_slice = slice(min_idx+1, max_idx)
            pre_partial_column[{"altitude1": mid_slice}] = ((f["O3.COLUMN.PARTIAL_ABSORPTION.SOLAR"] * 10000).isel(altitude1=mid_slice)
            )
        
        pre_partial_column[{"altitude1": max_idx}] = (
            O3_density.isel(altitude1=max_idx)
            * layer_thickness[max_idx]
            * 1000
            * max_proportion
        )

    partial_column = pre_partial_column.sum(dim="altitude1", skipna=True)
    all_nan = pre_partial_column.isnull().all(dim="altitude1")
    partial_column = partial_column.where(~all_nan)
    return partial_column


def get_column_DU(min_alt = None, max_alt = None):
    _conversion_factor = 2.687e20
    O3_partial_column = get_column(min_alt, max_alt)
    return O3_partial_column / _conversion_factor

def get_time_filtered_vmr(o3, dt1 = "2006-01-01", dt2 = "2020-12-31"):
    return o3.sel(DATETIME = slice(dt1, dt2))


def get_zone_filtered_vmr(o3, lat1 = -90, lat2 = 90, long1 = -200, long2 = 200):
    return o3.where(((o3.latitude >= lat1) & (o3.latitude <= lat2) & (o3.longitude >= long1) & (o3.longitude <= long2)), drop = True)


def get_lat(o3):
    return o3["latitude"]


def get_long(o3):
    return o3["longitude"]