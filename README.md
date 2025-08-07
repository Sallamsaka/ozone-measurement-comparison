# Ozone Measurement Comparison

**Comparative Analysis of Satellite & Ground-Based Ozone Measurements**  
NSERC USRA @ University of Toronto | May 2025 – Aug 2025

---

## Project Overview
This repository contains the code I used to process and validate 1.2 million+ ozone column measurements from satellite (ACE-FTS and OSIRIS) and ground-based (PEARL FTIR) instruments to quantify instrument biases and temporal consistency.

---

## Project Highlights
- Processed over 1.2 M records from HDF4/HDF5 and netCDF files using Pandas, NumPy, and Xarray to standardize data.  
- Engineered pipeline modules for quality-flag filtering, unit conversion, and spatiotemporal matching to ensure comparability.
- Calculated absolute/relative differences, Pearson correlation coefficients, and linear trends to quantify inter-instrument biases. 
- Generated 310+ Matplotlib plots (time series, climatology maps, scatter) to reveal spatial and temporal discrepancy patterns.
