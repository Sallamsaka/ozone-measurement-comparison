import numpy as np
import pandas as pd

seasonal_months = {"DJF": [12,1,2], "MAM": [3,4,5], "JJA": [6,7,8], "SON": [9,10,11]}

class SeasonalHelper:

    def __init__(self, measurement_times, coincidences1, coincidences2):
        pd_measurement_times = pd.to_datetime(measurement_times)
        
        self._seasonal_idx = {season: np.where(pd_measurement_times.month.isin(months))[0]
                            for season, months in seasonal_months.items()}
        
        self._coincidences1 = coincidences1
        self._coincidences2 = coincidences2
        self._times = np.array(measurement_times)


    def seasonal_indices(self):
        return self._seasonal_idx


    def seasonal_coincidences1(self):
        return {
            season: self._coincidences1[idxs]
            for season, idxs in self._seasonal_idx.items()
        }


    def seasonal_coincidences2(self):
        return {
            season: self._coincidences2[idxs]
            for season, idxs in self._seasonal_idx.items()
        }
    

    def seasonal_times(self):
        return {
            season: self._times[idxs]
            for season, idxs in self._seasonal_idx.items()
        }


    def seasonal_coincidences_count(self):
        return {season: len(self._seasonal_idx[season])
                           for season in seasonal_months}
    

    def empty_seasons(self):
        return [season for season, n in self._seasonal_idx.items() if len(n) == 0]