"""

Embry-Riddle Ionospheric Scintillation Algorithm (EISA)
Version 2
Support functions (ML)

Embry-Riddle Aeronautical University
Department of Physical Sciences
Space Physics Research Lab (SPRL)
Author: Nicolas Gachancipa

"""
# Imports.
from Graphing.support_graphing_functions import plot, naming
from matplotlib import cm
from matplotlib.colors import ListedColormap
import numpy as np
import os
import pandas as pd
import subprocess

filesep = os.sep


def time_ranges_scintillation(file, threshold=1, header=0, scintillation_col_name='y', times_col_name='GPS TOW'):
    """
    This function is used to identify the different periods of time in which a satellite's signal is experiencing
    scintillation. For example, if the signal is experiencing scintillation between 6-9 AM and 3-5PM, the function
    returns the following arrays: start_times = [6AM, 3PM] and end_times = [9AM, 5PM]. EISA creates one plot per
    period of time using the arrays returned by this function.

    :param file: (string) Directory to the CSV file (including file name).
    :param threshold: (float) Threshold. The scintillation column must contain labels specifying if there is a
                              scintillation event happening. EISA's default labels are: 0 for no scintillation,
                              1 (or more) for scintillation.
    :param header: (int) Number of header rows in the CSV file (using Python indexing).
    :param scintillation_col_name: (string) Name of the column that contains the scintillation labels.
    :param times_col_name: (string) Name of the column that contains the time steps.
    :return: start_times (list) and end_times (list): List of times when the satellite crosses the given threshold.
    """

    # Open the CSV file.
    DF = pd.read_csv(file, header=header)

    # If the dataset is empty, return two empty lists.
    if len(DF) == 0:
        return [], []

    # Filter the data using the given scintillation threshold.
    filtered_DF = DF[DF[scintillation_col_name] >= threshold]
    filtered_DF = filtered_DF[[times_col_name, scintillation_col_name]]

    # Find the difference between one row and another.
    filtered_DF['difference'] = [120] + [x - y for x, y in zip(filtered_DF[times_col_name][1:],
                                                               filtered_DF[times_col_name])]

    # Start rows (All those rows that have an index difference greater than 600 with respect to the previous row).
    # The difference > 600 indicates that the data was collected at a different time of the day (at least 600 seconds
    # or 10 minutes later), and the satellite crossed the elevation threshold multiple times throughout the day.
    start_rows = filtered_DF[filtered_DF['difference'] > 60]
    start_rows = start_rows.dropna()
    start_times = list(start_rows[times_col_name])

    # Identify the end times.
    filtered_DF['end difference'] = list(filtered_DF['difference'][1:]) + [120]
    end_rows = filtered_DF[filtered_DF['end difference'] > 60]
    end_rows = end_rows.dropna()
    end_times = list(end_rows[times_col_name])

    # Remove outliers in the data (i.e. when the start and end times are equal).
    idx_to_remove = sorted([e for e, (x, y) in enumerate(zip(start_times, end_times)) if x - y == 0])[::-1]
    for i in idx_to_remove:
        del start_times[i]
        del end_times[i]

    # Return.
    return start_times, end_times


def high_rate_parsing(reduced_file, output_file, exe_file, binary_file, prn):
    # Identify the time periods.
    start_times, end_times = time_ranges_scintillation(reduced_file)
    print(start_times, end_times)

    # For each time period, parse the raw data.
    for e, (start_time, end_time) in enumerate(zip(start_times, end_times), 1):
        # Command.
        exe_command = prn + " \"" + binary_file + "\" \"" + output_file + "\""

        # Add the times to the command.
        binary_file_name = os.path.basename(binary_file)
        week_number, week_day_number = int(binary_file_name[:4]), int(binary_file_name[5])
        start_time_GPS_TOW = week_day_number * 86400 + start_time
        end_time_GPS_TOW = week_day_number * 86400 + end_time
        exe_command = exe_command + " " + str(start_time_GPS_TOW) + " " + str(end_time_GPS_TOW) + " " + str(
            week_number) + " " + str(week_number)

        # Parse the file by running the command.
        print(exe_file + ' ' + exe_command)
        subprocess.call("\"{}\" {}".format(exe_file, exe_command))


