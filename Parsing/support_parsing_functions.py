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
import os
import subprocess

filesep = os.sep


def parse_file(binary_file, file_type, exe_dir, model):
    # Obtain directory to the exe parsing files.
    if file_type == 'reduced':
        exe_file = exe_dir + r'\ParseReduced.exe'
    elif file_type == 'raw':
        exe_file = exe_dir + r'\ParseRaw.exe'
    else:
        return False, "File type must be defined: Either 'reduced' or 'raw'"

    # Obtain week number and directory to file.
    week_number = int(binary_file[:4])
    day_number = int(binary_file[5])
    binary_dir = model.binary_dir + filesep + str(week_number) + filesep + binary_file

    # TODO: FIX - constellationandprns = '-'
    for satellite in model.PRNs_to_parse:

        # Obtain the command to run in the exe.
        CSV_name = binary_file + "_" + satellite + ".csv"
        exe_command = satellite + " " + binary_dir + " " + CSV_name

        # For raw files only: If the user selects a specific period of time to parse, add the parameter to the command.
        if model.set_time_range:
            start_time_GPS_TOW = day_number * 86400 + model.time_start_value * 3600
            end_time_GPS_TOW = day_number * 86400 + model.time_end_value * 3600
            exe_command = exe_command + " " + str(start_time_GPS_TOW) + " " + str(end_time_GPS_TOW)

        # Parse the file by running the command.
        print(exe_file + ' ' + exe_command)
        subprocess.call(r"C:\Users\nicol\Desktop\Research_Local_Files\EISA\Parsing\ParseReduced.exe G1 C:\Users\nicol\Desktop\Research_Local_Files\RX1\2119\2119_6_00_RX1.GPS 2119_6_00_RX1.GPS_G1.csv")

