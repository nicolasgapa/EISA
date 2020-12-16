"""

Embry-Riddle Ionospheric Scintillation Algorithm (EISA)
Version 2
Support functions

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


def time_ranges(file, threshold=0, header=0, elev_col_name=' Elev', times_col_name='GPS TOW'):
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
    :return: start_times (list) and end_times (list): List of times when the satellite crosses the given threshold.
    """

    # Open the CSV file, and filter the data using the given elevation threshold.
    DF = pd.read_csv(file, header=header)
    filtered_DF = DF[DF[elev_col_name] >= threshold]
    filtered_DF = filtered_DF[[times_col_name, elev_col_name]]

    # Find the difference between one row and another.
    filtered_DF['Index difference'] = [2] + [x - y for x, y in zip(filtered_DF.index[1:], filtered_DF.index)]

    # Start rows (All those rows that have an index difference greater than 1 with respect to the previous row).
    # The difference > 1 indicates that the data was collected at a different time of the day, and the satellite
    # crossed the elevation theshold multiple times throughout the day.
    start_rows = filtered_DF[filtered_DF['Index difference'] > 1]
    start_times = list(start_rows[times_col_name])

    # End rows.
    end_times = []
    for index, row in start_rows.iloc[1:].iterrows():
        end_row = filtered_DF.loc[int(index - row['Index difference']), :]
        end_times.append(int(end_row[times_col_name]))
    end_times.append(int(filtered_DF.iloc[-1, :][times_col_name]))

    # Return.
    return start_times, end_times


