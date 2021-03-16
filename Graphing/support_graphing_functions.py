"""

Embry-Riddle Ionospheric Scintillation Algorithm (EISA)
Version 2
Support functions (Graphing)

Embry-Riddle Aeronautical University
Department of Physical Sciences
Space Physics Research Lab (SPRL)
Author: Nicolas Gachancipa

"""
# Imports.
import os
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
import pandas as pd

filesep = os.sep


def get_date_str(date):
    year, month, day = [str(i) for i in date]
    if len(month) == 1:
        month = '0' + str(month)
    if len(day) == 1:
        day = '0' + str(day)
    return year + month + day


def time_ranges(file, threshold=0, header=0, elev_col_name='Elevation', times_col_name='GPS TOW',
                signal_type_col_name='SigType'):
    """
    This function is used to identify the different periods of time in which a satellite is over the given threshold.
    For example, if a satellite is above a given 30 degree threshold between 6-9 AM and 3-5PM, the function returns
    the following arrays: start_times = [6AM, 3PM] and end_times = [9AM, 5PM]. EISA creates one plot per period of time
    using the arrays returned by this function.

    :param file (string): Directory to the CSV file (including file name).
    :param threshold (float): Elevation threshold.
    :param header (int): Number of header rows in the CSV file (using Python indexing).
    :param elev_col_name (string): Name of the column that contains the elevation data.
    :param times_col_name (string): Name of the column that contains the timesteps.
    :param signal_type_col_name (string): Name of the column that contains the signal tipe.
    :return: start_times (list) and end_times (list): List of times when the satellite crosses the given threshold.
    """

    # Open the CSV file.
    DF = pd.read_csv(file, header=header)

    # If the dataset is empty, return two empty lists.
    if len(DF) == 0:
        return [], []

    # Only process one signal type (the first one).
    DF = DF[DF[signal_type_col_name] == DF[signal_type_col_name][0]]

    # Filter the data using the given elevation threshold.
    filtered_DF = DF[DF[elev_col_name] >= threshold]
    filtered_DF = filtered_DF[[times_col_name, elev_col_name]]

    # Find the difference between one row and another.
    filtered_DF['difference'] = [600] + [x - y for x, y in zip(filtered_DF[times_col_name][1:],
                                                               filtered_DF[times_col_name])]
    # Start rows (All those rows that have an index difference greater than 600 with respect to the previous row).
    # The difference > 600 indicates that the data was collected at a different time of the day (at least 600 seconds
    # or 10 minutes later), and the satellite crossed the elevation theshold multiple times throughout the day.
    start_rows = filtered_DF[filtered_DF['difference'] >= 600]
    start_rows = start_rows.dropna()
    start_times = list(start_rows[times_col_name])

    # Identiy the end times.
    filtered_DF['end difference'] = list(filtered_DF['difference'][1:]) + [600]
    end_rows = filtered_DF[filtered_DF['end difference'] >= 600]
    end_rows = end_rows.dropna()
    end_times = list(end_rows[times_col_name])

    # Remove outliers in the data (i.e. when the start and end times are equal).
    idx_to_remove = sorted([e for e, (x, y) in enumerate(zip(start_times, end_times)) if x - y == 0])[::-1]
    for i in idx_to_remove:
        del start_times[i]
        del end_times[i]

    # Return.
    return start_times, end_times


