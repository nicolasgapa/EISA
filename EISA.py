# Import libraries
import os
from datetime import datetime, timedelta
from threading import Timer
import time
import csv
import shutil

now = datetime.today()  # Today's date and time.
cwd = os.getcwd()  # Current working directory.
filesep = os.sep  # File separator (Changes between windows, linux and other OS).

#
# 2019
# Embry-Riddle Aeronautical University
# Department of Physics and Life Sciences
#
# Code developer: Jose Nicolas Gachancipa
#
# Embry-Riddle Ionospheric Algorithm (EISA)
# Ionospheric and TEC data collector
#
# Last time updated: August 27th, 2020.
#


# ------------ Inputs ------------ #
# Insert the receiver name.
receivers = ["RX1"]

# '1' for yesterday. "2" for the day before yesterday, etc.
days_before = 38

# Set run_now to 1 if you want EISA to run now, rather than at a certain time.
# Set run_now to 0 if you want EISA to run at a certain time every day.
run_now = 1

# Local time + UTC_delta = UTC time
UTC_delta = 4

# Elevation threshold.
elevation_threshold = 30

# Receiver location. 
receiver_location = "Daytona Beach, FL"

# At what time would you like the code to run every day?
# Only valid if run_now is not equal to 1.
# EG: hour = 4, minute = 30, second = 30 : Will run at 04:30:30 every day.
if run_now != 1:
    hour, minute, second = 4, 0, 0
# --------------------------------- #

# --------------------------------- #
# EISA.
# DO NOT CHANGE ANYTHING BELOW THIS UNLESS YOU KNOW WHAT YOU ARE DOING.
# --------------------------------- #

# Set the time to now if run_now = 1.
else:
    hour, minute, second = now.hour, now.minute, now.second + 2

# Print a message with the current time and date.
print("\nCurrent date/time: ", now)

# Set the time at which the code will run (the time given bu the user).
time_to_run = now.replace(day=now.day, hour=hour, minute=minute,
                          second=second, microsecond=0)

# If that time has already passed today, add a day (the code will run tomorrow
# at that time).
if time_to_run < now:
    time_to_run = now.replace(day=now.day + 1, hour=hour, minute=minute,
                              second=second, microsecond=0)

# Print a message showing the user at what time the code will run.
print("The code will parse the data again at:", time_to_run, "local time.")
print("DO NOT CLOSE THIS WINDOW")


