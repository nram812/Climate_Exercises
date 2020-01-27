import xarray as xr
import numpy as np
import pandas as pd
import datetime as dt
from scipy.fftpack import fft, fftfreq, fftshift, ifft
import matplotlib.pyplot as py

class LoadSOI:

# Incorparate a condition to load the SOI dataset
    def __init__(self, soi_directory):

        self.soi_dir = soi_directory
        # Read the SOI data in Tabular form
        self.soi_data = pd.read_csv(soi_directory)


    def extract_values(self, fill_value):
        soi_time_series = np.array(self.soi_data['SOI'],
                                   dtype='float32')
        # Load data as a numpy array
        self.mask_bad_values = (soi_time_series == fill_value)
        soi_time_series[self.mask_bad_values] = np.nan
        self.soi_time_series = soi_time_series
        return self.soi_time_series


    def extract_time_str(self):
        self.time_string = np.array(self.soi_data['index'],
                                   dtype='object')
        return self.time_string

    def convert_time_str_to_arr(self):

        list_of_dates_soi = self.extract_time_str()
        datetime_soi = []
        for date in list_of_dates_soi:
            datetime_soi.append(dt.datetime.strptime(date,
                                "%Y-%d-%m"))
        self.datetime_soi_time = datetime_soi

        return self.datetime_soi_time

    def running_mean_smooth(self, smoothing_interval_months = 5):
        """

        :param smooth_months: Number of months for a smoothing filter
        :return: Smoothed array
        """
        average_filter = np.ones(smoothing_interval_months
                                 ).astype('float32')/\
                         smoothing_interval_months

        return np.convolve(self.soi_time_series, average_filter,
                           mode = 'same')



soi_directory = 'C:/Users/neele/Desktop/' \
                'Southern_Oscillation_Index_dt_index_to_fix.csv'
soi_file = LoadSOI(soi_directory)

fill_value = -9999.9
soi_time_series = soi_file.extract_values(fill_value)
# Apply method of extracting data

time = soi_file.convert_time_str_to_arr()
smooth_interval = 6
soi_time_series_smooth = soi_file.running_mean_smooth(smoothing_interval_months=
                                               smooth_interval)
# Smoothed time-series is computed using a running mean




# Signal Smoothing

fig, ax = py.subplots(figsize=(5,5), dpi=100)

ax.plot_date(time, soi_time_series, 'r--', alpha=0.2,
             label='Original Signal')
ax.plot_date(time, soi_time_series_smooth, 'r-',
             label='Smoothed Signal')

ax.set_xlabel('Time')
ax.set_ylabel('SOI Index')
ax.set_title('SOI Index with a ' + str(smooth_interval) +
             ' Month Box Filter')
ax.legend()

fig.show()




## Task 2

class LoadNino:
    def __init__(self, oni_directory):
        self.directory = oni_directory
        self.nino_data = pd.read_csv(oni_directory,delimiter='  ')

    def extract_values(self, fill_value):
        nino_time_series = np.array(self.nino_data[' TOTAL'],
                                   dtype='float32')
        # Load data as a numpy array
        self.mask_bad_values = (nino_time_series == fill_value)
        nino_time_series[self.mask_bad_values] = np.nan
        self.nino_time_series = nino_time_series
        return self.nino_time_series


# A simple calculation yields the common reference
# point between the arrays
index_common = 869
# Note, at this point the arrays have the exact same time index 1950

#The arrays have a strong negative correlation of -0.84

def compute_correlation(arr1,arr2,month):
    """

    :param arr1: A time-series with a sampling interval of months
    :param arr2: A second time-series with a sampling interval of months
    :param month: The month to compute the correlation over
    :return: pearsons correlation coefficient
    """
    return np.corrcoef(arr1[month::12],arr2[month::12])[0,1]**2
n_months = 12
monthly_corr_coef = [compute_correlation(values,
                                    soi_time_series_smooth[index_common:],
                                    month)
                for month in range(n_months)]



months = [
    'Jan', 'Feb', 'Mar',
    'Apr', 'May', 'Jun',
    'Jul', 'Aug', 'Sep',
    'Oct', 'Nov', 'Dec']
py.figure()
py.plot(months,monthly_corr_coef,'r-x')
py.xlabel('Month')
py.ylabel('Correlation Coefficient$^2$ ($r^2$)')
