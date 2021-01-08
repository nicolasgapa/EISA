"""
2019
Embry-Riddle Aeronautical University
Department of Physics and Life Sciences

Code developer: Nicolas Gachancipa

Embry-Riddle Ionospheric Scintillation Algorithm (EISA) 2.0
Ionospheric and TEC data collector

Last time updated: Spring 2020.
"""

# Imports.
from datetime import datetime, timedelta
from EISA_objects import GraphSettings, ParseSettings
from gnsscal import date2gpswd
from Graphing.Graphing import run_graphing
import os
import pandas as pd
from Parsing.Parsing import run_parsing
from ML.neural_network import run_ML, NNModel
import shutil
import textwrap
import time

cwd = os.getcwd()  # Current working directory.
filesep = os.sep  # File separator (Changes between windows, linux and other OS).


# Functions.
def days_before_to_date(days_before):
    # Run the graphing tool only if the csvfiles exist.
    date = datetime.today() - timedelta(days_before)
    year, month, day = str(date.year), str(date.month), str(date.day)
    if len(month) == 1:
        month = "0" + month
    if len(day) == 1:
        day = "0" + day
    date = year + month + day
    return date


# ----- Part 1: Parse ----- #
def parse(days_before, receivers, constellations):
    # Run iteratively for every receiver.
    for receiver_name in receivers:
        # Print a message.
        date = (datetime.today() - timedelta(days_before)).date()

        # Define PRNs.
        PRNs_to_parse = []
        if 'G' in constellations:
            PRNs_to_parse.extend(['G' + str(i) for i in range(1, 33)])
        if 'R' in constellations:
            PRNs_to_parse.extend(['R' + str(i) for i in range(1, 25)])
        if 'E' in constellations:
            PRNs_to_parse.extend(['E' + str(i) for i in range(1, 31)])

        # Define parsing parameters.
        parameters = ParseSettings()
        parameters.binary_dir = os.path.abspath(os.path.join(cwd, os.pardir)) + '\\' + receiver_name
        parameters.CSV_dir = os.path.abspath(os.path.join(cwd, os.pardir)) + r'\EISA_OUTPUT\{}\CSV_FILES'.format(
            receiver_name)
        parameters.receiver_name = receiver_name
        parameters.date_range = False
        parameters.start_date = [date.year, date.month, date.day]
        parameters.end_date = [date.year, date.month, date.day]
        parameters.reduced = True
        parameters.raw = False
        parameters.PRNs_to_parse = PRNs_to_parse
        parameters.set_time_range = False

        # Binary dir and file.
        binary_file = str(date2gpswd(date)[0]) + '_' + str(date2gpswd(date)[1]) + '_00_' + receiver_name + '.GPS'
        binary_dir = parameters.binary_dir + filesep + str(date2gpswd(date)[0]) + filesep + binary_file

        # If the binary file exists, parse.
        if os.path.exists(binary_dir):
            # Print status to command window.
            print("\n---------------------------------------------------------------------")
            print("PART 1: EISA PARSING. Receiver: {}. Date: ({}, {}, {})\n".format(receiver_name, date.year,
                                                                                    date.month, date.day))

            # Parse.
            run_parsing(parameters, cwd + filesep + "Parsing")
        else:
            print("The binary file for the following date does not exist: {}. Receiver: {}.".format(binary_dir,
                                                                                                    receiver_name))


