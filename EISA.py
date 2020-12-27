# 2019
# Embry-Riddle Aeronautical University
# Department of Physics and Life Sciences
#
# Code developer: Nicolas Gachancipa
#
# Embry-Riddle Ionospheric Algorithm (EISA) 2.0
# Ionospheric and TEC data collector
#
# Last time updated: Spring 2020.

# Imports.
from datetime import datetime, timedelta
from EISA_objects import GraphSettings, ParseSettings
from Graphing.Graphing import run_graphing
import os
import pandas as pd
from Parsing.Parsing import run_parsing
import shutil
import time

cwd = os.getcwd()  # Current working directory.
filesep = os.sep  # File separator (Changes between windows, linux and other OS).


# ----- Part 1: Parse ----- #
def parse(days_before, receivers, constellations):
    print("\n---------------------------------------------------------------------")
    # Run iteratively for every receiver.
    for receiver_name in receivers:
        # Print a message.
        date = datetime.today() - timedelta(days_before)
        print("Receiver: ", receiver_name, "  Date: ({}, {}, {})".format(date.year, date.month, date.day))

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

        # Parse.
        run_parsing(parameters, cwd + filesep + "Parsing")


# ----- Part 2: Graph ----- #
def graph(days_before, receivers, constellations, threshold, location):
    print("\n---------------------------------------------------------------------")
    # Run iteratively for every receiver.
    for receiver_name in receivers:

        # Run the graphing tool only if the csvfiles exist.
        date = datetime.today() - timedelta(days_before)
        year, month, day = str(date.year), str(date.month), str(date.day)
        if len(month) == 1:
            month = "0" + month
        if len(day) == 1:
            day = "0" + day
        date = year + month + day

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


# ----- Part 3: Upload ----- #


# ----- run_EISA function ------ #
def run_EISA(parameters='EISA_parameters.csv'):
    # Get times.
    now = datetime.today()  # Today's date and time.
    utc_time = datetime.utcnow()  # UTC time.

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

    # Print a message with the current time and date.
    print("\nCurrent local date/time: ", now)
    print("Current UTC date/time: {}.".format(utc_time))

    # Set the time at which the code will run (the time given by the user).
    if run_now:
        # Add two seconds to give the code time to run before starting to parse.
        time_plus_2 = now + timedelta(seconds=2)
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

        # If days_before is larger than 1, process the next day immediately. Otherwise, start a timer to run
        # the code again tomorrow. Note: even if the user does not select the 'run now' option, EISA will run
        # immediately if the selected date is before yesterday.
        if days_before > 1:
            # parse(days_before, receivers, constellations)
            graph(days_before, receivers, constellations, threshold, location)
            days_before -= 1
        else:
            # Print a message showing the user at what time the code will run again.
            print("\nThe code will parse (and plot) the data at:", next_run, "local time.")
            print("DO NOT CLOSE THIS WINDOW")

            # Run the loop again after parsing the files of the day before.
            time.sleep(secs)

            # Parse (after the timer ends).
            # parse(days_before, receivers, constellations)
            graph(days_before, receivers, constellations, threshold, location)
