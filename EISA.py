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
import os
import pandas as pd
import shutil
from threading import Timer
import time

cwd = os.getcwd()  # Current working directory.
filesep = os.sep  # File separator (Changes between windows, linux and other OS).


# ----- Part 1: Parse ----- #
def parse():
    print("\n\n---------------------------------------------------------------------")
    # Run iteratively for every receiver in the folder:
    for receiver_name in receivers:
        # Print a message.
        print("Receiver: ", receiver_name, "  Date:", datetime.today() - timedelta(days_before))
        print("--------------------------- Step 1: Parse ---------------------------")

        # Identify the directory to the Parsing.py file.
        parsing_directory = cwd + filesep + "Parsing" + filesep
        os.chdir(parsing_directory)

        # Run the Parsing.py file.
        os.system("py Parsing.py")

        # Now, proceed to step 3: Graphing.
        # graph(receiver_name)

    # Print a message at the end.
    parse_end_time = datetime.today()
    print("Current date/time: ", parse_end_time)
    parse_end_time = parse_end_time.replace(day=parse_end_time.day + 1, hour=hour, minute=minute,
                                            second=second, microsecond=0)
    print("The code will parse the data again at:", parse_end_time, "local time.")
    print("---------------------------------------------------------------------")


# ----- Part 2: Graph ----- #
def graph(receiver):
    # Print message.
    print("--------------------------- Step 2: Graph ---------------------------")
    graphormat = '.png'

    # Identify the directory to the graphing.py file.
    graphing_directory = cwd + filesep + "Graphing" + filesep
    os.chdir(graphing_directory)

    # Define the three constellations (GPS, GLONASS, and GALILEO)
    constellations = ['G']  # , 'R', 'E']

    # Run the graphing tool only if the csvfiles exist.
    yesterday = datetime.today() - timedelta(days_before)
    if len(str(yesterday.month)) == 1:
        month = "0" + str(yesterday.month)
    else:
        month = str(yesterday.month)
    if len(str(yesterday.day)) == 1:
        day = "0" + str(yesterday.day)
    else:
        day = str(yesterday.day)
    location = ""
    for u in csvfiles_location:
        location = location + u + filesep
    print(location + str(yesterday.year) + month + day)
    if os.path.exists(location + str(yesterday.year) + month + day):

        # REDUCED SCINTILLATION (REDOBS)
        # count = 1: Azimuth, count = 2: Elevation, count = 3: CNo, count = 4: Lock Time, count = 5: CMC avg,
        # count = 6: CMC std, count = 7: S4, count = 8: S4 Cor, count = 9: 1secsigma, count = 10: 3secsigma
        # count = 11: 10secsigma, count = 12: 30secsigma, count = 13: 60secsigma.
        # Individual plots.
        count = 1
        while count <= 1:
            for constellation in constellations:

                if count in [7, 8]:
                    yaxis = ['1', '0', '0.8']
                # For 1secsigma through 60secsigma, set the y axis range from 0 to 0.4.
                elif 9 <= count <= 13:
                    yaxis = ['1', '0', '0.8']
                else:
                    yaxis = ['0', '0', '0']

                # Individual plots.
                graphsettings(["RED", "OBS"], elevation_threshold, [constellation], ["T"], ['0', '0'], ['0'],
                              ['0', '0', '0'], yaxis, ['0'], ['0'], ['0', '0'], ['0'], ['0'], [graphormat],
                              ['12', '12'], receiver_location)

                # Run the graphing.py file.
                os.system("py graphing.py no_menu " + str(count))
            count = count + 1

        ## Summary plots. Save them to a different folder.
        valid_categories = [2, 7, 8, 9, 10, 11, 12, 13]
        for count in valid_categories:
            for constellation in constellations:
                onlyonesignal_settings = ['1']
                yaxis = ['0', '0', '0']
                plabel = ['0']

                if count == 2:
                    plabel = ['1']

                if count >= 7:
                    yaxis = ['1', '0', '0.8']

                # Summary plots.
                graphsettings(["RED", "OBS"], elevation_threshold, [constellation], ["T"], ["1", "0"], ['0'],
                              ['0', '0', '0'],
                              yaxis, plabel, ['0'], ['0', '0'], ['0'], onlyonesignal_settings, [graphormat],
                              ['12', '12'],
                              receiver_location)

                # Run the graphing.py code.
                os.system("py Graphing.py no_menu " + str(count))

        # REDUCED TOTAL ELECTRON CONTENT (REDTEC)
        # count = 1: Azimuth, count = 2: Elevation, count = 3: CNo, count = 4: Lock Time, count = 5: CMC avg,
        # count = 6: CMC std, count = 7: S4, count = 8: S4 Cor, count = 9: 1secsigma, count = 10: 3secsigma
        # count = 11: 10secsigma, count = 12: 30secsigma.
        # Individual TEC plots.
        valid_categories = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        for count in valid_categories:
            for constellation in constellations:
                # Individual plots.
                graphsettings(["RED", "TEC"], elevation_threshold, [constellation], ["T"], ['0', '0'], ['0'],
                              ['0', '0', '0'],
                              ['0', '0', '0'], ['0'], ['0'], ['0', '0'], ['0'], ['0'], [graphormat], ['12', '12'],
                              receiver_location)

                # Run the graphing.py file.
                os.system("py Graphing.py no_menu " + str(count))

        # TEC Summary plots. Save them to a different folder.
        valid_categories = [5, 7, 9, 11]
        for count in valid_categories:
            for constellation in constellations:

                normalize = [0, 1]
                for i in normalize:
                    if i == 0:
                        # Summary plots.
                        graphsettings(["RED", "TEC"], elevation_threshold, [constellation], ["T"], [1, 0], ['0'],
                                      ['0', '0', '0'], ['0', '0', '0'], ['1'], ['0'], ['0', '0'], ['0'], ['0'],
                                      [graphormat], ['12', '12'], receiver_location)

                        # Run the graphing.py file.
                        os.system("py Graphing.py no_menu " + str(count))
                    elif i == 1:
                        vertical_tec = [0, 1]
                        for j in vertical_tec:
                            # Summary plots.
                            graphsettings(["RED", "TEC"], elevation_threshold, [constellation], ["T"], [1, 0], ['1'],
                                          ['0', '0', '0'], ['0', '0', '0'], ['1'], ['0'], ['0', '0'], [str(j)], ['0'],
                                          [graphormat], ['12', '12'], receiver_location)

                            # Run the graphing.py file.
                            os.system("py Graphing.py no_menu " + str(count))

        # Make a zip file of the graphs folder for that date. Save it to the graphs folder in EISA_OUTPUT
        # (include the receiver name in the zip file name).
        collected_data_date = datetime.today() - timedelta(days_before)
        year = str(collected_data_date.year)
        month = str(collected_data_date.month)
        day = str(collected_data_date.day)
        if len(month) != 2:
            month = "0" + str(month)
        if len(day) != 2:
            day = "0" + str(day)
        zipfile_name = year + month + day + "_" + receiver
        dir_name = cwd + filesep + os.pardir + filesep + "EISA_OUTPUT" + filesep + receiver + filesep + "GRAPHS" + filesep + year + month + day
        shutil.make_archive(dir_name + filesep + os.pardir + filesep + zipfile_name, 'zip', dir_name)

    # If the csv files for that day don't exist, print a message.
    else:
        print("CSVfiles for the following date do not exist: ", str(yesterday.year), str(month), str(day),
              " - Receiver:", receiver)


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

    # Print a message with the current time and date.
    print("\nCurrent date/time: ", now)

    # Set the time at which the code will run (the time given by the user).
    if run_now:
        hour, minute, second = now.hour, now.minute, now.second + 2
    else:
        hour, minute, second = start_time[0], start_time[1], 0
    time_to_run = now.replace(day=now.day, hour=hour, minute=minute, second=second, microsecond=0)

    # If that time has already passed today, add a day (the code will run tomorrow at that time).
    if time_to_run < now:
        time_to_run = now.replace(day=now.day + 1, hour=hour, minute=minute, second=second, microsecond=0)

    # Set the start date, using the days_before variable.
    print(start_today)
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

    # Print a message showing the user at what time the code will run.
    print("The code will parse the data at:", time_to_run, "local time.")
    print("DO NOT CLOSE THIS WINDOW")

    # At the same time everyday (time_to_run), parse the files created on the previous day, and create the graphs.
    eternal_loop = True
    while eternal_loop:
        # Determine the current date and time.
        x = datetime.today()

        # Modify the date and time. Run the code every day at the same time.
        y = x.replace(day=x.day + 1, hour=hour, minute=minute, second=second, microsecond=0)

        # Compute the time left for the next iteration to occur (in seconds).
        delta_t = y - x
        secs = delta_t.seconds + 1
        print(secs)

        # Parse.
        # parse
        print('PARSE', days_before)

        # If days_before is larger than 1, process the next day immediately. Otherwise, start a timer to run
        # the code again tomorrow.
        if days_before > 1:
            days_before -= 1
        else:
            # Initiate a timer. The script will run the parse function when the timer stops.
            t = Timer(secs, parse)
            t.start()

            # Run the loop again after parsing the files of the day before.
            time.sleep(secs)