def naming(prn, signal_type, date, time_period=1, file_type='REDTEC', graph_type='Azimuth', summary_plot=False,
           night_subtraction=False, vertical_TEC=False, threshold=30, location=''):
    """
    Fuction to obtain the file name, title, and subtitle of a plot.

    :param prn (str): e.g. G1 for GPS 1, or R4 for GLONASS 4
    :param signal_type (str): Name of the signal type, e.g. 'L1CA' (Only valid for individual plots, can be set to
                              None for summary plots).
    :param date (list): Date: [year, month, day]
    :param time_period (int): An integer indicating the time period of the plot. E.g. if the satellite is over the
                              elevation threshold during two time periods in a single day (e.g. 6-9AM and 3-5PM),
                              the plot showing time period "1" (6-9AM) must have time_period == 1, while the plot for
                              time period 2 (3-5PM), must have time_period == 2. Default: 1.
    :return: plot_name (str), title (str), subttitle (str)
    """
    # Define the month names.
    month_names = {'01': 'January', '02': 'February', '03': 'March', '04': 'April', '05': 'May', '06': 'June',
                   '07': 'July', '08': 'August', '09': 'September', '10': 'October', '11': 'November', '12': 'December'}

    # Define constellation types.
    constellations = {"G": "GPS", "R": "GLONASS", "E": "GALILEO"}

    # The time_period_vars letter will be printed in the title of the plot.
    # The letter represents the time period. e.g. if there are two time periods for one PRN in a single day
    # (e.g. 6-9AM and 3-5PM), the plot showing time period 1 (6-9AM) will have an "A" in the title.
    # Time period 2 (3-5PM) will have a "B".
    time_period_vars = {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E', 6: 'F', 7: 'G', 8: 'H', 9: 'I', 10: 'J'}
    period = time_period_vars[time_period]

    # Define the plot name.
    plot_name = get_date_str(date) + '_' + file_type

    # Summary Plot.
    if summary_plot:
        plot_name += '_SummaryPlot_' + constellations[prn[0]] + '_' + graph_type

    # Individual Plot.
    else:
        plot_name += '_' + graph_type + '_' + prn + "_Signal" + '-' + str(signal_type) + '_' + period

    # Normalization (night subtraction) and Vertical TEC.
    if graph_type in ['TEC15', 'TEC30', 'TEC45', 'TECTOW', 'TEC']:
        if night_subtraction:
            plot_name += "_Normalized"
        if vertical_TEC:
            plot_name += "_verticalTEC"

    # Set the title  and subtitle of the plot.
    month, day = get_date_str(date)[4:6], get_date_str(date)[6:8]
    title = month_names[month] + " " + day + " - " + "Time (UTC) vs. " + graph_type
    subtitle = "Elevation threshold: " + str(threshold) + '°'

    # Summary plot title
    if summary_plot:
        title += " - Summary Plot - " + constellations[prn[0]]
        subtitle += " - Loc: " + location

    # Individual plot title and subtitle.
    else:
        title += " - " + constellations[prn[0]] + " " + prn[1:] + " (" + period + ")"
        subtitle += " - Signal type: " + str(signal_type) + " - Loc: " + location

    # Subtitle edits: Normalization (night subtraction) and Vertical TEC.
    if night_subtraction:
        subtitle += " - Normalized"
    if vertical_TEC:
        subtitle += " - Vertical TEC"

    # Return the plot's file name, title, and subtitle.
    return plot_name, title, subtitle


def detrend(x_values, y_values, poly_degree=3, cutoff=0.1, order=6):
    """"
    Fuction: Detrend TEC or phase scintillation data using a butterworth filter.
    To detrend power scintillation data, use the power_detrend function.

    Inputs:
        x_values (list): time values.
        y_values (list): TEC values.
        poly_degree (int): Degree of the polynomial.
        cutoff (float): Desired cut off frequency [Hz]
        order (int): Order of the butterworth filter.
    Output:
        This function returns the detrended TEC or phase sinctillation (y-axis) values only.
    """

    # Convert all values to float.
    bftimes = [float(x) for x in x_values]
    bfTEC = [float(y) for y in y_values]

    # TEC: Polyfit subtraction and then a type of Butterworth filtering/ Sliding Avg
    poly_coef = np.polyfit(bftimes, bfTEC, poly_degree)  # Degree of the polynomial.
    poly = np.polyval(poly_coef, bftimes)  # In this case, y-axis is the TEC vector.
    poly_sub_tec = bfTEC - poly
    polyfit_tec = signal.detrend(poly_sub_tec)
    Tdata = bftimes[-2] - bftimes[0]
    dfreq = 1 / Tdata
    LP = len(polyfit_tec)
    tec_fft = np.fft.fftshift(np.fft.fft(np.fft.ifftshift(polyfit_tec)))

    # ------------------- Butterworth filter -------------------------- #
    # This extract creates a kernel for low pass butterworth filter.
    freq = np.arange(-LP / 2 * dfreq + dfreq, (LP / 2 * dfreq) + dfreq, dfreq)  # Create frequency array
    butterlow = np.divide(1, np.sqrt(1 + (np.power((freq / cutoff), (2 * order)))))  # Size(freq)
    butterhi = 1.0 - butterlow
    # ----------------------------------------------------------------- #
    tec_filt = np.fft.fftshift(np.fft.ifft(np.fft.ifftshift(np.multiply(tec_fft, butterhi))))
    Detrended_TEC = (np.real(tec_filt))

    # Return the detrendet TEC vector (y-axis values).
    return Detrended_TEC


def power_detrend(x_values, y_values, cutoff=0.1, order=6):
    """"
    Fuction: Detrend power scintillation data using a butterworth filter.
    To detrend phase scintillation data or TEC, use the detrend function.

    Inputs:
        x_values (list): time values.
        y_values (list): TEC values.
        cutoff (float): Desired cut off frequency [Hz]
        order (int): Order of the butterworth filter.
    Output:
        This function returns the detrended power (y-axis) values only.
    """
    data_rate = 1. / np.mean(np.diff(x_values))
    b, a = signal.butter(order, cutoff / (0.5 * data_rate))
    y = signal.filtfilt(b, a, y_values)
    power_detrend = 10 * np.log10(y_values / y)
    return power_detrend


def slant_to_vertical_tec(y_values, elevations):
    """
    This function converts slant TEC values to vertical TEC (considering Earth's geometry).

    :param y_values: The TEC values (y-axis values of a TEC plot).
    :param elevations: The elevation values corresponding to the TEC values.
    :return: new_y_values (list): Corrected TEC values.
    """
    min_value = min(y_values)
    normalized = np.array([i - min_value for i in y_values])
    cos_elevations = np.cos(np.array(elevations) * 0.0174533)
    obliquities = 1 / (np.sqrt(1 - (0.947979 * cos_elevations)))
    new_y_values = (normalized / obliquities) + min_value
    return new_y_values


def plot(x_values, y_values, prn, title, subtitle, line_width=1, legend=False,
         label_prns=False, graph_type='Azimuth', title_font_size=12, subtitle_font_size=12,
         set_x_axis_range=False, set_y_axis_range=False, x_axis_start_value=0, x_axis_final_value=1,
         y_axis_start_value=0, y_axis_final_value=1, vertical_line=False, x_value_vertical_line=0, units=None,
         plot_type='line'):
    """
    Function used to plot, and to determine the directory where such plot will be saved.

    Inputs:
        x_values (list): values in the x-axis (usually time).
        y_values (list): values in the y-axis.
        prn (str): Satellite constellation and number. E.g. G1 for GPS 1.
        graph_name (str): Graph name (under which the plot will be saved), not including the extension.
        title (str): Plot title (to print).
        subtitle (str): Plot subtitle (to print).
        model (GraphSettings): A GraphSettings model including all the plot settings.
        plot_type (Str): 'line' or 'scatter'
    Output:
        plt: Resulting plot.
    """
    # Plot.
    # If the user wants a legend, add the labels. Otherwise, plot without labels. For summary plots, reduce the
    # line width to 0.4.
    if plot_type == 'scatter':
        plt.scatter(x_values, y_values, s=0.05)
    else:
        if legend:
            plt.plot(x_values, y_values, label=prn, linewidth=line_width)
        else:
            plt.plot(x_values, y_values, linewidth=line_width)

    # Add the X and Y-axis labels.
    if units is None:
        plt.ylabel(graph_type)
    else:
        plt.ylabel(graph_type + ' ({})'.format(units))
    plt.xlabel('Time (UTC)')

    # Change the limits of the axes (if applicable).
    if set_x_axis_range:
        plt.xlim(x_axis_start_value, x_axis_final_value)
    if set_y_axis_range:
        plt.ylim(y_axis_start_value, y_axis_final_value)

    # If the user wants to print a vertical line, use the axvline function - Line 29 of the GRAPHSETTINGS.csv file.
    if vertical_line:
        plt.axvline(x=x_value_vertical_line, color='K', linewidth=0.5)

    # Label the plot lines (in-plot legends) - Line 25 of the GRAPHSETTINGS.csv file.
    if label_prns:
        xdatapoint, ydatapoint = x_values[int(len(x_values) / 2)], y_values[int(len(y_values) / 2)]
        plt.text(xdatapoint, ydatapoint, prn)

    # Print the title and subtitle in the plot.
    plt.suptitle(title, fontsize=title_font_size)
    plt.title(subtitle, fontsize=subtitle_font_size)

    # Print the legend on the plot if legend == True.
    if legend:
        plt.legend()

    # Return the plot.
    return plt


def times_to_filter_df(df, start_times, end_times):
    """
    Filter a DF given a set of start and end times. All the data inside the time intervals defined y the start_times
    and end_times lists are returned in a new DF.

    :param df (pandas dataframe): Original data frame.
    :param start_times (list): A list of the start times of each time interval.
    :param end_times (list): A list of the end times of each time interval
    :return: pandas data frame: The filtered data frame.
    """
    new_df = []
    for s, e in zip(start_times, end_times):
        data = df[df['GPS TOW'] >= s]
        data = data[data['GPS TOW'] <= e]
        new_df.append(data)
    new_df = pd.concat(new_df)
    return new_df
