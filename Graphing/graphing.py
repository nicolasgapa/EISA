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
import matplotlib.pyplot as plt
import pandas as pd
import os

# Internal imports.
from Graphing.support_graphing_functions import (time_ranges, tec_detrending, slant_to_vertical_tec, naming, plot,
                                                 times_to_filter_df)

# Set the file separator to work in both Linux and Windows.
filesep = os.sep


# Functions.
def plot_prn(model, prn, shift=0):
    """
    Function to plot the data of a satellite (prn) with the settings in a given GraphSettings model.

    :param model: (GraphSettings) A GraphSettings model. Refer to the EISA_objects file, GraphSettings class.
    :param prn: (str) The satellite. E.g. G1 for GPS 1, or R5 for GLONASS 5.
    :param shift: (int) Vertical shift (Useful for summary plots).
    :return: success (boolean): Whether the plot is created successfully (True) or not (False).
             error (str): Error message if success=False. None if success == True.
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
    if model.file_type in ['RAWTEC', 'RAWOBS', 'DETOBS']:
        reduced_file = model.CSV_dir + filesep + model.get_date_str() + filesep + "REDTEC" + "_" + prn + "_" + \
                       model.get_date_str() + ".csv"
        if not os.path.isfile(reduced_file):
            return False, "Could not find the REDTEC file corresponding to the raw data: {}.".format(reduced_file)
    else:
        reduced_file = csv_file

    # If the file can't be found, show an error message.
    if not os.path.isfile(csv_file):
        return False, ("The {} CSV data for the following PRN does not exist: {}. It can't be found in the specified "
                       "directory: {}.".format(model.file_type, prn, csv_file))

    # Identify the time ranges in which the satellite is above the given threshold. The start_times array indicates
    # the times at which the satellite crosses the threshold and is gaining elevation, while the end_times array
    # contains the times at which the satellite cross the threshold moving downwards (towards the horizon line).
    # Each pair of start-end times is the range of time in which the satellite was above the threshold.
    start_times, end_times = time_ranges(reduced_file, threshold=model.threshold,
                                         elev_col_name=model.elevation_column_name,
                                         times_col_name=model.times_column_name)
    if not start_times:
        return False, ('Either all the values of the following PRN are below the elevation threshold, or the CSV file '
                       'is empty: {}.'.format(prn))
    """

    Section: Data pre-processing.
    Purpose: Filter the dataset to only include the corresponding columns: Time, elevation, signal type, and the 
             graph type selected by the user (the parameter that will be plotted, e.g. Azimuth or TEC15). 

    """
    # Import and read the csv (if it exists).
    if not os.path.isfile(csv_file):
        return "The following directory does not exist: {}.".format(csv_file)

    # Open the CSV file.
    DF = pd.read_csv(csv_file)

    # Apply the elevation threshold.
    if model.file_type in ['RAWTEC', 'RAWOBS', 'DETOBS']:
        filtered_DF = times_to_filter_df(DF, start_times, end_times)
    else:
        filtered_DF = DF[DF[model.elevation_column_name] >= model.threshold]

    # Obtain the following columns: Time, elevation, signal type, and graph type (i.e. what you want to plot).
    # For RAW files, discard the elevation column, since the values were already filtered for the threshold in
    # the previous step. Moreover, if the user wants to plot the elevation, only save the elevation column
    # once under the 'graph_type' column.
    if model.file_type in ['RAWTEC', 'RAWOBS', 'DETOBS'] or model.elevation_column_name == model.graph_type:
        filtered_DF = filtered_DF[[model.times_column_name, model.signal_column_name, model.graph_type]]
    else:
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

            # If the dataset is empty, continue with the next time range (break out of the loop).
            if len(list(data[model.graph_type])) == 0:
                continue

            """
            
            Subsection: Other features
            Purpose: Post-data processing, including TEC detrending, night-subtraction (normalization), TEC 
            slant-to-vertical conversion, and ionospheric event detection using machine learning.
            
            CREDITS: The Butterworth filter used for TEC detrending was based on a Matlab function written by 
            Dr. Kshitija Deshpande, Professor of Engineering Physics at Embry-Riddle Aeronautical University.
            
            """

            # For low-rate scintillation data, get rid of non-sense values (e.g. values above a value of 5).
            # These values may come from errors in the receiver/computer or signal interference and are not
            # representative of S4/sigma scintillation values.
            if model.graph_type in model.scintillation_types:
                data = data[data[model.graph_type] <= 5]

            # High-rate TEC processing:
            if (model.file_type == 'RAWTEC') and (model.graph_type in model.TEC_types):

                # TEC detrending (High-rate TEC data).
                if model.TEC_detrending:
                    x_values, y_values = list(data[model.times_column_name]), list(data[model.graph_type])
                    data[model.graph_type] = tec_detrending(x_values, y_values)

            # Low-rate TEC processing.
            if (model.file_type == 'REDTEC') and (model.graph_type in model.TEC_types):

                # Vertical TEC conversion (Low-rate TEC data).
                if model.vertical_TEC:
                    y_values, elevations = list(data[model.graph_type]), list(data[model.elevation_column_name])
                    data[model.graph_type] = slant_to_vertical_tec(y_values, elevations)

                # Night subtraction (Low-rate TEC individual plots). For summary plots, the normalization
                # step is done after all PRNs are processed.
                if model.night_subtraction and not model.summary_plot:
                    # Update the y-values.
                    y_values = data[model.graph_type]
                    data[model.graph_type] = y_values - min(y_values)

            # Shift value.
            if shift != 0:
                data[model.graph_type] = data[model.graph_type] + shift

            """
            
            Subsection: Final edits and plot.
            Purpose: Convert times to UTC, define the graph name, and plot.
            
            """

            # Convert times (in seconds) to UTC (in hours).
            data[model.times_column_name] = [(float(i) % 86400) / 3600 for i in data[model.times_column_name]]

            # Determine the signal type (L1, L2, ETC).
            signal_type_name = model.signal_types[prn[0]][str(signal_type)]

            # Name the plot.
            graph_name, title, subtitle = naming(prn, signal_type_name, model.date, time_period=i,
                                                 file_type=model.file_type, graph_type=model.graph_type,
                                                 summary_plot=model.summary_plot,
                                                 night_subtraction=model.night_subtraction,
                                                 vertical_TEC=model.vertical_TEC, threshold=model.threshold,
                                                 location=model.location)

            # Plot and save the figure. Plot only if the dataframe is not empty. If the plot is a raw data plot, reduce
            # the line width.
            x_values, y_values = list(data[model.times_column_name]), list(data[model.graph_type])
            if model.file_type in ['RAWTEC', 'RAWOBS', 'DETOBS']:
                reduce_line_width = True
            else:
                reduce_line_width = False
            prn_plot = plot(x_values, y_values, prn, title, subtitle, summary_plot=model.summary_plot,
                            legend=model.legend, label_prns=model.label_prns,
                            graph_type=model.graph_type, title_font_size=model.title_font_size,
                            subtitle_font_size=model.subtitle_font_size,
                            set_x_axis_range=model.set_x_axis_range, set_y_axis_range=model.set_y_axis_range,
                            x_axis_start_value=model.x_axis_start_value,
                            x_axis_final_value=model.x_axis_final_value,
                            y_axis_start_value=model.y_axis_start_value,
                            y_axis_final_value=model.y_axis_final_value, vertical_line=model.vertical_line,
                            x_value_vertical_line=model.x_value_vertical_line,
                            units=model.units[model.graph_type], reduce_line_width=reduce_line_width)

            # If the summary plot option is NOT selected, save, show and clear the graph.
            if not model.summary_plot:

                # Set the output directory, and create it if it does not exist.
                directory = model.output_dir + filesep + model.graph_type
                if not os.path.exists(directory):
                    os.makedirs(directory)
                directory += filesep + graph_name + '.' + model.format_type

                # Print the directory in the command window.
                print('Saving plot: {}. PRN: {}.'.format(directory, prn))

                # Save the figure.
                prn_plot.savefig(directory)

                # Show the plot before clearing (if applicable).
                if model.show_plots:
                    prn_plot.show()

                # Clear the plot.
                prn_plot.clf()

        # Break out of the loop if the user chose to plot only one signal per PRN.
        if model.one_plot_per_prn:
            break

    # Return Success.
    return True, 'The plots for PRN {} have been processed.'.format(prn)


# ----------- GRAPHING ------------ #
def run_graphing(model, output_dir):
    """
    Run graphing.

    :param model: (GraphSettings) Graph settings model.
    :param output_dir: (str) Output directory.
    """
    # Print start message to terminal.
    if model.summary_plot:
        constellation_names = {'G': 'GPS', 'R': 'GLONASS', 'E': 'GALILEO'}
        constellations = [constellation_names[c] for c in list(set([prn[0] for prn in model.PRNs_to_plot]))]
        print("\n\n# --- " + model.file_type + " - Summary plot: Plotting Time vs. " + model.graph_type + " --- #")
        print("Creating summary plot - Constellations: {}.".format(', '.join(constellations)))
    else:
        print("\n\n# --- " + model.file_type + ": Plotting Time vs. " + model.graph_type + " --- #")
    print('Date (year, month, day): {}, {}, {}'.format(model.date[0], model.date[1], model.date[2]))

    # Set the output directory.
    model.output_dir = output_dir

    # Generate plots for the given date and PRNs.
    unsuccessful_prns = []
    for prn in model.PRNs_to_plot:

        # Plot.
        success, error_msg = plot_prn(model, prn)

        # Show a message if there is an error.
        if not success:
            if not model.summary_plot:
                print(error_msg)
            else:
                unsuccessful_prns.append(prn)

    # Summary plot post-processing.
    if model.summary_plot:

        # Update y-values for night-subtraction (if selected).
        if model.night_subtraction:

            # Find the minimum value in the plot.
            min_value = min([min(line.get_ydata()) for line in plt.gca().get_lines()])

            # Clear plot.
            plt.clf()

            # Repeat the process with a shift value: Generate plots for the given date and PRNs.
            unsuccessful_prns = []
            for prn in model.PRNs_to_plot:

                # Plot.
                success, error_msg = plot_prn(model, prn, shift=-min_value)

                # Show a message if there is an error.
                if not success:
                    unsuccessful_prns.append(prn)

        # Print summary.
        if unsuccessful_prns:
            print('The following PRNs were not included in the summary plot, because the CSV files were either '
                  'empty or all the data was below the elevation threshold: \n {}.'.format(
                  ','.join(unsuccessful_prns)))
        print('The following summary plot was created: {}.'.format(model.graph_type))

        # Obtain the name of the plot.
        graph_name, _, _ = naming(model.PRNs_to_plot[0], None, model.date, file_type=model.file_type,
                                  graph_type=model.graph_type, summary_plot=model.summary_plot,
                                  night_subtraction=model.night_subtraction, vertical_TEC=model.vertical_TEC,
                                  threshold=model.threshold, location=model.location)

        # Save the plot. Create the output directory if it doesn't exist.
        file_type = "TEC" if model.file_type in ["REDTEC", 'RAWTEC'] else "OBS"
        directory = model.output_dir + filesep + "Summary_Plots" + filesep + file_type
        if not os.path.exists(directory):
            os.makedirs(directory)
        directory += filesep + graph_name + '.' + model.format_type
        plt.savefig(directory)

        # Show the summary plot (if applicable).
        if model.show_plots:
            plt.show()

    # Clean plt.
    plt.clf()
