"""

Embry-Riddle Ionospheric Scintillation Algorithm (EISA)
Version 2
Graphing

Embry-Riddle Aeronautical University
Department of Physical Sciences
Space Physics Research Lab (SPRL)
Author: Nicolas Gachancipa

"""
# External imports.
import pandas as pd
import os

# Internal imports.
from support_functions import (time_ranges, header_size, tec_detrending, slant_to_vertical_tec, naming, plot)

# Set the file separator to work in both Linux and Windows.
filesep = os.sep


# Functions.
def plot_prn(model, prn):
    """
    Function to plot the data of a satellite (prn) with the settigs in a given GraphSettings model.

    :param model (GraphSettings): A GraphSettings model. Refere to the EISA_objects file, GraphSettings class.
    :param prn (str): The satellite. E.g. G1 for GPS 1, or R5 for GLONASS 5.
    :return: success (boolean), error (str): The success variable is True when the plots for the give prn were
             generated succesfully, and False if there was an error. The error variable returns the Exception, or
             None when success == True.
    """

    # Set the directory to the output csv file.
    csv_to_graph = model.file_type + "_" + prn + "_" + model.get_date_str() + ".csv"
    csv_file = model.CSV_dir + filesep + model.get_date_str() + filesep + csv_to_graph

    """
    
    Section: Time ranges.
    Purpose: Determine the range of times in which the satellite is above the elevation threshold.
    
    """
    # For raw files, the elevation data must be extracted from the equivalent reduced file. Set the directory to
    # such file.
    reduced_file = csv_file
    if model.file_type in ['RAWTEC', 'RAWOBS']:
        reduced_file = model.CSV_dir + filesep + "REDTEC" + "_" + prn + "_" + model.get_date_str() + ".csv"
        if not os.path.isfile(reduced_file):
            return False, "Could not find the REDTEC file corresponding to the raw data."

    # If the file can't be found, show an error message.
    if not os.path.isfile(csv_file):
        return False, ("The {} CSV data for the following PRN does not exist (or can't be found in the specified "
                       "directory): {}.".format(model.file_type, prn))

    # Identify the time ranges in which the satellite is above the given threshold. The start_times array indicates
    # the times at which the satellite crosses the threshold and is gaining elevation, while the end_times array
    # contains the times at which the satellite cross the threshold moving downwards (towards the horizon line).
    # Each pair of start-end times is the range of time in which the satellite was above the threshold.
    start_times, end_times = time_ranges(reduced_file, threshold=model.threshold, header=header_size('REDTEC'),
                                         elev_col_name=model.elevation_column_name,
                                         times_col_name=model.times_column_name)
    """

    Section: Data pre-processing.
    Purpose: Filter the dataset to only include the corresponding columns: Time, elevation, signal type, and the 
             graph type selected by the user (the paramater that will be plotted, e.g. Azimuth or TEC15). 

    """
    # Import and read the csv (if it exists).
    if not os.path.isfile(csv_file):
        return "The following directory does not exist: " + csv_file

    # Filter the dataset.
    header = header_size(model.file_type)
    DF = pd.read_csv(csv_file, header=header)
    filtered_DF = DF[DF[model.elevation_column_name] >= model.threshold]
    filtered_DF = filtered_DF[[model.times_column_name, model.elevation_column_name, model.signal_column_name,
                               model.graph_type]]

    # Identify the signal types present in the data (Signal types are an integer between 1 and 7).
    signal_types = filtered_DF[model.signal_column_name].unique()

    """
    
    Section: Plot.
    Purpose: Loop over the signal types previously identified. Make one plot per signal type.
    
    """
    for signal_type in signal_types:

        # Filter the dataset to only include rows corresponding to the signal type being processed.
        signal_data = filtered_DF[filtered_DF[model.signal_column_name] == signal_type]
        signal_data = signal_data.drop(model.signal_column_name, axis=1)

        """
        
        Subsection: Plot per time range.
        Purpose: For each time range previously identified, make one plot. For example, for a satellite which is 
        above the elevation threshold twice in a day (e.g. between 6-9AM and 3-5PM), make one plot for each time 
        period using the start_times and end_times arrays previously created. 
        
        """
        for i, (start_time, end_time) in enumerate(zip(start_times, end_times), 1):

            # Cut the times and y-axis columns for the current time period.
            data = signal_data[signal_data[model.times_column_name] <= end_time]
            data = data[start_time <= data[model.times_column_name]]

            """
            
            Subsection: Other features
            Purpose: Post-data processing, including TEC detrending, night-subtraction (normalization) and TEC 
            slant-to-vertical conversion. 
            
            CREDITS: The Butterworth filter used for TEC detrending was based on a Matlab function written by 
            Dr. Kshitija Deshpande, Professor of Engineering Physics at Embry-Riddle Aeronautical University.
            
            """

            # For scintillation data, get rid of non-sense values (e.g. values above a value of 5).
            # These values may come from errors in the receiver/computer or signal interference and
            # are not representative of S4/sigma scintillation values.
            if model.graph_type in [" S4", " S4_Cor", " 1secsigma", " 3secsigma", " 10secsigma", " 30secsigma",
                                    " 60secsigma"]:
                data = data[data[model.graph_type] <= 5]

            # TEC detrending (High-rate TEC data).
            if model.TEC_detrending and (model.file_type == 'RAWTEC'):
                x_values, y_values = list(data[model.times_column_name]), list(data[model.graph_type])
                data[model.graph_type] = tec_detrending(x_values, y_values)

            # Night subtraction (Low-rate TEC data).
            if model.night_subtraction and (model.file_type == 'REDTEC'):
                y_values = data[model.graph_type]
                data[model.graph_type] = y_values - min(y_values)

            # Vertical TEC conversion (Low-rate TEC data).
            if model.vertical_TEC and (model.file_type == 'REDTEC'):
                y_values, elevations = list(data[model.graph_type]), list(data[model.elevation_column_name])
                data[model.graph_type] = slant_to_vertical_tec(y_values, elevations)

            """
            
            Subsection: Final edits and plot.
            Purpose: Convert times to UTC, define the graph name, and plot.
            
            """

            # Convert times (in seconds) to UTC (in hours).
            data[model.times_column_name] = [(float(i) % 86400) / 3600 for i in data[model.times_column_name]]

            # Determine the signal type (L1, L2, ETC).
            signal_type_name = model.signal_types[prn[0]][str(signal_type)]

            # Name the plot.
            graph_name, title, subtitle = naming(model, prn, signal_type_name, time_period=i)

            # Plot and save the figure.
            x_values, y_values = list(data[model.times_column_name]), list(data[model.graph_type])
            plot(x_values, y_values, prn, graph_name, title, subtitle, model)

    # Return Success.
    return True, None


