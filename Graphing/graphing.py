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
from support_functions import (time_ranges, header_size,

                               naming, tec_detrending, slant_to_vertical_tec, seconds_to_utc,
                               plot)
from EISA_objects import GraphSettings

# Set the file separator to work in both Linux and Windows.
filesep = os.sep


# Functions.
def plot_prn(model, prn):

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
    if model.file_type in model.raw_data_types:
        reduced_file = model.CSV_dir + filesep + "REDTEC" + "_" + prn + "_" + model.get_date_str() + ".csv"
        if not os.path.isfile(reduced_file):
            return "Could not find the REDTEC file corresponding to the raw data."

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
        for i, (start_time, end_time) in enumerate(zip(start_times, end_times)):

            # Cut the times and y-axis columns for the current time period.
            times_data = signal_data[signal_data[model.times_column_name] <= end_time]
            times_data = times_data[start_time <= times_data[model.times_column_name]]

            """
            
            Subsection: Other features
            Purpose: Post-data processing, including TEC detrending, night-subtraction (normalization) and TEC 
            slant-to-vertical conversion. 
            
            CREDITS: The Butterworth filter used for TEC detrending was based on a Matlab function written by 
            Dr. Kshitija Deshpande, Professor of Engineering Physics at Embry-Riddle Aeronautical University.
            
            """

            # For scintillation data, get rid of non-sense values (e.g. values above a value of 5).
            # These values may come from errors in the receiver/computer or signal interferencies and
            # are not representative of S4/sigma scintillation values.
            if model.graph_type in model.scintillation_data_types:
                times_data = times_data[times_data[model.graph_type] <= 5]

            # TEC detrending (High-rate TEC data).
            if model.TEC_detrending and (model.file_type in model.raw_data_types):
                x_values, y_values = list(times_data[model.times_column_name]), list(times_data[model.graph_type])
                times_data[model.graph_type] = tec_detrending(x_values, y_values)

            # Night-subtraction and vertical TEC (for low-rate TEC data only).
            #### UPDATES HERE AS OF DEC 13 #### TO-DO NEXT: SPLIT VERTICAL TEC FROM NORMALIZATION.
            if model.file_type == "REDTEC":

                # When normalize==0 (regular data), select the minimum value.
                if not model.night_subtraction:

                    # After FOR LOOP  runs completely for the first time, it will calculate the
                    # minimum TEC value from ALL PRNs.
                    minimumvalueyaxis = min(float(s) for s in yaxiscolumn)
                    if minimumvalueyaxis < model.minimum:
                        model.minimum = minimumvalueyaxis

                # When normalize==1 (i.e. when FOR LOOP B runs for the second time):
                elif model.night_subtraction:
                    yaxiscolumn = slant_to_vertical_tec(yaxiscolumn, elevations, model.minimum,
                                                        vertical_tec=model.verticaltec)

            # Convert times to UTC.
            yaxiscolumn = [float(e) for e in yaxiscolumn]
            times = seconds_to_utc(times)

            # If the user is doing a summary plot add the shift value to every element in the
            # listforyaxisflt vector. See Section 1.
            if model.summaryplot:
                yaxiscolumn = [z + (prn * model.shiftvalue) for z in yaxiscolumn]

            # Determine the signal type (L1, L2, ETC).
            signal_types = {"G": {"1": "L1CA", "4": "L2Y", "5": "L2C", "6": "L2P", "7": "L5Q"},
                            "R": {"1": "L1CA", "3": "L2CA", "4": "L2P"},
                            "E": {"1": "E1", "2": "E5A", "3": "E5B", "4": "AltBOC"}}
            sttp = signal_types[prn[0]][str(signal_type)]

            # Name the plot.
            graph_name, directory, title, subtitle = naming(prn, sttp, normalize, i, model)

            # Plot.
            if len(yaxiscolumn) != 0:
                plot(times, yaxiscolumn, directory, graph_name, title, subtitle, model)


# ----------- GRAPHING ------------ #
def run_graphing(model):
    # Print start message to terminal.
    print("\n\n# --- " + model.file_type + ": Plotting Time vs. " + model.graph_type + " --- #")
    print('Date (year, month, day): {}, {}, {}'.format(model.date[0], model.date[1], model.date[2]))

    # Add a folder the output directory.
    model.output_dir = model.output_dir + filesep + model.get_date_str()
    print(model.output_dir)

    # Generate plots for the given date and PRNs.
    for prn in model.PRNs_to_plot:
        plot_prn(model, prn)

# Temporary.
# m = GraphSettings()
# m.date = [2020, 8, 2]
# m.PRNs_to_plot = ['G1']
# m.output_dir = r'C:\Users\nicol\Desktop\Research Local Files\EISA_OUTPUT\RX1\GRAPHS'
# m.CSV_dir = r'C:\Users\nicol\Desktop\Research Local Files\EISA_OUTPUT\RX1\CSVFILES'
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