# ----- Part 2: Graph ----- #
def graph(days_before, receivers, constellations, threshold, location):
    # Run iteratively for every receiver.
    for receiver_name in receivers:

        # Determine the date.
        date = days_before_to_date(days_before)
        year, month, day = date[:4], date[4:6], date[6:]

        # Set graphing parameters.
        parameters = GraphSettings()
        parameters.CSV_dir = os.path.abspath(
            os.path.join(os.getcwd(), os.pardir)) + r'\EISA_OUTPUT\{}\CSV_FILES'.format(receiver_name)
        parameters.date = [year, month, day]
        parameters.threshold = threshold

        # Other plot options.
        parameters.location = location
        parameters.summary_plot = False
        parameters.TEC_detrending = False
        parameters.night_subtraction = False
        parameters.vertical_TEC = False
        parameters.one_plot_per_prn = True

        # Plot visual settings.
        parameters.set_x_axis_range = False
        parameters.set_y_axis_range = False
        parameters.vertical_line = False
        parameters.label_prns = False
        parameters.legend = False
        parameters.format_type = 'png'
        parameters.show_plots = False

        # Define output directory, with date.
        output_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir)) + r'\EISA_OUTPUT\{}\GRAPHS'.format(
            receiver_name)
        output_dir += filesep + parameters.get_date_str()

        # Define PRNs.
        PRNs_to_plot = []
        if 'G' in constellations:
            PRNs_to_plot.extend(['G' + str(i) for i in range(1, 33)])
        if 'R' in constellations:
            PRNs_to_plot.extend(['R' + str(i) for i in range(1, 25)])
        if 'E' in constellations:
            PRNs_to_plot.extend(['E' + str(i) for i in range(1, 31)])
        GPS_satellites = [prn for prn in PRNs_to_plot if prn[0] == 'G']
        GLONASS_satellites = [prn for prn in PRNs_to_plot if prn[0] == 'R']
        GALILEO_satellites = [prn for prn in PRNs_to_plot if prn[0] == 'E']
        parameters.PRNs_to_plot = PRNs_to_plot

        # Continue only if the files of the corresponding date exist.
        if os.path.exists(parameters.CSV_dir + filesep + date):

            # Print status to command window.
            print("\n---------------------------------------------------------------------")
            print("PART 2: EISA GRAPHING. Receiver: {}. Date: ({}, {}, {})\n".format(receiver_name, year, month, day))

            # REDUCED SCINTILLATION (REDOBS): Individual plots.
            parameters.file_type = 'REDOBS'
            for graph_type in parameters.graph_types_REDOBS:

                # Define the file type and parameters.
                parameters.graph_type = graph_type
                parameters.one_plot_per_prn = False

                # Define the y axis range.
                if graph_type in parameters.scintillation_types:
                    parameters.set_y_axis_range = True
                    parameters.y_axis_start_value = 0
                    parameters.y_axis_end_value = 0.8
                else:
                    parameters.set_y_axis_range = False

                # Plot.
                run_graphing(parameters, output_dir)

            # Scintillation summary plots. Save them to a different folder.
            parameters.summary_plot = True
            for graph_type in ['Elevation'] + parameters.scintillation_types:

                # Create a summary plot per constellation.
                for satellites in [GPS_satellites, GLONASS_satellites, GALILEO_satellites]:

                    # Define file type and parameters.
                    parameters.PRNs_to_plot = satellites
                    parameters.graph_type = graph_type
                    parameters.one_plot_per_prn = True
                    parameters.label_prns = True

                    # Define the y axis range.
                    if graph_type in parameters.scintillation_types:
                        parameters.set_y_axis_range = True
                        parameters.y_axis_start_value = 0
                        parameters.y_axis_end_value = 0.8
                        parameters.label_prns = False
                    else:
                        parameters.set_y_axis_range = False
                        parameters.label_prns = True

                    # Plot.
                    run_graphing(parameters, output_dir)

            # REDUCED TOTAL ELECTRON CONTENT (REDTEC)
            parameters.file_type = 'REDTEC'
            parameters.summary_plot = False
            for graph_type in parameters.graph_types_REDTEC[2:]:
                # Set parameters.
                parameters.graph_type = graph_type
                parameters.set_y_axis_range = False
                parameters.one_plot_per_prn = False
                parameters.label_prns = False

                # Plot.
                run_graphing(parameters, output_dir)

            # TEC Summary plots. Save them to a different folder.
            parameters.summary_plot = True
            for graph_type in ['TEC15', 'TEC30', 'TEC45', 'TECTOW']:

                # Create a summary plot per constellation.
                for satellites in [GPS_satellites, GLONASS_satellites, GALILEO_satellites]:
                    # Set parameters.
                    parameters.PRNs_to_plot = satellites
                    parameters.graph_type = graph_type
                    parameters.label_prns = True

                    # Normal.
                    run_graphing(parameters, output_dir)

                    # Normalized (night subtraction).
                    parameters.night_subtraction = True
                    run_graphing(parameters, output_dir)

                    # Vertical TEC.
                    parameters.night_subtraction = False
                    parameters.vertical_TEC = True
                    run_graphing(parameters, output_dir)

                    # Normalized AND vertical TEC.
                    parameters.night_subtraction = True
                    run_graphing(parameters, output_dir)

            # Make a zip file of the graphs folder for that receiver and date. Save it to the graphs folder in
            # EISA_OUTPUT (include the receiver name in the zip file name).
            zip_file_name = date + "_" + receiver_name
            dir_name = cwd + filesep + os.pardir + filesep + "EISA_OUTPUT"
            dir_name += filesep + receiver_name + filesep + "GRAPHS" + filesep + date
            shutil.make_archive(dir_name + filesep + os.pardir + filesep + zip_file_name, 'zip', dir_name)

        # If the csv files for that day don't exist, print a message.
        else:
            print("CSV files for the following date do not exist: {}. Receiver: {}.".format(date, receiver_name))


