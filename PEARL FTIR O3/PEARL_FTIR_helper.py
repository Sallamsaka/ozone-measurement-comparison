import xarray as xr
import numpy as np
# import pandas as pd
from matplotlib import pyplot as plt
import glob

directory = r'C:\Users\salla\Onedrive(uoft acc)\OneDrive - University of Toronto\Desktop\School Information\NSERC\NSERC\PEARL FTIR O3\netcdf_out'

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


def get_column(min_alt = None, max_alt = None):
    if min_alt == None and max_alt == None:
        return f["O3.COLUMN.PARTIAL_ABSORPTION.SOLAR"]
    elif min_alt == None or max_alt == None:
        raise Exception("Provide both min and max altitude")
    else:
        alt_boundaries = f["ALTITUDE.BOUNDARIES"][0]
        lower_alt_bounds = alt_boundaries[1].values
        upper_alt_bounds = alt_boundaries[0].values
        alt_boundary_diffs = (upper_alt_bounds - lower_alt_bounds)

        min_alt_bound = 0
        max_alt_bound = len(altitude) - 1
        min_proportion = 0
        max_proportion = 0
        bottom_alt_bound = 0
        top_alt_bound = len(altitude) - 1
        no_column = False

        _min_lower_bounds = min(lower_alt_bounds)
        _max_upper_bounds = max(upper_alt_bounds)

        for i, (lower_bound, upper_bound) in enumerate(zip(lower_alt_bounds, upper_alt_bounds)):
            bound_diff = alt_boundary_diffs[i]
            if min_alt < _min_lower_bounds:
                pass
            elif lower_bound <= min_alt <= upper_bound:
                bottom_alt_bound = i-1
                min_proportion = (upper_bound - min_alt) / bound_diff
                min_alt_bound = i
            elif min_alt > _max_upper_bounds:
                no_column = True
                break
            if max_alt > _max_upper_bounds:
                pass
            elif lower_bound <= max_alt <= upper_bound:
                max_alt_bound = i
                top_alt_bound = i+1
                max_proportion = (max_alt - lower_bound) / bound_diff
            elif max_alt < _min_lower_bounds:
                no_column = True
                break

        _top_slice = slice(max_alt_bound, top_alt_bound + 1)
        _middle_slice = slice(min_alt_bound, max_alt_bound + 1)
        _bottom_slice = slice(bottom_alt_bound, min_alt_bound + 1)

        O3_density = get_density()
        O3_column_top = (O3_density.isel(altitude1 = _top_slice) * alt_boundary_diffs[_top_slice]) * max_proportion * 1000
        O3_column = O3_density.isel(altitude1 = _middle_slice) * alt_boundary_diffs[_middle_slice] * 1000
        O3_column_bottom = (O3_density.isel(altitude1 = _bottom_slice) * alt_boundary_diffs[_bottom_slice]) * min_proportion * 1000

        _dim_name = "altitude1"
        O3_partial_column = (O3_column_top.sum(dim = _dim_name) + O3_column.sum(dim = _dim_name) + O3_column_bottom.sum(dim = _dim_name)).where(not no_column, 0)

        return O3_partial_column


def get_column_DU(min_alt = None, max_alt = None):
    if min_alt == None and max_alt == None:
        return get_column(min_alt, max_alt) / 2.687e20
    
    elif min_alt == None or max_alt == None:
        raise Exception("Provide both min and max altitude")
    
    _conversion_factor = 2.687e20
    O3_partial_column = get_column(min_alt, max_alt)
    O3_partial_column_DU = O3_partial_column / _conversion_factor

    return O3_partial_column_DU

def get_time_filtered_vmr(o3, dt1 = "2006-01-01", dt2 = "2020-12-31"):
    return o3.sel(time = slice(dt1, dt2))


def get_zone_filtered_vmr(o3, lat1 = -90, lat2 = 90, long1 = -200, long2 = 200):
    return o3.where(((o3.latitude >= lat1) & (o3.latitude <= lat2) & (o3.longitude >= long1) & (o3.longitude <= long2)), drop = True)


def get_lat(o3):
    return o3["latitude"]


def get_long(o3):
    return o3["longitude"]