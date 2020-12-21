"""

Embry-Riddle Ionospheric Scintillation Algorithm (EISA)
Version 2
Support functions (Parsing)

Embry-Riddle Aeronautical University
Department of Physical Sciences
Space Physics Research Lab (SPRL)
Author: Nicolas Gachancipa

"""
# Imports.
import math
import os
import pandas as pd
import subprocess

filesep = os.sep


def parse_file(binary_file, reduced_or_raw, exe_dir, model):
    # Obtain directory to the exe parsing files.
    if reduced_or_raw == 'reduced':
        exe_file = exe_dir + filesep + 'ParseReduced.exe'
        file_types = ['REDTEC', 'REDOBS']
    elif reduced_or_raw == 'raw':
        exe_file = exe_dir + filesep + 'ParseRaw.exe'
        file_types = ['ismRawTec', 'ismRawObs', 'ismDetObs']
    else:
        return False, "File type must be defined: Either 'reduced' or 'raw'"

    # Obtain week number and directory to file.
    week_number = int(binary_file[:4])
    day_number = int(binary_file[5])
    binary_dir = model.binary_dir + filesep + str(week_number)

    # TODO: FIX - constellationandprns = '-'
    for satellite in model.PRNs_to_parse:

        # Obtain the command to run in the exe.
        CSV_name = binary_file + "_" + satellite + ".csv"
        exe_command = satellite + " " + binary_dir + filesep + binary_file + " " + CSV_name

        # For raw files only: If the user selects a specific period of time to parse, add the parameter to the command.
        if model.set_time_range:
            start_time_GPS_TOW = day_number * 86400 + model.time_start_value * 3600
            end_time_GPS_TOW = day_number * 86400 + model.time_end_value * 3600
            exe_command = exe_command + " " + str(start_time_GPS_TOW) + " " + str(end_time_GPS_TOW)

        # Parse the file by running the command.
        # subprocess.call(exe_file + ' ' + exe_command)

        # Process each of the file types (e.g. REDTEC and REDOBS for reduced files).
        ys = {'ismRawTec': 'RAWTEC', 'ismRawObs': 'RAWOBS', 'ismDetObs': 'DETOBS'}
        for file_type in file_types:
            csv_file = file_type + '_' + CSV_name
            y = csv_file
            if reduced_or_raw == 'raw':
                y = ys[file_type]
            csv_file = exe_dir + filesep + csv_file

            # Process the csv file (if it exists).
            print('here', csv_file)
            if os.path.exists(csv_file):
                # Open the CSV file.
                DF = pd.read_csv(csv_file)

                # If the DF is empty, return an error msg.
                if len(DF) == 0:
                    return False, 'The following file was discarded, because it was empty: {}.'.format(CSV_name)

                # Extract the times column.
                times = DF[model.times_column_name].astype(float)
                first_second = times.iloc[0]
                week_day = math.floor(first_second/86400)

                savelength = len(times)
                if firstsecond < 86400:  # for the first time (day of the week).
                    firstday = "Sunday"
                    rownumber = 0
                elif 86400 <= firstsecond < 172800:
                    firstday = "Monday"
                    rownumber = 1
                elif 172800 <= firstsecond < 259200:
                    firstday = "Tuesday"
                    rownumber = 2
                elif 259200 <= firstsecond < 345600:
                    firstday = "Wednesday"
                    rownumber = 3
                elif 345600 <= firstsecond < 432000:
                    firstday = "Thursday"
                    rownumber = 4
                elif 432000 <= firstsecond < 518400:
                    firstday = "Friday"
                    rownumber = 5
                elif 518400 <= firstsecond < 604800:
                    firstday = "Saturday"
                    rownumber = 6
                start = week_day*86400
                end = start + 86400
                name = "GPSCALENDAR.csv"
                with open(name) as csvfile:
                    readCSV = csv.reader(csvfile, delimiter=',')
                    yearlist = []
                    monthlist = []
                    daylist = []
                    dayoftheyearlist = []
                    dayoftheweeklist = []
                    weeklist = []
                    for row in readCSV:
                        year = row[0]
                        month = row[1]
                        day = row[2]
                        dayoftheyear = row[3]
                        dayoftheweek = row[4]
                        week = row[5]
                        yearlist.append(year)
                        monthlist.append(month)
                        daylist.append(day)
                        dayoftheyearlist.append(dayoftheyear)
                        dayoftheweeklist.append(dayoftheweek)
                        weeklist.append(week)
                weeklistint = []  # Convert the week numbers to integers, so they can be compared to the
                for item in weeklist:  # week number from the csv file.
                    weeklistint.append(int(item))  #
                weekpositions = []  # Compare each item in the week list to the week number. Identify which
                csvcolumn = (i for i, item in enumerate(weeklistint) if
                             item == week_number)  # rows in the GPScalendar file correspond to the week number. Then,
                for i in csvcolumn:  # read the row to select the date (day, year, month etc).
                    weekpositions.append(i)
                csvrownumber = weekpositions[rownumber]
                daynumber = int(daylist[csvrownumber])
                yearnumber = int(yearlist[csvrownumber])
                monthnumber = int(monthlist[csvrownumber])
                if monthnumber == 1:  # Change the month number to its corresponding name.
                    monthname = "January"
                elif monthnumber == 2:
                    monthname = "February"
                elif monthnumber == 3:
                    monthname = "March"
                elif monthnumber == 4:
                    monthname = "April"
                elif monthnumber == 5:
                    monthname = "May"
                elif monthnumber == 6:
                    monthname = "June"
                elif monthnumber == 7:
                    monthname = "July"
                elif monthnumber == 8:
                    monthname = "August"
                elif monthnumber == 9:
                    monthname = "September"
                elif monthnumber == 10:
                    monthname = "October"
                elif monthnumber == 11:
                    monthname = "November"
                elif monthnumber == 12:
                    monthname = "December"
                day1 = []  # This section will read through the variables collected earlier in this
                selection = (i for i, item in enumerate(timesflt) if
                             item >= start and item < end)  # code and will identify the corresponding lines in the csv file for
                for i in selection:  # each date. The first part corresponds to the first day of the data, and
                    day1.append(
                        i)  # the second part consists of a while loop that will repeat until all the
                lenday1 = len(day1)  # rows in the csv file are read.
                timesflt = timesflt[
                           lenday1:lentimes]  # The code will print the corresponding row numbers and dates after reading the
                if lenday1 == 0:  # file.
                    beginning1 = 0
                    end1 = 0  #
                    stringtoprint = "There is no data for day 1."
                    totallength = 1
                elif lenday1 != 0:
                    beginning1 = 1
                    end1 = lenday1 + 1
                    stringtoprint = "Day 1 goes from cell " + str(beginning1) + " to cell " + str(
                        end1) + ". (" + firstday + ", " + monthname + " " + str(
                        daynumber) + ", " + str(
                        yearnumber) + ")"
                    totallength = end1  #
                with open(x) as csvfile:  #
                    readCSV = csv.reader(csvfile, delimiter=',')  #
                    day1toprint = []
                    rowcount = 1
                    for row in readCSV:
                        if rowcount <= end1:
                            day1toprint.append(row)
                        rowcount = rowcount + 1
                if daynumber <= 9:  # Print the new csv file for day 1.
                    daynumber = "0" + str(daynumber)
                if monthnumber <= 9:
                    monthnumber = "0" + str(monthnumber)
                pathtoprint = CSVfilesdirectory + filesep + str(yearnumber) + str(
                    monthnumber) + str(
                    daynumber)
                if not os.path.exists(pathtoprint):
                    os.makedirs(pathtoprint)
                csvfilename1 = pathtoprint + filesep + y + "_" + constellation + str(
                    satellite) + "_" + str(yearnumber) + str(monthnumber) + str(daynumber) + ".csv"
                with open(csvfilename1, "w+", newline='') as csvfile:  #
                    writer = csv.writer(csvfile)  #
                    writer.writerows(day1toprint)  #
                firstdaycode = rownumber  # Do the same for all of the days.
                daycount = 2

                while totallength < savelength:
                    if start == 518400:  #
                        start = 0  #
                        end = 86400  #
                    else:  #
                        start = start + 86400  #
                        end = end + 86400  #
                    day2 = []  #
                    selection = (i for i, item in enumerate(timesflt) if
                                 item >= start and item < end)
                    for i in selection:
                        day2.append(i)
                    lenday2 = len(day2)
                    lentimes = len(timesflt)
                    timesflt = timesflt[lenday2:lentimes]
                    if lenday2 == 0:
                        beginning2 = 0
                        end2 = 0
                        stringtoprint = "There is no data for day " + str(daynumber) + "."
                    elif lenday2 != 0:
                        if totallength != 1:
                            beginning2 = totallength + 1
                        elif totallength == 1:
                            beginning2 = totallength
                        if firstdaycode != 6:
                            firstdaycode = firstdaycode + 1
                        elif firstdaycode == 6:
                            firstdaycode = 0
                        end2 = totallength + lenday2
                        if firstdaycode == 0:
                            firstday = "Sunday"
                        elif firstdaycode == 1:
                            firstday = "Monday"
                        elif firstdaycode == 2:
                            firstday = "Tuesday"
                        elif firstdaycode == 3:
                            firstday = "Wednesday"
                        elif firstdaycode == 4:
                            firstday = "Thursday"
                        elif firstdaycode == 5:
                            firstday = "Friday"
                        elif firstdaycode == 6:
                            firstday = "Saturday"
                        m = csvrownumber + daycount - 1
                        daynumber = int(daylist[m])
                        yearnumber = int(yearlist[m])
                        monthnumber = int(monthlist[m])
                        if monthnumber == 1:  # Change the month name.
                            monthname = "January"
                        elif monthnumber == 2:
                            monthname = "February"
                        elif monthnumber == 3:
                            monthname = "March"
                        elif monthnumber == 4:
                            monthname = "April"
                        elif monthnumber == 5:
                            monthname = "May"
                        elif monthnumber == 6:
                            monthname = "June"
                        elif monthnumber == 7:
                            monthname = "July"
                        elif monthnumber == 8:
                            monthname = "August"
                        elif monthnumber == 9:
                            monthname = "September"
                        elif monthnumber == 10:
                            monthname = "October"
                        elif monthnumber == 11:
                            monthname = "November"
                        elif monthnumber == 12:
                            monthname = "December"
                        stringtoprint = "Day " + str(daycount) + " goes from cell " + str(
                            beginning2) + " to cell " + str(
                            end2) + ". (" + firstday + ", " + monthname + " " + str(
                            daynumber) + ", " + str(yearnumber) + ")"
                        with open(x) as csvfile:  #
                            readCSV = csv.reader(csvfile, delimiter=',')  #
                            header = []  #
                            rowcount = 1  #
                            for row in readCSV:  #
                                if rowcount < 1:  #
                                    header.append(row)  #
                                rowcount = rowcount + 1
                        with open(x) as csvfile:  #
                            readCSV = csv.reader(csvfile, delimiter=',')  #
                            daytoprintwoheader = []
                            rowcount = 1
                            for row in readCSV:
                                if beginning2 <= rowcount <= end2:
                                    daytoprintwoheader.append(row)
                                rowcount = rowcount + 1
                            daytoprint = header + daytoprintwoheader
                        if daynumber <= 9:
                            daynumber = "0" + str(daynumber)
                        if monthnumber <= 9:
                            monthnumber = "0" + str(monthnumber)
                        pathtoprint = CSVfilesdirectory + filesep + str(yearnumber) + str(
                            monthnumber) + str(daynumber)
                        if not os.path.exists(pathtoprint):
                            os.makedirs(pathtoprint)
                        csvfilename = pathtoprint + filesep + y + "_" + constellation + str(
                            satellite) + "_" + str(yearnumber) + str(monthnumber) + str(
                            daynumber) + ".csv"
                        with open(csvfilename, "w+",
                                  newline='') as csvfile:  # Create the new csvfile.
                            writer = csv.writer(csvfile)
                            writer.writerows(daytoprint)
                        totallength = end2
                    daycount = daycount + 1
                os.remove(x)  # Remove miscelanous files.
        # TODO: Print parsing review.
        return False, 'Fail'