#       if file_type == "reduced":  # Open the .csv file and divide it by dates.
#           rangenumber = 2
#       elif file_type == "raw":
#           rangenumber = 3
#       for selection in range(rangenumber):
#           if file_type == "reduced":  # Set the name of the .CSV file.
#               if selection == 0:
#                   x = "REDTEC_" + CSV_name
#                   y = "REDTEC"
#               elif selection == 1:
#                   x = "REDOBS_" + CSV_name
#                   y = "REDOBS"
#           elif file_type == "raw":
#               if selection == 0:
#                   x = "ismRawTec_" + CSV_name
#                   y = "RAWTEC"
#               elif selection == 1:
#                   x = "ismRawObs_" + CSV_name
#                   y = "RAWOBS"
#               elif selection == 2:
#                   x = "ismDetObs_" + CSV_name
#                   y = "DETOBS"
#           x = codedirectory + x  # Modify the file name once again to include the folder path.
#           toremove = x  #
#           forlateruse = 0
#           if os.path.exists(x):
#               forlateruse = 1
#               # Assign a variable number depending on the filetype. This number represents
#               # the first row of the csv file with data (first row that is not the heading).
#               # Different files have different header lengths.
#               variable = 1
#               with open(x) as csvfile:
#                   readCSV = csv.reader(csvfile, delimiter=',')
#                   # Create an empty vector that will collect the first column of the
#                   # csv files (with a for loop). This column represents the time
#                   # (in seconds) at which every datapoint was collected.
#                   times = []  # First, identify if the row is empty. If it is, replace it with
#                   for row in readCSV:
#                       time = row[0]
#                       times.append(time)
#
#               lentimes = len(
#                   times)  # Calculate the length of the vector that gathers all the times. This length
#               savelength = lentimes  # value will be modified further into this code, but the original value will
#               forcomparison = variable - 1  # also be used later (save it into a variable called savelengh).
#               if len(
#                       times) > 1:  # Discard the .csv files that are empty. Just run the rest of the program if the files have data.
#                   timeswoheading = times[
#                                    variable:lentimes]  # Create a vector that cuts off the heading of the times vector.
#                   timesflt = []  # Convert all the strings in timeswoheading to float values.
#                   timesflt = [float(i) for i in timeswoheading]
#                   firstsecond = timesflt[
#                       0]  # Select the first number of the list to identify when the data was collected
#                   if firstsecond < 86400:  # for the first time (day of the week).
#                       firstday = "Sunday"
#                       firsteval = [0, 86400]
#                       rownumber = 0
#                   elif 86400 <= firstsecond < 172800:
#                       firstday = "Monday"
#                       firsteval = [86400, 172800]
#                       rownumber = 1
#                   elif 172800 <= firstsecond < 259200:
#                       firstday = "Tuesday"
#                       firsteval = [172800, 259200]
#                       rownumber = 2
#                   elif 259200 <= firstsecond < 345600:
#                       firstday = "Wednesday"
#                       firsteval = [259200, 345600]
#                       rownumber = 3
#                   elif 345600 <= firstsecond < 432000:
#                       firstday = "Thursday"
#                       firsteval = [345600, 432000]
#                       rownumber = 4
#                   elif 432000 <= firstsecond < 518400:
#                       firstday = "Friday"
#                       firsteval = [432000, 518400]
#                       rownumber = 5
#                   elif 518400 <= firstsecond < 604800:
#                       firstday = "Saturday"
#                       firsteval = [518400, 604800]
#                       rownumber = 6
#                   start = firsteval[0]
#                   end = firsteval[1]
#                   name = "GPSCALENDAR.csv"
#                   with open(name) as csvfile:
#                       readCSV = csv.reader(csvfile, delimiter=',')
#                       yearlist = []
#                       monthlist = []
#                       daylist = []
#                       dayoftheyearlist = []
#                       dayoftheweeklist = []
#                       weeklist = []
#                       for row in readCSV:
#                           year = row[0]
#                           month = row[1]
#                           day = row[2]
#                           dayoftheyear = row[3]
#                           dayoftheweek = row[4]
#                           week = row[5]
#                           yearlist.append(year)
#                           monthlist.append(month)
#                           daylist.append(day)
#                           dayoftheyearlist.append(dayoftheyear)
#                           dayoftheweeklist.append(dayoftheweek)
#                           weeklist.append(week)
#                   weeklistint = []  # Convert the week numbers to integers, so they can be compared to the
#                   for item in weeklist:  # week number from the csv file.
#                       weeklistint.append(int(item))  #
#                   weekpositions = []  # Compare each item in the week list to the week number. Identify which
#                   csvcolumn = (i for i, item in enumerate(weeklistint) if
#                                item == week_number)  # rows in the GPScalendar file correspond to the week number. Then,
#                   for i in csvcolumn:  # read the row to select the date (day, year, month etc).
#                       weekpositions.append(i)
#                   csvrownumber = weekpositions[rownumber]
#                   daynumber = int(daylist[csvrownumber])
#                   yearnumber = int(yearlist[csvrownumber])
#                   monthnumber = int(monthlist[csvrownumber])
#                   if monthnumber == 1:  # Change the month number to its corresponding name.
#                       monthname = "January"
#                   elif monthnumber == 2:
#                       monthname = "February"
#                   elif monthnumber == 3:
#                       monthname = "March"
#                   elif monthnumber == 4:
#                       monthname = "April"
#                   elif monthnumber == 5:
#                       monthname = "May"
#                   elif monthnumber == 6:
#                       monthname = "June"
#                   elif monthnumber == 7:
#                       monthname = "July"
#                   elif monthnumber == 8:
#                       monthname = "August"
#                   elif monthnumber == 9:
#                       monthname = "September"
#                   elif monthnumber == 10:
#                       monthname = "October"
#                   elif monthnumber == 11:
#                       monthname = "November"
#                   elif monthnumber == 12:
#                       monthname = "December"
#                   day1 = []  # This section will read through the variables collected earlier in this
#                   selection = (i for i, item in enumerate(timesflt) if
#                                item >= start and item < end)  # code and will identify the corresponding lines in the csv file for
#                   for i in selection:  # each date. The first part corresponds to the first day of the data, and
#                       day1.append(
#                           i)  # the second part consists of a while loop that will repeat until all the
#                   lenday1 = len(day1)  # rows in the csv file are read.
#                   timesflt = timesflt[
#                              lenday1:lentimes]  # The code will print the corresponding row numbers and dates after reading the
#                   if lenday1 == 0:  # file.
#                       beginning1 = 0  #
#                       end1 = 0  #
#                       stringtoprint = "There is no data for day 1."  #
#                       totallength = variable  #
#                   elif lenday1 != 0:  #
#                       beginning1 = variable  #
#                       end1 = lenday1 + variable  #
#                       stringtoprint = "Day 1 goes from cell " + str(beginning1) + " to cell " + str(
#                           end1) + ". (" + firstday + ", " + monthname + " " + str(
#                           daynumber) + ", " + str(
#                           yearnumber) + ")"
#                       totallength = end1  #
#                   with open(x) as csvfile:  #
#                       readCSV = csv.reader(csvfile, delimiter=',')  #
#                       day1toprint = []
#                       rowcount = 1
#                       for row in readCSV:
#                           if rowcount <= end1:
#                               day1toprint.append(row)
#                           rowcount = rowcount + 1
#                   if daynumber <= 9:  # Print the new csv file for day 1.
#                       daynumber = "0" + str(daynumber)
#                   if monthnumber <= 9:
#                       monthnumber = "0" + str(monthnumber)
#                   pathtoprint = CSVfilesdirectory + filesep + str(yearnumber) + str(
#                       monthnumber) + str(
#                       daynumber)
#                   if not os.path.exists(pathtoprint):
#                       os.makedirs(pathtoprint)
#                   csvfilename1 = pathtoprint + filesep + y + "_" + constellation + str(
#                       satellite) + "_" + str(yearnumber) + str(monthnumber) + str(daynumber) + ".csv"
#                   with open(csvfilename1, "w+", newline='') as csvfile:  #
#                       writer = csv.writer(csvfile)  #
#                       writer.writerows(day1toprint)  #
#                   firstdaycode = rownumber  # Do the same for all of the days.
#                   daycount = 2
#
#                   while totallength < savelength:
#                       if start == 518400:  #
#                           start = 0  #
#                           end = 86400  #
#                       else:  #
#                           start = start + 86400  #
#                           end = end + 86400  #
#                       day2 = []  #
#                       selection = (i for i, item in enumerate(timesflt) if
#                                    item >= start and item < end)
#                       for i in selection:
#                           day2.append(i)
#                       lenday2 = len(day2)
#                       lentimes = len(timesflt)
#                       timesflt = timesflt[lenday2:lentimes]
#                       if lenday2 == 0:
#                           beginning2 = 0
#                           end2 = 0
#                           stringtoprint = "There is no data for day " + str(daynumber) + "."
#                       elif lenday2 != 0:
#                           if totallength != variable:
#                               beginning2 = totallength + 1
#                           elif totallength == variable:
#                               beginning2 = totallength
#                           if firstdaycode != 6:
#                               firstdaycode = firstdaycode + 1
#                           elif firstdaycode == 6:
#                               firstdaycode = 0
#                           end2 = totallength + lenday2
#                           if firstdaycode == 0:
#                               firstday = "Sunday"
#                           elif firstdaycode == 1:
#                               firstday = "Monday"
#                           elif firstdaycode == 2:
#                               firstday = "Tuesday"
#                           elif firstdaycode == 3:
#                               firstday = "Wednesday"
#                           elif firstdaycode == 4:
#                               firstday = "Thursday"
#                           elif firstdaycode == 5:
#                               firstday = "Friday"
#                           elif firstdaycode == 6:
#                               firstday = "Saturday"
#                           m = csvrownumber + daycount - 1
#                           daynumber = int(daylist[m])
#                           yearnumber = int(yearlist[m])
#                           monthnumber = int(monthlist[m])
#                           if monthnumber == 1:  # Change the month name.
#                               monthname = "January"
#                           elif monthnumber == 2:
#                               monthname = "February"
#                           elif monthnumber == 3:
#                               monthname = "March"
#                           elif monthnumber == 4:
#                               monthname = "April"
#                           elif monthnumber == 5:
#                               monthname = "May"
#                           elif monthnumber == 6:
#                               monthname = "June"
#                           elif monthnumber == 7:
#                               monthname = "July"
#                           elif monthnumber == 8:
#                               monthname = "August"
#                           elif monthnumber == 9:
#                               monthname = "September"
#                           elif monthnumber == 10:
#                               monthname = "October"
#                           elif monthnumber == 11:
#                               monthname = "November"
#                           elif monthnumber == 12:
#                               monthname = "December"
#                           stringtoprint = "Day " + str(daycount) + " goes from cell " + str(
#                               beginning2) + " to cell " + str(
#                               end2) + ". (" + firstday + ", " + monthname + " " + str(
#                               daynumber) + ", " + str(yearnumber) + ")"
#                           with open(x) as csvfile:  #
#                               readCSV = csv.reader(csvfile, delimiter=',')  #
#                               header = []  #
#                               rowcount = 1  #
#                               for row in readCSV:  #
#                                   if rowcount < variable:  #
#                                       header.append(row)  #
#                                   rowcount = rowcount + 1
#                           with open(x) as csvfile:  #
#                               readCSV = csv.reader(csvfile, delimiter=',')  #
#                               daytoprintwoheader = []
#                               rowcount = 1
#                               for row in readCSV:
#                                   if beginning2 <= rowcount <= end2:
#                                       daytoprintwoheader.append(row)
#                                   rowcount = rowcount + 1
#                               daytoprint = header + daytoprintwoheader
#                           if daynumber <= 9:
#                               daynumber = "0" + str(daynumber)
#                           if monthnumber <= 9:
#                               monthnumber = "0" + str(monthnumber)
#                           pathtoprint = CSVfilesdirectory + filesep + str(yearnumber) + str(
#                               monthnumber) + str(daynumber)
#                           if not os.path.exists(pathtoprint):
#                               os.makedirs(pathtoprint)
#                           csvfilename = pathtoprint + filesep + y + "_" + constellation + str(
#                               satellite) + "_" + str(yearnumber) + str(monthnumber) + str(
#                               daynumber) + ".csv"
#                           with open(csvfilename, "w+",
#                                     newline='') as csvfile:  # Create the new csvfile.
#                               writer = csv.writer(csvfile)
#                               writer.writerows(daytoprint)
#                           totallength = end2
#                       daycount = daycount + 1
#               os.remove(toremove)  # Remove miscelanous files.
#       countt = countt + 1
# prnlist = ': '
# elementcount = 1
# for element in PRNs:
#     if 1 < len(PRNs) != elementcount:
#         prnlist = prnlist + str(element) + ', '
#     elif len(PRNs) == 1 or elementcount == len(PRNs):
#         prnlist = prnlist + str(element) + '. '
#     elementcount = elementcount + 1
# if constellation == 'G':
#     constellationname = 'GPS'
# elif constellation == 'R':
#     constellationname = 'GLONASS'
# elif constellation == 'E':
#     constellationname = 'GALILEO'
# constellationandprns = constellationandprns + constellationname + ' ' + str(prnlist)
# if forlateruse == 1:
#    done = 'The following data was parsed: ' + filetorun + '. Date: ' + str(monthnumber) + ' ' + str(
#        daynumber) + ', ' + str(yearnumber) + '. ' + constellationandprns
#    printmatrix.append(done)  # Print status.
        return False, 'Fail'