# ----------- GRAPHING ------------ #
def run_graphing(model):
    # Print start message to terminal.
    print("\n\n# --- " + model.file_type + ": Plotting Time vs. " + model.graph_type + " --- #")
    print('Date (year, month, day): {}, {}, {}'.format(model.date[0], model.date[1], model.date[2]))

    # Add the date folder to the output directory.
    model.output_dir = model.output_dir + filesep + model.get_date_str()

    # Generate plots for the given date and PRNs.
    for prn in model.PRNs_to_plot:
        success, error_msg = plot_prn(model, prn)
        if not success:
            print(error_msg)

# Temporary.
# from EISA_objects import GraphSettings

# m = GraphSettings()
# m.date = [2020, 8, 2]
# m.PRNs_to_plot = ['G1']
# m.output_dir = r'C:\Users\nicol\Desktop\Research Local Files\EISA_OUTPUT\RX1\GRAPHS'
# m.CSV_dir = r'C:\Users\nicol\Desktop\Research Local Files\EISA_OUTPUT\RX1\CSVFILES'
# m.legend = True
# run_graphing(m)

# ------------------------- SECTION 5: PLOTTING --------------------------- #
#    # Generate plots for the given date.
#    for prn in settings.PRNstograph:
#        plot_per_prn(settings, prn, normalize=0)
#    if settings.normalize_data == 1:
#        plt.clf()
#        for prn in settings.PRNstograph:
#            plot_per_prn(m, prn, normalize=1)
#
#    # Print message to the terminal.
#    print("The following day has been processed: " + settings.monthname + " " + str(settings.daynumber) +
#          " - Graph Type: " + str(graph_type) + " - Constellation: " + settings.constellationtype)