# ----- Part 3: ML ----- #
def ML_event_detection(days_before, receivers, constellations, threshold, location):
    # Run iteratively for every receiver.
    for receiver_name in receivers:

        # Determine the date, CSV dir, and GRAPHS dir.
        date = days_before_to_date(days_before)
        year, month, day = date[:4], date[4:6], date[6:]

        CSV_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir)) + r'\EISA_OUTPUT\{}\CSV_FILES'.format(
            receiver_name)
        graphs_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir)) + r'\EISA_OUTPUT\{}\GRAPHS'.format(
            receiver_name)

        # Define PRNs.
        PRNs_to_process = []
        if 'G' in constellations:
            PRNs_to_process.extend(['G' + str(i) for i in range(1, 33)])
        if 'R' in constellations:
            PRNs_to_process.extend(['R' + str(i) for i in range(1, 25)])
        if 'E' in constellations:
            PRNs_to_process.extend(['E' + str(i) for i in range(1, 31)])

        # Continue only if the path containing the csv files of the corresponding date exists.
        if os.path.exists(CSV_dir + filesep + date):

            # Print status to command window.
            print("\n---------------------------------------------------------------------")
            print("PART 3: EISA ML MODULE. Receiver: {}. Date: ({}, {}, {})\n".format(receiver_name, year, month, day))

            # Create S4 Neural Network, and load the weights.
            S4_model = NNModel('S4')
            S4_model.load_weights('ML' + filesep + 's4_scintillation.h5')

            # Create sigma Neural Network, and load the weights.
            sigma_model = NNModel('sigma')
            sigma_model.load_weights('ML' + filesep + 'sigma_scintillation.h5')

            # Ionospheric scintillation detection.
            for prn in PRNs_to_process:
                # Files.
                input_file = CSV_dir + filesep + date + filesep + 'REDOBS_{}_{}.csv'.format(prn, date)
                output_file = CSV_dir + filesep + date + filesep + r'\ML_Detection\REDOBS_{}_{}_ML_Detection'.format(
                    prn, date)

                # Convert date to list format (which is the input format for the run_ML function).
                date_list = [date[:4], date[4:6], date[6:]]

                # Directory to the new (ML) plots.
                graphs_output_dir = graphs_dir + filesep + date + filesep + 'ML'

                # ML Detection: S4 scintillation.
                run_ML(input_file, output_file, S4_model, prn, date_list, scintillation_type='S4', save_plot=True,
                       save_plot_dir=graphs_output_dir + filesep + 'Amplitude', threshold=threshold, location=location,
                       save_events_only=True)

                # ML Detection: sigma scintillation.
                run_ML(input_file, output_file, sigma_model, prn, date_list, scintillation_type='sigma',
                       save_plot=True, save_plot_dir=graphs_output_dir + filesep + 'Phase', threshold=threshold,
                       location=location, save_events_only=True)


