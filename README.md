# Ozone Measurement Comparison

**Comparative Analysis of Satellite & Ground-Based Ozone Measurements**  
NSERC USRA @ University of Toronto | May 2025 – Aug 2025

---

## Project Overview
This repo contains the code and notebooks I used to process and validate 1.2 million+ ozone column measurements from satellite and ground-based sensors to quantify instrument biases and temporal consistency.

---

## Summary
- I was awarded one of 15 NSERC USRA positions to investigate atmospheric ozone measurement consistency.  
- I processed over 1.2 M records from HDF4/HDF5 and netCDF files using Pandas, NumPy, and Xarray to standardize data.  
- I engineered pipeline modules for quality-flag filtering, DU ↔ nmol/m² unit conversion, and spatiotemporal matching to ensure comparability.
- I calculated absolute/relative differences, Pearson correlation coefficients, and linear trends to quantify inter-instrument biases. 
- I generated 310+ Matplotlib plots (time series, climatology maps, scatter) to reveal spatial and temporal discrepancy patterns.
