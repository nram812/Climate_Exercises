import h5py
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import datetime as dt

class LoadNetcdf:
    def __init__(self, directory):

        self.directory = directory
        self.n_months = 12
        # Loading the NetCDF file
        self.netcdf=h5py.File(directory,'r')
    def _get_air_temp_data(self):
        self.air_temp = self.netcdf['air']
        # Acessing the Temperature data attributes
        return self.netcdf['air']
    def _get_lat_lon_meshgrid(self):

        lat = self.netcdf['lat'][:]
        lon = self.netcdf['lon'][:]
        # Accessing the Lat/Lon fields
        lat_mesh, lon_mesh = np.meshgrid(lat, lon)
        # Creating a Meshgrid for plotting data
        return lat_mesh.T, lon_mesh.T

    def compute_monthly_mean(self):
        self.time_len = len(self.netcdf['time'][:])
        self.lat_shape = len(self.netcdf['lat'][:])
        self.lon_shape = len(self.netcdf['lon'][:])
        year_0 = 1950
        time_ref_0 = 1981
        time_ref_1 = 2010

        # Reshaping the data so that computing a monthly average is easy

        self.monthly_reshaping = self.netcdf['air'][:].reshape(
            self.time_len//self.n_months,
            self.n_months,
            self.lat_shape,
            self.lon_shape)
        # Reassign monthly orgaise

        return np.nanmean(self.monthly_reshaping[time_ref_0-year_0:
                                                 time_ref_1-year_0],
                          axis=0)
    def compute_anomalies(self):
        # Extract Monthly Averages
        monthly_means = self.compute_monthly_mean()[np.newaxis,:]
        repeat_steps = self.time_len // self.n_months
        monthly_means = np.repeat(monthly_means, repeat_steps,
                                  axis=0)
        # Repeating the Monthly means to have the same shape
        # As the original time-series for subtraction


        monthly_anomaly = self.monthly_reshaping - monthly_means
        return monthly_anomaly

    def compute_global_anomallies(self):
        # Computing the Average anomally globally (Lat/Lon averaging)
        # Axis (-1,-2) are the lat/lon axes
        monthly_anomally = self.compute_anomalies()
        return np.nanmean(monthly_anomally,
                          axis= (-1, -2))

    def compute_global_annual_anomalies(self):
        # Same as previous function, but averages over month too.
        monthly_anomally = self.compute_anomalies()
        return np.nanmean(monthly_anomally,
                          axis= (-1, -2, -3))

air_temp_directory = r'C:\Users\neele\Desktop\air.mon.mean.nc'
AirTempData =  LoadNetcdf(air_temp_directory)
air_temp_monthly = AirTempData.compute_monthly_mean()
lats, lons = AirTempData._get_lat_lon_meshgrid()


# Plotting the data using Cartopy
months_dict=['January', 'February', 'March', 'April']
proj = ccrs.PlateCarree(central_longitude=180)
fig, axes = plt.subplots(2, 2, subplot_kw=dict(projection=proj))
# Setting up a suitable projection to load the data onto
axes = axes.ravel()

# get the path of the file. It can be found in the repo data directory.



for months_idx in range(len(axes)):

    cs = axes[months_idx].contourf(lons, lats,
                                   air_temp_monthly[months_idx],
                                   30,
                               transform=ccrs.PlateCarree(), cmap='jet')

    axes[months_idx].coastlines()
    axes[months_idx].set_title(months_dict[months_idx])


cbar_axes = fig.add_axes([0.92, 0.15, 0.01, 0.7])
cbar = fig.colorbar(cs, cax=cbar_axes)
cbar_tick_range = np.arange(-60,60,5)
cbar.set_ticks(cbar_tick_range)
cbar.set_ticklabels(cbar_axes)
cbar.set_label('Temperature ($\degree$ C)')
fig.suptitle('Global Air Temperature Monthly Means')
plt.show()





# Computing the Annual Anomalies


annual_anomally = AirTempData.compute_global_annual_anomalies()
# Output shape is a (72,) length array
anomally = AirTempData.compute_global_anomallies()
# Output shape is a (864,) length array

anomally_global = AirTempData.compute_anomalies()
# Output shape is (864,72,144) and represents global anomalies

year_0 = 1950
years = np.arange(year_0, year_0+len(annual_anomally))
from scipy.stats import linregress
slope, intercept, rvalue, pvalue, stderr = \
    linregress(years,annual_anomally)

plt.figure()
plt.plot(years,annual_anomally,'rx', alpha=0.6, label='Data')
plt.plot(years, slope*years + intercept,'r--',
         label='$\delta$ T ($\degree$ C)=%.2f YR +%.2f, $r^2$ = %.2f' %
                                                     (slope, intercept,
                                                      rvalue**2))
plt.xlabel('Year (YR)')
plt.ylabel('Temperature Anomally ($\delta$ T)')
plt.title('Global Air Temperature Trends')
plt.legend()


#Note please see other methods linked to this class for other questions asked.