def naming(model, prn, signal_type, time_period=1):
    """
    Fuction to obtain the file name, title, and subtitle of a plot.

    :param model: GraphSettings model.
    :param prn (str): e.g. G1 for GPS 1, or R4 for GLONASS 4
    :param signal_type (str): Name of the signal type, e.g. 'L1CA' (Only valid for individual plots, can be set to
                              None for summary plots).
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
    plot_name = model.get_date_str() + '_' + model.file_type

    # Summary Plot.
    if model.summary_plot:
        plot_name += '_SummaryPlot_' + constellations[prn[0]] + '_' + model.graph_type

    # Individual Plot.
    else:
        plot_name += '_' + model.graph_type + '_' + prn + "_Signal" + '-' + str(signal_type) + '_' + period

    # Normalization (night subtraction) and Vertical TEC.
    if model.graph_type in model.TEC_types:
        if model.night_subtraction:
            plot_name += "_Normalized"
        if model.vertical_TEC:
            plot_name += "_verticalTEC"

    # Set the title  and subtitle of the plot.
    month, day = model.get_date_str()[4:6], model.get_date_str()[6:8]
    title = month_names[month] + " " + day + " - " + "Time (UTC) vs. " + model.graph_type
    subtitle = "Elevation threshold: " + str(model.threshold) + '°'

    # Summary plot title
    if model.summary_plot:
        title += " - Summary Plot - " + constellations[prn[0]]
        subtitle += " - Loc: " + model.location

    # Individual plot title and subtitle.
    else:
        title += " - " + constellations[prn[0]] + " " + prn[1:] + " (" + period + ")"
        subtitle += " - Signal type: " + str(signal_type) + " - Loc: " + model.location

    # Subtitle edits: Normalization (night subtraction) and Vertical TEC.
    if model.night_subtraction:
        subtitle += " - Normalized"
    if model.vertical_TEC:
        subtitle += " - Vertical TEC"

    # Return the plot's file name, title, and subtitle.
    return plot_name, title, subtitle


def tec_detrending(x_values, y_values):
    """"
    Fuction: Detrend the TEC data using a butterworth filter.

    Inputs:
        x_values (list): time values
        y_values (list): TEC values
    Output:
        This function returns the detrended TEC (y-axis) values only.
    """

    # Convert all values to float.
    bftimes = [float(x) for x in x_values]
    bfTEC = [float(y) for y in y_values]

    # TEC: Polyfit subtraction and then a type of Butterworth filtering/ Sliding Avg
    poly_degree = 3  # Filtering on TEC time series (TEC_ts values).
    poly_coef = np.polyfit(bftimes, bfTEC, poly_degree)  # Degree of the polynomial.
    poly = np.polyval(poly_coef, bftimes)  # In this case, y-axis is the TEC vector.
    poly_sub_tec = bfTEC - poly
    polyfit_tec = signal.detrend(poly_sub_tec)
    Tdata = bftimes[-2] - bftimes[0]
    dfreq = 1 / Tdata
    LP = len(polyfit_tec)
    tec_fft = np.fft.fftshift(np.fft.fft(np.fft.ifftshift(polyfit_tec)))

    # ------------------- Butterworth filter -------------------------- #
    cutoff = 0.1  # Desired cut off frequency [Hz]
    order = 6  # Order of the butterworth filter.

    # This extract creates a kernel for low pass butterworth filter.
    freq = np.arange(-LP / 2 * dfreq + dfreq, (LP / 2 * dfreq) + dfreq, dfreq)  # Create frequency array
    butterlow = np.divide(1, np.sqrt(1 + (np.power((freq / cutoff), (2 * order)))))  # Size(freq)
    butterhi = 1.0 - butterlow
    # ----------------------------------------------------------------- #
    tec_filt = np.fft.fftshift(np.fft.ifft(np.fft.ifftshift(np.multiply(tec_fft, butterhi))))
    Detrended_TEC = (np.real(tec_filt))

    # Return the detrendet TEC vector (y-axis values).
    return Detrended_TEC


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


def plot(x_values, y_values, prn, graph_name, title, subtitle, model):
    """
    Function used to plot, and to determine the directory where such plot will be saved.

    Inputs:
        x_values (list): values in the x-axis (usually time).
        y_values (list): values in the y-axis.
        prn (str): Satellite constellation and number. E.g. G1 for GPS 1.
        graph_name (str): Graph name (under which the plot will be saved), not inluding the extension.
        title (str): Plot title (to print).
        subttile (str): Plot subtitle (to print).
        model (GraphSettings): A GraphSettings model including all the plot settings.
    Output:
        plt: Resulting plot.
        str: Directory to the new plot.
    """
    # If the user wants a legend, add the labels. Otherwise, plot without labels.
    if model.legend:
        plt.plot(x_values, y_values, label=prn)
    else:
        plt.plot(x_values, y_values)
    if model.summary_plot:
        plt.linewidth = 0.4

    # Add the X and Y-axis labels.
    plt.ylabel(model.graph_type)
    plt.xlabel('Time (UTC)')

    # Change the limits of the axes (if applicable).
    if model.set_x_axis_range:
        plt.xlim([model.x_axis_start_value, model.x_axis_final_value])
    if model.set_y_axis_range:
        plt.ylim([model.y_axis_start_value, model.y_axis_final_value])

    # If the user wants to print a vertical line, use the axvline function - Line 29 of the GRAPHSETTINGS.csv file.
    if model.vertical_line:
        plt.axvline(x=model.x_value_vertical_line, color='K', linewidth=0.5)

    # Label the plot lines (in-plot legends) - Line 25 of the GRAPHSETTINGS.csv file.
    if model.label_prns:
        xdatapoint, ydatapoint = x_values[int(len(x_values) / 2)], y_values[int(len(y_values) / 2)]
        plt.text(xdatapoint, ydatapoint, prn)

    # Print the title and subtitle in the plot.
    plt.suptitle(title, fontsize=model.title_font_size)
    plt.title(subtitle, fontsize=model.subtitle_font_size)

    # Set the directory, and create it if it does not exist.
    directory = model.output_dir
    if model.summary_plot:
        ftype = "TEC" if model.file_type in ["REDTEC", 'RAWTEC'] else "OBS"
        directory += filesep + "Summary_Plots" + filesep + ftype
    else:
        directory = directory + filesep + model.graph_type
    if not os.path.exists(directory):
        os.makedirs(directory)
    directory += filesep + graph_name + '.' + model.format_type

    # Print the legend on the plot if legend == True.
    if model.legend:
        plt.legend()

    # Return the plot.
    return plt, directory


def header_size(file_type):
    """
    Function to obtain the number of rows in the header of a CSV file (Output of a NovAtel GPStation 6).
    The function can be further modified for EISA to be capable of handling data from other receivers.

    :param file_type (string): File type (reduced/raw, or TEC/scintillation). E.g. "REDTEC"
    :return: header size (int): Number of rows in the header of such file.
    """
    if file_type == "REDTEC" or file_type == "ismRawTEC" or file_type == "ismRawTec" or file_type == "REDOBS":
        return 12
    elif file_type == "ismRawObs" or file_type == "ismRawOBS" or file_type == "ismDetObs" or file_type == "ismDetOBS":
        return 7
