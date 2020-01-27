import pandas as pd
import numpy as np
import scipy
import matplotlib.pyplot as plt

ins_directory = 'C:/Users/neele/Downloads/ins12_38S_0to50ka.csv'

class ReadInsolation:

    def __init__(self, ins_directory):

        self.directory = ins_directory
        self.insolation_dset = pd.read_csv(ins_directory)


    def linear_spline(self, insolation):
        """
        Method to compute a bi-variate spline from a two-dimensional
        array
        :return: A callable spline object (x=ka Bp,y=months) as inputs
        """

        K_bpa_arr = np.array(self.insolation_dset['K Year BP'],
                             dtype=float)
        months = np.array(range(12),
                          dtype=float)
        # the above are all the month containing insolation values
        return scipy.interpolate.RectBivariateSpline(K_bpa_arr[:-1], months,
                                                insolation[:-1],
                                                kx=1, ky=1)
    def compute_rolling_average(self, smoothing_filter):
        """
        To compute a rolling average using the mid-monthly points,
        we first oversample the signal using interpolation, then we
        smooth the signal (convolution), and resample it at the old
        sampling rate.
        :param smoothing_filter: length of smoothing interval
        :return: A smoothed signal
        """

        # The smoothing filter is doubled as the sampling is also
        # doubled
        smoothing_filter = smoothing_filter*2
        # Convert pandas dataset to array
        insolation = np.array(self.insolation_dset)[:,1:].ravel(order='C')
        time_steps = np.arange(0, len(insolation))

        interp = scipy.interpolate.interp1d(time_steps, insolation,
                                            kind='linear',
                                            bounds_error=False)
        mid_monthly_pts = np.arange(0, len(insolation), 0.5)
        mid_monthly_interp = interp(mid_monthly_pts)
        average_filter = np.ones(smoothing_filter
                                 ).astype('float32')/ \
                         smoothing_filter
        conv_signal = np.convolve(mid_monthly_interp, average_filter,
                    mode = 'same')[::2]

        # Replace signal end points due to convolution filter
        sig_len = conv_signal.size

        conv_signal[:smoothing_filter] = mid_monthly_interp[:smoothing_filter]
        conv_signal[sig_len-smoothing_filter:] = mid_monthly_interp[sig_len-smoothing_filter]

        return conv_signal


filter_len = 6
n_months = 12
k_bpa_times = range(51)


# Loading and Computing a running mean on the insolation dataset
InsolaionDset = ReadInsolation(ins_directory)
rolling_average = InsolaionDset.compute_rolling_average(filter_len).\
    reshape(n_months,len(k_bpa_times),order='F')
reference_idx = 0
reference_insolation = np.expand_dims(rolling_average[:,reference_idx],
                                      axis=-1)


# Computing the percentage deviation
percentage_dev = abs(rolling_average-reference_insolation)/reference_insolation


def mean_deviation_month(percentage_dev, month):


    percentage_dev = percentage_dev[month:month+1]

    mean_deviation = np.nanmean(percentage_dev, axis=0)*100.0
    std_err_dev = np.nanstd(percentage_dev, axis=0)*100.0
    return mean_deviation, std_err_dev



# Plotting the data

plt.figure()

#Note the last index is filtered out as the last index is
#not smoothed through the convolution operation.
mean_dev_jan,std_dev_jan=mean_deviation_month(percentage_dev,0)
plt.plot(k_bpa_times[:-1],mean_dev_jan[:-1],'r-', label='Jan')
mean_dev_may,std_dev_may=mean_deviation_month(percentage_dev,4)
plt.plot(k_bpa_times[:-1],mean_dev_may[:-1],'b-', label= 'May')
mean_dev_jul,std_dev_jul=mean_deviation_month(percentage_dev,6)
plt.plot(k_bpa_times[:-1],mean_dev_jul[:-1],'g-', label='Jul')
mean_dev_sep,std_dev_sep=mean_deviation_month(percentage_dev,9)
plt.plot(k_bpa_times[:-1],mean_dev_sep[:-1],'k-', label='Sep')
plt.legend()
plt.xlabel('Time (ka BP)')
plt.ylabel('Percentage Deviation (%)')
plt.title('Historical Deviations from Present Day Solar Insolation')