# ----- Part 1: Parse ----- #
def parse():
    # Run iteratively for every receiver in the folder:
    for receiver_name in receivers:

        # Print a message.
        print("\n\nReceiver: ", receiver_name, "  Date:", datetime.today() - timedelta(days_before))
        print("\n--------------------------- Step 1: Parse ---------------------------")

        # Identify the directory to the parsing.py file.
        parsing_directory = cwd + filesep + "Parsing" + filesep
        os.chdir(parsing_directory)

        # Open the settings.csv file and edit every row.
        with open("Settings.csv") as csvfile:
            read_csv = csv.reader(csvfile, delimiter=',')
            count = 1

            newcsv = []
            # Edit the rows.
            for row in read_csv:
                if count == 2:
                    # Split the cwd into words.
                    cwd_split_directory = (cwd.split(filesep))
                    # Get rid of the last folder (EISA), since the binary files are located outside this folder.
                    cwd_split_directory = cwd_split_directory[:-1]
                    # Enter the receiver's folder.
                    cwd_split_directory.append(receiver_name)
                    add_line = cwd_split_directory
                elif count == 4:
                    # Set the parsing code directory.
                    add_line = (parsing_directory.split(filesep))
                elif count == 6:
                    # Only reduced data when running EISA.
                    add_line = ['1']
                elif count == 8:
                    # Split the cwd into words.
                    cwd_split_directory = (cwd.split(filesep))
                    # CSV files output directory.EISA_OUTPUT
                    cwd_split_directory[-1] = "EISA_OUTPUT"
                    cwd_split_directory.append(receiver_name)
                    cwd_split_directory.append("CSVFILES")
                    add_line = cwd_split_directory
                elif count == 10:
                    # Parse data for all constellations when running parsing.py
                    # add_line = ['G', 'R', 'E']
                    add_line = ['G', 'R', 'E']
                elif count == 12:
                    # All PRNs.
                    # add_line = ['T']
                    add_line = ['T']
                elif count == 17:
                    # Receiver name from user input.
                    add_line = [receiver_name]
                elif count == 19:
                    # Year
                    local_date = datetime.today()
                    local_year = local_date.year
                    add_line = [local_year]
                elif count == 21:
                    # Initial date (YESTERDAY!)
                    yesterday = datetime.today() - timedelta(days_before)
                    add_line = [yesterday.month, yesterday.day]
                elif count == 23:
                    # Final date (ALSO YESTERDAY!)
                    yesterday = datetime.today() - timedelta(days_before)
                    add_line = [yesterday.month, yesterday.day]
                else:
                    add_line = row
                newcsv.append(add_line)
                count += 1

        with open("Settings.csv", "w+", newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(newcsv)

        # Run the parsing.py file.
        os.system("py parsing.py")

        # Now, proceed to step 3: Graphing.
        graph(receiver_name)

    # Print a message at the end.
    parse_end_time = datetime.today()
    print("\n\nCurrent date/time: ", parse_end_time)
    parse_end_time = parse_end_time.replace(day=parse_end_time.day + 1, hour=hour, minute=minute,
                                            second=second, microsecond=0)
    print("The code will parse the data again at:", parse_end_time, "local time.")


# ----- Part 2: Graph ----- #
def graphsettings(data_type, elev_threshold, constellations, satellites, summary_plot, normalize_tec, x_axisrange,
                  y_axisrange, prn_label, legends, vertical_lines, vertical_tec, only_one_signal, graph_format,
                  title_size, location):
    # Open the graphsettings.csv file and edit every row respectively (For REDOBS).
    with open("GRAPHSETTINGS.csv") as csvfile:
        read_csv = csv.reader(csvfile, delimiter=',')
        count = 1
        newcsv = []

        # Edit the rows.
        for row in read_csv:
            if count == 2:
                # Type of data being plotted.
                add_line = data_type
            elif count == 4:
                # Elevation threshold.
                add_line = [elev_threshold]
            elif count == 6:
                # Plot data for all constellations.
                add_line = constellations
            elif count == 8:
                # Plot data for all satellites.
                add_line = satellites
            elif count == 10:
                # Initial date (YESTERDAY == 1)
                yesterday = datetime.today() - timedelta(days_before)
                add_line = [yesterday.month, yesterday.day]
            elif count == 12:
                # Final date (ALSO YESTERDAY == 1)
                yesterday = datetime.today() - timedelta(days_before)
                add_line = [yesterday.month, yesterday.day]
            elif count == 14:
                # Year
                local_date = datetime.today()
                local_year = local_date.year
                add_line = [local_year]
            elif count == 16:
                # Summary Plot
                add_line = summary_plot
            elif count == 18:
                add_line = normalize_tec
            elif count == 20:
                # No specific range for the x axis.
                add_line = x_axisrange
            elif count == 21:
                # No specific range for the y axis.
                add_line = y_axisrange
            elif count == 25:
                # Label each PRN number on the graph.
                add_line = prn_label
            elif count == 27:
                # Legends nest to the graph.
                add_line = legends
            elif count == 29:
                # Vertical lines across the graph.
                add_line = vertical_lines
            elif count == 31:
                # Vertical TEC.
                add_line = vertical_tec
            elif count == 33:
                # Only one signal per PRN
                add_line = only_one_signal
            elif count == 35:
                # png format
                add_line = graph_format
            elif count == 37:
                # Plot title/subtitle size.
                add_line = title_size
            elif count == 39:
                # Location
                add_line = [location]
            else:
                add_line = row
            count = count + 1
            newcsv.append(add_line)

    # Modify the csv file.
    with open("GRAPHSETTINGS.csv", "w+", newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(newcsv)


def graph(receiver):
    # Print message.
    print("--------------------------- Step 2: Graph ---------------------------")
    graphormat = '.png'

    # Identify the directory to the graphing.py file.
    graphing_directory = cwd + filesep + "Graphing" + filesep
    os.chdir(graphing_directory)

    # Open the PATHS.csv file and edit every row respectively.
    with open("PATHS.csv") as csvfile:
        read_csv = csv.reader(csvfile, delimiter=',')
        count = 1
        newcsv = []

        # Edit the rows.
        for row in read_csv:
            if count == 2:
                # Path to CSV files
                # Split the cwd into words.
                cwd_split_directory = (cwd.split(filesep))

                # Get rid of the last folder (EISA), since the CSV files are located outside this folder.
                add_line = cwd_split_directory[0:-1]
                add_line.append("EISA_OUTPUT")
                add_line.append(receiver)
                add_line.append("CSVFILES")
                csvfiles_location = add_line
            elif count == 4:
                # Set the parsing code directory.
                add_line = cwd_split_directory[0:-1]
                add_line.append("EISA_OUTPUT")
                add_line.append(receiver)
                add_line.append("GRAPHS")
            else:
                add_line = row
            count = count + 1
            newcsv.append(add_line)

    # Modify the csv file.
    with open("PATHS.csv", "w+", newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(newcsv)

    # Define the three constellations (GPS, GLONASS, and GALILEO)
    constellations = ['G', 'R', 'E']

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
        while count <= 13:
            for constellation in constellations:

                if count in [7, 8]:
                    yaxis = ['1', '0', '1']
                # For 1secsigma through 60secsigma, set the y axis range from 0 to 0.4.
                elif 9 <= count <= 13:
                    yaxis = ['1', '0', '0.8']
                else:
                    yaxis = ['0', '0', '0']

                # Individual plots.
                graphsettings(["RED", "OBS"], elevation_threshold, [constellation], ["T"], ['0', '0'], ['0'],
                              ['0', '0', '0'], yaxis, ['0'], ['0'], ['0', '0'], ['0'], ['0'], [graphormat], ['12', '12'],
                              receiver_location)

                # Run the graphing.py file.
                os.system("py graphing.py no_menu " + str(count))
            count = count + 1

        # Summary plots. Save them to a different folder.
        valid_categories = [2, 7, 8, 9, 10, 11, 12, 13]
        for count in valid_categories:
            for constellation in constellations:
                if count == 7 or count == 8:
                    summaryplot_settings = [1, 0.05]
                    onlyonesignal_settings = ['1']
                elif count == 2:
                    summaryplot_settings = [1, 0]
                    onlyonesignal_settings = ['0']
                else:
                    summaryplot_settings = [1, 0]
                    onlyonesignal_settings = ['1']

                # Individual plots.
                graphsettings(["RED", "OBS"], elevation_threshold, [constellation], ["T"], summaryplot_settings, ['0'],
                              ['0', '0', '0'],
                              ['0', '0', '0'], ['1'], ['0'], ['0', '0'], ['0'], onlyonesignal_settings, [graphormat],
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
# At 4 am, everyday, parse the files created on the previous day, and create the graphs.
eternalloop = 1
while eternalloop == 1:
    # Determine the current date and time.
    x = datetime.today()

    # Modify the date and time. Run the code every day at the same time.
    y = x.replace(day=x.day + 1, hour=hour, minute=minute, second=second,
                  microsecond=0)

    # Compute the time left for the next iteration to occur (in seconds).
    delta_t = y - x
    secs = delta_t.seconds + 1

    # If days_before is larger than 1, process the next day immediately. Otherwise, start a timer to run
    # the code again tomorrow.
    if days_before > 1:
        parse()
        days_before -= 1
    else:
        # Initiate a timer. The script will run the parse function when the timer stops.
        t = Timer(secs, parse)
        t.start()

        # Run the loop again after parsing the files of the day before.
        time.sleep(secs)