def plot_scintillation_detections(file, graph_type, prn, threshold, location, signal_type_name, date, time_period=1):
    """
    Function to create a plot with a color bar indicating if there is a scintillation event present.

    :param file: (str) CSV file containing the scintillation data. i.e. it must contain a column 'y' with the labels.
    :param graph_type: (str) One of the following: ['S4', '60SecSigma']
    :param prn: (str) The satellite number. E.g. 'G1' for GPS 1 or 'R5' for GLONASS 5.
    :param threshold: (float) The elevation threshold.
    :param location: (str) The location of the receiver. E.g. 'Daytona Beach, FL'
    :param signal_type_name: (str) Signal type name. E.g. L1CA, L2Y, L5Q, etc.
    :param date: (list) [year, month, day]
    :param time_period: (int) When a satellite passes over the receiver more than once during the same day, each range
                              of times at which the satellite was locked to the receiver is a time period. For example,
                              let us say that satellite G1 passes over the receiver twice in a day. First, between
                              6AM and 8AM, and then between 8PM and 10PM. The period between 6AM and 8AM is therefore
                              time_period == 1, while the 8PM-10PM corresponds to time_period == 2.
    :return: plt: Resulting matplotlib plot, str: graph name.
    """

    # Validate.
    if graph_type not in ['S4', '60SecSigma']:
        raise Exception("Graph type must be one of the following: ['S4', '60SecSigma'].")

    # Open output file.
    df = pd.read_csv(file)

    # Filter out values below the given elevation threshold.
    df = df[df['Elevation'] >= threshold]

    # Plot settings.
    x_values, y_values, detections = list(df['GPS TOW']), list(df[graph_type]), list(df['y'])
    x_values = [(float(i) % 86400) / 3600 for i in x_values]

    # Obtain name, title, and subtitle.
    graph_name, title, subtitle = naming(prn, signal_type_name, date, time_period=time_period, file_type='REDOBS',
                                         graph_type=graph_type, threshold=threshold, location=location)
    graph_name += '_ML_Output'

    # Plot.
    plt = plot(x_values, y_values, None, title, subtitle, graph_type=graph_type, set_y_axis_range=True,
               y_axis_start_value=0, y_axis_final_value=1, units=None)

    # Number of output categories (4 for S4 and 5 for 60SecSigma). This number is used to create the color bar.
    if graph_type == 'S4':
        no_categories = 4
    else:
        no_categories = 5

    # Plot colors
    bottom = cm.get_cmap('Oranges_r', no_categories * 32)
    top = cm.get_cmap('Blues', 32)
    new_colors = np.vstack((top(np.linspace(1, 0, 32)),
                           bottom(np.linspace(1, 0, no_categories * 32))))
    new_cmp = ListedColormap(new_colors, name='OrangeBlue')

    # Identify max value (to set the range of the y-axis). Minimum range of y values is 0-1.
    max_val = max(y_values)
    if max_val <= 1:
        max_val = 1

    # Add NN detections to the plot.
    ax = plt.gca()
    background_map = [np.array([i + 1] * 2) if i != no_categories else np.array([0] * 2) for i in detections]
    background_map = np.stack(background_map, axis=0).T
    detection_map = ax.matshow(background_map, cmap=new_cmp, origin='lower', alpha=0.3,
                               extent=[x_values[0], x_values[-1], 0, max_val], aspect='auto', vmin=0,
                               vmax=no_categories + 0.5)

    # Plot visual parameters.
    ax.set_yticks([0 * max_val, 0.2 * max_val, 0.4 * max_val, 0.6 * max_val, 0.8 * max_val, 1 * max_val])
    plt.tick_params(axis='x', which='both', bottom=True, top=False, labelbottom=True, labeltop=False)
    if graph_type == 'S4':
        c_bar = plt.colorbar(detection_map, ticks=[0, 1, 2, 3, 4])
        c_bar.ax.set_yticklabels(['Multi-Path', 'No Scintillation', 'Low', 'Medium', 'High'])
    else:
        c_bar = plt.colorbar(detection_map, ticks=[0, 1, 2, 3, 4, 5])
        c_bar.ax.set_yticklabels(['Multi-Path', 'No Scintillation', 'Low', 'Medium', 'High', 'Extreme'])
    plt.subplots_adjust(top=0.85, bottom=0.1)

    # Return plot and plot name.
    return plt, graph_name
