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


def plot_scintillation_detections(file, graph_type, prn, threshold, location, signal_type_name, date, time_period=1):
    # Open output file.
    df = pd.read_csv(file)

    # Filter out values below the given elevation threshold.
    df = df[df['Elevation'] >= threshold]

    # Plot settings.
    x_values, y_values, detections = list(df['GPS TOW']), list(df[graph_type]), list(df['y'])
    x_values = [(float(i) % 86400) / 3600 for i in x_values]
    output_dir = os.path.dirname(file)

    # Obtain name, title, and subtitle.
    graph_name, title, subtitle = naming(prn, signal_type_name, date, time_period=time_period, file_type='REDOBS',
                                         graph_type=graph_type, threshold=threshold, location=location)
    graph_name += '_ML_Output'

    # Plot.
    plt, _ = plot(x_values, y_values, None, graph_name, title, subtitle, output_dir, file_type='REDOBS',
                  graph_type=graph_type, set_y_axis_range=True, y_axis_start_value=0, y_axis_final_value=1, units=None)

    # Plot colors.
    top = cm.get_cmap('Oranges_r', 128)
    bottom = cm.get_cmap('Blues', 32)
    newcolors = np.vstack((top(np.linspace(0, 1, 128)),
                           bottom(np.linspace(0, 1, 32))))
    newcmp = ListedColormap(newcolors, name='OrangeBlue')

    # Add NN detections to the plot.
    ax = plt.gca()
    new_array = [np.array([abs(i-3)] * 2) if i <= 3 else np.array([i] * 2) for i in detections]
    new_array = np.stack(new_array, axis=0).T
    detection_map = ax.matshow(new_array, cmap=newcmp, origin='lower', alpha=0.3,
                               extent=[x_values[0], x_values[-1], 0, 1], aspect='auto', vmin=0, vmax=4.5)

    # Plot visual parameters.
    ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1])
    plt.tick_params(axis='x', which='both', bottom=True, top=False, labelbottom=True, labeltop=False)
    cbar = plt.colorbar(detection_map, ticks=[0, 1, 2, 3, 4])
    cbar.ax.set_yticklabels(['Extreme', 'High', 'Low', 'No Scintillation', 'Multi-Path'])
    plt.subplots_adjust(top=0.85, bottom=0.1)

    # Return plot.
    return plt
