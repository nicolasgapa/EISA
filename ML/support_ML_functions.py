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
import pandas as pd


def plot_scintillation_detections(file, graph_type, prn, threshold, location, signal_type_name, date, time_period=1):
    """
    Function to create a plot with a colorbar indicating if there is a scintillation event present.

    :param file (str): CSV file containing the scintillation data. i.e. it must contain a column 'y' with the labels.
    :param graph_type (str): One of the following: ['S4', '60SecSigma']
    :param prn (str): The satellite number. E.g. 'G1' for GPS 1 or 'R5' for GLONASS 5.
    :param threshold (float): The elevation threshold.
    :param location (str): The location of the receiver. E.g. 'Daytona Beach, FL'
    :param signal_type_name (str): Signal type name. E.g. L1CA, L2Y, L5Q, etc.
    :param date (list): [year, month, day]
    :param time_period (int): When a satellite passes over the receiver more than once during the same day, each range
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
    newcolors = np.vstack((top(np.linspace(1, 0, 32)),
                           bottom(np.linspace(1, 0, no_categories * 32))))
    newcmp = ListedColormap(newcolors, name='OrangeBlue')

    # Identify max value (to set the range of the y-axis). Minimum range of y values is 0-1.
    max_val = max(y_values)
    if max_val <= 1:
        max_val = 1

    # Add NN detections to the plot.
    ax = plt.gca()
    background_map = [np.array([i + 1] * 2) if i != no_categories else np.array([0] * 2) for i in detections]
    background_map = np.stack(background_map, axis=0).T
    detection_map = ax.matshow(background_map, cmap=newcmp, origin='lower', alpha=0.3,
                               extent=[x_values[0], x_values[-1], 0, max_val], aspect='auto', vmin=0,
                               vmax=no_categories + 0.5)

    # Plot visual parameters.
    ax.set_yticks([0 * max_val, 0.2 * max_val, 0.4 * max_val, 0.6 * max_val, 0.8 * max_val, 1 * max_val])
    plt.tick_params(axis='x', which='both', bottom=True, top=False, labelbottom=True, labeltop=False)
    if graph_type == 'S4':
        cbar = plt.colorbar(detection_map, ticks=[0, 1, 2, 3, 4])
        cbar.ax.set_yticklabels(['Multi-Path', 'No Scintillation', 'Low', 'Medium', 'High'])
    else:
        cbar = plt.colorbar(detection_map, ticks=[0, 1, 2, 3, 4, 5])
        cbar.ax.set_yticklabels(['Multi-Path', 'No Scintillation', 'Low', 'Medium', 'High', 'Extreme'])
    plt.subplots_adjust(top=0.85, bottom=0.1)

    # Return plot and plot name.
    return plt, graph_name