# ----- Part 4: Upload ----- #


# ----- run_EISA function ------ #
def run_EISA(parameters='EISA_parameters.csv'):
    # Get times.
    now = datetime.today()  # Today's date and time.
    utc_time = datetime.utcnow()  # UTC time.

    # Print command window header.
    print(textwrap.dedent("""\n
                          ----------------------------------
                          EMBRY-RIDDLE AERONAUTICAL UNIVERSITY
                          Department of Physical Sciences
                          Space Physics Research Laboratory (SPRL)
                          Embry-Riddle Ionospheric Scintillation Algorithm (EISA)
                          Version 2.0
                          Current local date/time: {}
                          Current UTC date/time: {}.
                          ----------------------------------\n
                          """.format(now, utc_time)))

    # Open the settings file.
    DF = pd.read_csv(parameters).values

    # Extract inputs.
    start_today = False if int(DF[0][0]) == 0 else True
    start_date = [int(i) for i in DF[2][:3]]
    run_now = False if int(DF[4][0]) == 0 else True
    start_time = [int(i) for i in DF[6][:2]]
    receivers = [str(i) for i in DF[8] if str(i) != 'nan']
    threshold = int(DF[10][0])
    location = str(DF[12][0])
    constellations = [str(i) for i in DF[14] if str(i) != 'nan']

    # Set the time at which the code will run (the time given by the user).
    if run_now:
        # Add one second to give the code time to run before starting to parse.
        time_plus_2 = now + timedelta(seconds=1)
        hour, minute, second = time_plus_2.hour, time_plus_2.minute, time_plus_2.second
    else:
        hour, minute, second = start_time[0], start_time[1], 0
    time_to_run = now.replace(day=now.day, hour=hour, minute=minute, second=second, microsecond=0)

    # Set the start date, using the days_before variable.
    if start_today:
        # Binary files containing today's data are generated by the receiver at 23:59 UTC. Therefore, if the
        # 'start from today' option is selected, and the selected time is before 23:59 UTC, EISA will start by
        # parsing the data from yesterday (days_before = 1).
        if now <= (now.replace(hour=23, minute=59, second=59) - (utc_time - now)):
            days_before = 1
        else:
            days_before = 0
    else:
        # Find the difference (in days) between the input date, and today.
        dif = now - datetime(year=start_date[0], month=start_date[1], day=start_date[2], hour=now.hour,
                             minute=now.minute, second=now.second, microsecond=0)
        days_before = dif.days

    # At the same time everyday (time_to_run), parse the files created on the previous day, and create the graphs.
    eternal_loop = True
    while eternal_loop:
        # Determine the current date and time.
        now = datetime.today()

        # Modify the date and time. Run the code every day at the same time.
        next_run = now.replace(day=now.day, hour=time_to_run.hour, minute=time_to_run.minute,
                               second=time_to_run.second, microsecond=0)
        if now >= next_run:
            next_run = now.replace(day=now.day + 1, hour=time_to_run.hour, minute=time_to_run.minute,
                                   second=time_to_run.second, microsecond=0)

        # Compute the time left for the next iteration to occur (in seconds).
        secs = (next_run - now).seconds + 1

        # Parse, plot, process, and upload.
        parse(days_before, receivers, constellations)
        graph(days_before, receivers, constellations, threshold, location)
        ML_event_detection(days_before, receivers, constellations, threshold, location)

        # If days_before is larger than 1, process the next day immediately. Otherwise, start a timer to run
        # the code again tomorrow. Note: even if the user does not select the 'run now' option, EISA will run
        # immediately if the selected date is before yesterday.
        if (days_before > 1) or (
                days_before == 1 and now > (now.replace(hour=23, minute=59, second=59) - (utc_time - now))):
            days_before -= 1
        else:
            # Print a message showing the user at what time the code will run again.
            print("\nThe code will parse (and plot) the data at:", next_run, "local time.")
            print("DO NOT CLOSE THIS WINDOW")

            # Run the loop again after parsing the files of the day before.
            time.sleep(secs)
