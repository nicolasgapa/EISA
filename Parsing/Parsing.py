# Import modules.
import os
import csv

import time

start_time = time.time()

# print("The purpose of this code is to convert .GPS binary files into readable .csv files.")
# print("To change the settings of the code, go to settings.csv.")
filesep = os.sep
filesep = '/'

# -------------------------------------------------------------------- #
# --------------------------- Read inputs ---------------------------- #
# -------------------------------------------------------------------- #
# Open the settings .csv file and read the rows.
with open("settings.csv") as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')

    # Count for every row. Identify all the inputs.
    count = 1
    for row in readCSV:
        if count == 2:
            # Set the path to binary files.
            pathtobinaryfilerow = row
            lengthpathbinary = len(pathtobinaryfilerow)
            binaryfiledirectory = ""
            for a in range(lengthpathbinary):
                toappendbinary = pathtobinaryfilerow[a]
                if len(toappendbinary) != 0:
                    toappendbinary = toappendbinary + filesep
                    binaryfiledirectory = binaryfiledirectory + toappendbinary
        if count == 4:
            pathtoparsingcode = row
            lengthparsingcode = len(pathtoparsingcode)
            parsingcodedirectory = ""
            for a in range(lengthparsingcode):
                toappendparsing = pathtoparsingcode[a]
                if len(toappendparsing) != 0:
                    toappendparsing = toappendparsing + filesep
                    parsingcodedirectory = parsingcodedirectory + toappendparsing
            codedirectory = parsingcodedirectory  # Save the path for later use.
        if count == 6:  # User selection (either parseraw, parsereduced, or both)
            selectionrawreduced = int(row[0])
        if count == 8:  # Folder where the csvfiles are going to be saved.
            pathtographsfolderrow = row
            lengthgraphspath = len(pathtographsfolderrow)
            CSVfilesdirectory = ""
            for a in range(lengthgraphspath):
                toappendbinary = pathtographsfolderrow[a]
                if len(toappendbinary) != 0:
                    toappendbinary = toappendbinary + filesep
                    CSVfilesdirectory = CSVfilesdirectory + toappendbinary
        if count == 10:  # Selected constellations.
            constellationstoparserow = row  #
            constellationstoparse = []  #
            for a in range(len(constellationstoparserow)):  #
                toappendconstellation = constellationstoparserow[a]  #
                if len(toappendconstellation) != 0:  #
                    constellationstoparse.append(toappendconstellation)  #
        if count == 12:  # Selected PRNs.
            PRNstoparserow = row
            PRNstoparse = []
            for a in range(len(PRNstoparserow)):
                toappendPRNs = PRNstoparserow[a]
                if len(toappendPRNs) != 0:
                    PRNstoparse.append(toappendPRNs)
        weekrollover = 0  # Selected times for parseraw.
        if count == 15:  #
            parserawtimes = row  #
            specifictimes = int(parserawtimes[0])  #
            if specifictimes == 1:  #
                starttime = parserawtimes[1]  #
                endtime = parserawtimes[2]  #
                if len(row) > 3:  #
                    weekrollover = 1  #
                    startweek = parserawtimes[3]  #
                    endweek = parserawtimes[4]  #
        if count == 17:  # Name of the receiver.
            receivername = row[0]
        if count == 19:
            yeari = row[0]
        if count == 21:  # Initial Date.
            monthi = str(row[0])  #
            dayi = str(row[1])  #
            if len(monthi) == 1:  #
                monthi = '0' + monthi  #
            if len(dayi) == 1:  #
                dayi = '0' + dayi  #
        if count == 23:  # Final Date.
            monthf = str(row[0])  #
            dayf = str(row[1])  #
            if len(monthf) == 1:  #
                monthf = '0' + monthf  #
            if len(dayf) == 1:  #
                dayf = '0' + dayf  #
        count += 1

# Create two matrices: day matrix and month matrix.
daymatrix = []
monthmatrix = []

# Each of these matrices has the days and the months withtin the selected range of dates respectively.
numberofmonths = int(monthf) - int(monthi)
monthcount = 0
rangea = numberofmonths + 1
if numberofmonths != 0:
    for month in range(rangea):  #
        if monthcount <= numberofmonths:  #
            if monthcount == 0:  #
                month = int(monthi)  #
            else:  #
                month = int(monthi) + monthcount  #
            if month in [1, 3, 5, 7, 8, 10, 12]:  #
                numofdays = 31;  #
            elif month in [4, 6, 9, 11]:  #
                numofdays = 30;  #
            elif month == 2:  #
                remainder = int(yeari) % 4  #
                if remainder == 0:  #
                    numofdays = 29  #
                else:  #
                    numofdays = 28  #
            if monthcount == 0:  #
                numofdays1 = numofdays - int(dayi)  #
            elif month != int(monthf):  #
                numofdays1 = numofdays  #
            else:  #
                numofdays1 = int(dayf)  #
            for day in range(numofdays1 + 1):  #
                if monthcount == 0:  #
                    daytoadd = int(dayi) + day  #
                    daymatrix.append(daytoadd)  #
                elif month != int(monthf):  #
                    if day != 0:  #
                        daytoadd = day  #
                        daymatrix.append(daytoadd)  #
                elif monthcount == numberofmonths:  #
                    if day <= int(dayf) and day != 0:  #
                        daytoadd = day  #
                        daymatrix.append(daytoadd)  #
                monthmatrix.append(month)  #
            monthcount += 1  #
elif numberofmonths == 0:
    month = monthi
    numberofdays = int(dayf) - int(dayi)
    for day in range(numberofdays + 1):
        daytoadd = day + int(dayi)
        monthmatrix.append(int(month))
        daymatrix.append(daytoadd)
# ---------------------------------------------------------------------------------------------------------------------#
# ---------------------------------------------------------------------------------------------------------------------#
# ---------------------------------------------------------------------------------------------------------------------#
# ---------------------------------------------------------------------------------------------------------------------#
# ---------------------------------------------------------- PARSING --------------------------------------------------#
howmanydays = len(daymatrix)
filestorun = []
weeknumbers = []
import csv

with open("GPSCALENDAR.csv") as csvfile:  # Determine the names of the binary files to be parsed.
    readCSV = csv.reader(csvfile, delimiter=',')  # and save them into a matrix called filestorun.
    for row in readCSV:  #
        counttwoo = 0  #
        fileyear = int(row[0])  #
        filemonth = int(row[1])  #
        fileday = int(row[2])  #
        for element in daymatrix:  #
            monthint = monthmatrix[(counttwoo)]  #
            dayint = element  #
            if fileyear == int(yeari) and filemonth == monthint and fileday == dayint:  #
                dayoftheweek = row[4]  #
                weeknumber = row[5]  #
                if dayoftheweek == 'Monday':  #
                    daycode = '_1_00_'  #
                elif dayoftheweek == 'Tuesday':  #
                    daycode = '_2_00_'  #
                elif dayoftheweek == 'Wednesday':  #
                    daycode = '_3_00_'  #
                elif dayoftheweek == 'Thursday':  #
                    daycode = '_4_00_'  #
                elif dayoftheweek == 'Friday':  #
                    daycode = '_5_00_'  #
                elif dayoftheweek == 'Saturday':  #
                    daycode = '_6_00_'  #
                elif dayoftheweek == 'Sunday':  #
                    daycode = '_0_00_'  #
                filetorun = str(weeknumber) + daycode + receivername + '.GPS'
                filestorun.append(filetorun)  #
                weeknumbers.append(weeknumber)  #
            counttwoo = counttwoo + 1  #
printmatrix = []
filecount = 1

for filetorun in filestorun:  # Start a for loop that will repeat for every csvfile.
    import os  #

    binaryfilename = filetorun  #
    weeknumber = weeknumbers[filecount - 1]  #
    readdirectory = binaryfiledirectory + weeknumber + filesep + binaryfilename  #
    if os.path.exists(readdirectory):  # Only if the file exists, continue parsing.
        if selectionrawreduced == 1 or selectionrawreduced == 2:  #
            runthecode = 1  # 1 time                                                              #
        elif selectionrawreduced == 3:  #
            runthecode = 2  # 2 times
        for parsing in range(0, runthecode):  # For loop for reduced and raw parsing.
            if parsing == 0:  #
                if selectionrawreduced == 1 or selectionrawreduced == 3:  #
                    # print('first if')
                    reducedorraw = "parsereduced"  #
                    parsereduceddirectory = codedirectory + "parsereduced.exe"  #
                elif selectionrawreduced == 2 or selectionrawreduced == 3:  #
                    # print('second if')
                    reducedorraw = "parseraw"  #
                    parsereduceddirectory = codedirectory + "parseraw.exe"  #
            elif parsing == 1:  #
                reducedorraw = "parseraw"  #
                parsereduceddirectory = codedirectory + "parseraw.exe"  #
            constellationandprns = '-'  #
            for constellation in constellationstoparse:  #
                import os  #

                print(parsereduceddirectory)
                print("____________________")
                os.system(parsereduceddirectory)  #
                if PRNstoparse[0] == "T":  #
                    if constellation == "G":  #
                        PRNs = range(1, 34)  #
                    elif constellation == "R":  #
                        PRNs = range(1, 26)  #
                    elif constellation == "E":  #
                        PRNs = range(1, 32)  #
                elif PRNstoparse[0] != "T":  #
                    newlistofPRNs = []  #
                    for a in PRNstoparse:  #
                        PRNstring = int(a)  #
                        newlistofPRNs.append(PRNstring)  #
                    PRNs = newlistofPRNs  #
                countt = 0  #
                for satellite in PRNs:  #
                    if selectionrawreduced == 1 or selectionrawreduced == 3:  #
                        if PRNstoparse[0] != "T":  #
                            satellite = PRNstoparse[countt]  #
                    CSVfullname = binaryfilename + "_" + constellation + str(satellite) + ".csv"  #
                    fullname2 = reducedorraw + " " + constellation + str(
                        satellite) + " " + readdirectory + " " + CSVfullname
                    if selectionrawreduced == 2 or selectionrawreduced == 3:  # If the user selects an specific time to be parsed in the settings file, add that to the fullname2.
                        if specifictimes == 1:  #
                            fullname2 = fullname2 + " " + str(starttime) + " " + str(endtime)  #
                        if weekrollover == 1:  #
                            fullname2 = fullname2 + " " + str(startweek) + " " + str(endweek)  #
                    import os  # Create a .CSV file for the specific constellation and satellite.

                    print(fullname2)
                    print("_____________________________")
                    os.system(fullname2)  #
                    if reducedorraw == "parsereduced":  # Open the .csv file and divide it by dates.
                        rangenumber = 2  #
                    elif reducedorraw == "parseraw":  #
                        rangenumber = 3  #
                    for selection in range(rangenumber):  #
                        if reducedorraw == "parsereduced":  # Set the name of the .CSV file.
                            if selection == 0:  #
                                x = "REDTEC_" + CSVfullname  #
                            elif selection == 1:  #
                                x = "REDOBS_" + CSVfullname  #
                            y = x[0:6]  #
                        elif reducedorraw == "parseraw":  #
                            if selection == 0:  #
                                x = "ismRawTec_" + CSVfullname  #
                            elif selection == 1:  #
                                x = "ismRawObs_" + CSVfullname  #
                            elif selection == 2:  #
                                x = "ismDetObs_" + CSVfullname  #
                            y = x[0:9]  #
                        x = codedirectory + x  # Modify the file name once again to include the folder path.
                        toremove = x  #
                        import os  # Check if the file exists. If it does, continue, if it doesn't, skip it.

                        forlateruse = 0  #
                        if os.path.exists(x):  #
                            forlateruse = 1  #
                            # Assign a variable number depending on the filetype. This number represents
                            # the first row of the csv file with data (first row that is not the heading).
                            # Different files have different header lengths.
                            if y == 'REDTEC' or y == 'REDOBS' or y == 'ismRawTEC' or y == 'ismRawTec':  #
                                variable = 20  #
                            elif y == 'ismRawObs' or y == 'ismDetObs':  #
                                if constellation == "G" or constellation == "E":  #
                                    variable = 9  #
                                elif constellation == "R":  #
                                    variable = 11  #
                            import csv  # Import csv file. Set delimiter as commas (',')

                            with open(x) as csvfile:  #
                                readCSV = csv.reader(csvfile, delimiter=',')  #
                                # Create an empty vector that will collect the first column of the
                                # csv files (with a for loop). This column represents the time
                                # (in seconds) at which every datapoint was collected.
                                times = []  # First, identify if the row is empty. If it is, replace it with
                                for row in readCSV:  # a vector full of zeros.
                                    rowlength = len(row)  #
                                    if rowlength == 0:  #
                                        row = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]  #
                                    time = row[0]  #
                                    times.append(time)  #
                            lentimes = len(
                                times)  # Calculate the length of the vector that gathers all the times. This length
                            savelength = lentimes  # value will be modified further into this code, but the original value will
                            forcomparison = variable - 1  # also be used later (save it into a variable called savelengh).
                            if savelength != forcomparison:  # Discard the .csv files that are empty. Just run the rest of the program if the files have data.
                                weeknumbercell = variable - 4  # Subtract 4 to the original "variable" value. This number represents the row
                                weeknumber = times[
                                    weeknumbercell]  # that prints the GPS number of the week. Read the string, cut it, and convert
                                weeknumber = int(weeknumber[-4:])  # the GPS week number into an integer.
                                timeswoheading = times[
                                                 variable:lentimes]  # Create a vector that cuts off the heading of the times vector.
                                timesflt = []  # Convert all the strings in timeswoheading to float values.
                                for item in timeswoheading:  #
                                    timesflt.append(float(item))  #
                                firstsecond = timesflt[
                                    0]  # Select the first number of the list to identify when the data was collected
                                if firstsecond < 86400:  # for the first time (day of the week).
                                    firstday = "Sunday"  #
                                    firsteval = [0, 86400]  #
                                    rownumber = 0  #
                                elif firstsecond >= 86400 and firstsecond < 172800:  #
                                    firstday = "Monday"  #
                                    firsteval = [86400, 172800]  #
                                    rownumber = 1  #
                                elif firstsecond >= 172800 and firstsecond < 259200:  #
                                    firstday = "Tuesday"  #
                                    firsteval = [172800, 259200]  #
                                    rownumber = 2  #
                                elif firstsecond >= 259200 and firstsecond < 345600:  #
                                    firstday = "Wednesday"  #
                                    firsteval = [259200, 345600]  #
                                    rownumber = 3  #
                                elif firstsecond >= 345600 and firstsecond < 432000:  #
                                    firstday = "Thursday"  #
                                    firsteval = [345600, 432000]  #
                                    rownumber = 4  #
                                elif firstsecond >= 432000 and firstsecond < 518400:  #
                                    firstday = "Friday"  #
                                    firsteval = [432000, 518400]  #
                                    rownumber = 5  #
                                elif firstsecond >= 518400 and firstsecond < 604800:  #
                                    firstday = "Saturday"  #
                                    firsteval = [518400, 604800]  #
                                    rownumber = 6  #
                                start = firsteval[0]  #
                                end = firsteval[1]  #
                                name = "GPSCALENDAR.csv"  #
                                import csv  # Import GPSCALENDAR file to identify the date and GPS week number.

                                with open(name) as csvfile:  #
                                    readCSV = csv.reader(csvfile, delimiter=',')  #
                                    yearlist = []  #
                                    monthlist = []  #
                                    daylist = []  #
                                    dayoftheyearlist = []  #
                                    dayoftheweeklist = []  #
                                    weeklist = []  #
                                    for row in readCSV:  #
                                        year = row[0]  #
                                        month = row[1]  #
                                        day = row[2]  #
                                        dayoftheyear = row[3]  #
                                        dayoftheweek = row[4]  #
                                        week = row[5]  #
                                        yearlist.append(year)  #
                                        monthlist.append(month)  #
                                        daylist.append(day)  #
                                        dayoftheyearlist.append(dayoftheyear)  #
                                        dayoftheweeklist.append(dayoftheweek)  #
                                        weeklist.append(week)  #
                                weeklistint = []  # Convert the week numbers to integers, so they can be compared to the
                                for item in weeklist:  # week number from the csv file.
                                    weeklistint.append(int(item))  #
                                weekpositions = []  # Compare each item in the week list to the week number. Identify which
                                csvcolumn = (i for i, item in enumerate(weeklistint) if
                                             item == weeknumber)  # rows in the GPScalendar file correspond to the week number. Then,
                                for i in csvcolumn:  # read the row to select the date (day, year, month etc).
                                    weekpositions.append(i)  #
                                csvrownumber = weekpositions[rownumber]  #
                                daynumber = int(daylist[csvrownumber])  #
                                yearnumber = int(yearlist[csvrownumber])  #
                                monthnumber = int(monthlist[csvrownumber])  #
                                if monthnumber == 1:  # Change the month number to its corresponding name.
                                    monthname = "January"  #
                                elif monthnumber == 2:  #
                                    monthname = "February"  #
                                elif monthnumber == 3:  #
                                    monthname = "March"  #
                                elif monthnumber == 4:  #
                                    monthname = "April"  #
                                elif monthnumber == 5:  #
                                    monthname = "May"  #
                                elif monthnumber == 6:  #
                                    monthname = "June"  #
                                elif monthnumber == 7:  #
                                    monthname = "July"  #
                                elif monthnumber == 8:  #
                                    monthname = "August"  #
                                elif monthnumber == 9:  #
                                    monthname = "September"  #
                                elif monthnumber == 10:  #
                                    monthname = "October"  #
                                elif monthnumber == 11:  #
                                    monthname = "November"  #
                                elif monthnumber == 12:  #
                                    monthname = "December"  #
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
                                    beginning1 = 0  #
                                    end1 = 0  #
                                    stringtoprint = "There is no data for day 1."  #
                                    totallength = variable  #
                                elif lenday1 != 0:  #
                                    beginning1 = variable  #
                                    end1 = lenday1 + variable  #
                                    stringtoprint = "Day 1 goes from cell " + str(beginning1) + " to cell " + str(
                                        end1) + ". (" + firstday + ", " + monthname + " " + str(daynumber) + ", " + str(
                                        yearnumber) + ")"
                                    totallength = end1  #
                                import \
                                    csv  # For day 1: Save all the rows that are part of day 1 in a new matrix that will be printed out later in a new csv file.

                                with open(x) as csvfile:  #
                                    readCSV = csv.reader(csvfile, delimiter=',')  #
                                    day1toprint = []  #
                                    rowcount = 1  #
                                    for row in readCSV:  #
                                        if rowcount <= end1:  #
                                            day1toprint.append(row)  #
                                        rowcount = rowcount + 1  #
                                if daynumber <= 9:  # Print the new csv file for day 1.
                                    daynumber = "0" + str(daynumber)  #
                                if monthnumber <= 9:  #
                                    monthnumber = "0" + str(monthnumber)
                                pathtoprint = CSVfilesdirectory + filesep + str(yearnumber) + str(monthnumber) + str(
                                    daynumber)
                                import os  # Create the folder directory if it does not exist.

                                if not os.path.exists(pathtoprint):  #
                                    os.makedirs(pathtoprint)  #
                                csvfilename1 = pathtoprint + filesep + y + "_" + constellation + str(
                                    satellite) + "_" + str(yearnumber) + str(monthnumber) + str(daynumber) + ".csv"
                                # csvfilename1=pathtoprint+filesep+y+"_"+constellation+str(satellite)+"_"+str(yearnumber)+"_"+str(monthnumber)+"_"+str(daynumber)+".csv"

                                import csv  #

                                with open(csvfilename1, "w") as csvfile:  #
                                    writer = csv.writer(csvfile)  #
                                    writer.writerows(day1toprint)  #
                                firstdaycode = rownumber  # Do the same for all of the days.
                                daycount = 2  # \

                                while totallength < savelength:
                                    if start == 518400:  #
                                        start = 0  #
                                        end = 86400  #
                                    else:  #
                                        start = start + 86400  #
                                        end = end + 86400  #
                                    day2 = []  #
                                    selection = (i for i, item in enumerate(timesflt) if item >= start and item < end)
                                    for i in selection:
                                        day2.append(i)  #
                                    lenday2 = len(day2)  #
                                    lentimes = len(timesflt)  #
                                    timesflt = timesflt[lenday2:lentimes]  #
                                    if lenday2 == 0:  #
                                        beginning2 = 0  #
                                        end2 = 0  #
                                        stringtoprint = "There is no data for day " + str(daynumber) + "."
                                    elif lenday2 != 0:  #
                                        if totallength != variable:  #
                                            beginning2 = totallength + 1  #
                                        elif totallength == variable:  #
                                            beginning2 = totallength  #
                                        if firstdaycode != 6:  #
                                            firstdaycode = firstdaycode + 1  #
                                        elif firstdaycode == 6:  #
                                            firstdaycode = 0  #
                                        end2 = totallength + lenday2  #
                                        if firstdaycode == 0:  #
                                            firstday = "Sunday"  #
                                        elif firstdaycode == 1:  #
                                            firstday = "Monday"  #
                                        elif firstdaycode == 2:  #
                                            firstday = "Tuesday"  #
                                        elif firstdaycode == 3:  #
                                            firstday = "Wednesday"  #
                                        elif firstdaycode == 4:  #
                                            firstday = "Thursday"  #
                                        elif firstdaycode == 5:  #
                                            firstday = "Friday"  #
                                        elif firstdaycode == 6:  #
                                            firstday = "Saturday"  #
                                        m = csvrownumber + daycount - 1  #
                                        daynumber = int(daylist[m])  #
                                        yearnumber = int(yearlist[m])  #
                                        monthnumber = int(monthlist[m])  #
                                        if monthnumber == 1:  # Change the month name.
                                            monthname = "January"  #
                                        elif monthnumber == 2:  #
                                            monthname = "February"  #
                                        elif monthnumber == 3:  #
                                            monthname = "March"  #
                                        elif monthnumber == 4:  #
                                            monthname = "April"  #
                                        elif monthnumber == 5:  #
                                            monthname = "May"  #
                                        elif monthnumber == 6:  #
                                            monthname = "June"  #
                                        elif monthnumber == 7:  #
                                            monthname = "July"  #
                                        elif monthnumber == 8:  #
                                            monthname = "August"  #
                                        elif monthnumber == 9:  #
                                            monthname = "September"  #
                                        elif monthnumber == 10:  #
                                            monthname = "October"  #
                                        elif monthnumber == 11:  #
                                            monthname = "November"  #
                                        elif monthnumber == 12:  #
                                            monthname = "December"  #
                                        stringtoprint = "Day " + str(daycount) + " goes from cell " + str(
                                            beginning2) + " to cell " + str(
                                            end2) + ". (" + firstday + ", " + monthname + " " + str(
                                            daynumber) + ", " + str(yearnumber) + ")"
                                        import \
                                            csv  # For day 2 and on: Save the rows that are to be printed in the variable writecsv files.

                                        with open(x) as csvfile:  #
                                            readCSV = csv.reader(csvfile, delimiter=',')  #
                                            header = []  #
                                            rowcount = 1  #
                                            for row in readCSV:  #
                                                if rowcount < variable:  #
                                                    header.append(row)  #
                                                rowcount = rowcount + 1  #
                                        import csv  #

                                        with open(x) as csvfile:  #
                                            readCSV = csv.reader(csvfile, delimiter=',')  #
                                            daytoprintwoheader = []  #
                                            rowcount = 1  #
                                            for row in readCSV:  #
                                                if rowcount >= beginning2 and rowcount <= end2:  #
                                                    daytoprintwoheader.append(row)  #
                                                rowcount = rowcount + 1  #
                                            daytoprint = header + daytoprintwoheader  #
                                        if daynumber <= 9:  #
                                            daynumber = "0" + str(daynumber)  #
                                        if monthnumber <= 9:  #
                                            monthnumber = "0" + str(monthnumber)  #
                                        pathtoprint = CSVfilesdirectory + filesep + str(yearnumber) + str(
                                            monthnumber) + str(daynumber)
                                        import os  # Create the folder directory if it does not exist.

                                        if not os.path.exists(pathtoprint):  #
                                            os.makedirs(pathtoprint)  #
                                        csvfilename = pathtoprint + filesep + y + "_" + constellation + str(
                                            satellite) + "_" + str(yearnumber) + str(monthnumber) + str(
                                            daynumber) + ".csv"
                                        import csv  #

                                        with open(csvfilename, "w") as csvfile:  # Create the new csvfile.
                                            writer = csv.writer(csvfile)  #
                                            writer.writerows(daytoprint)  #
                                        totallength = end2  #
                                    daycount = daycount + 1  #
                            import os  #

                            os.remove(toremove)  # Remove miscelanous files.
                    countt = countt + 1  #
                prnlist = ': '  #
                elementcount = 1  #
                for element in PRNs:  #
                    if len(PRNs) > 1 and elementcount != len(PRNs):  #
                        prnlist = prnlist + str(element) + ', '  #
                    elif len(PRNs) == 1 or elementcount == len(PRNs):  #
                        prnlist = prnlist + str(element) + '. '  #
                    elementcount = elementcount + 1  #
                if constellation == 'G':  #
                    constellationname = 'GPS'  #
                elif constellation == 'R':  #
                    constellationname = 'GLONASS'  #
                elif constellation == 'E':  #
                    constellationname = 'GALILEO'  #
                constellationandprns = constellationandprns + constellationname + ' ' + str(prnlist)  #
            if forlateruse == 1:  #
                done = 'The following data was parsed: ' + filetorun + '. Date: ' + str(monthnumber) + ' ' + str(
                    daynumber) + ', ' + str(yearnumber) + '. ' + constellationandprns
                printmatrix.append(done)  # Print status.
    else:  #
        daytoprint2 = daymatrix[filecount - 1]  # If the binary file does not exist, print status.
        monthtoprint2 = monthmatrix[filecount - 1]  #
        yeartoprint2 = yeari  #
        if len(str(monthtoprint2)) != 2:  #
            monthtoprint2 = '0' + str(monthtoprint2)  #
        if len(str(daytoprint2)) != 2:  #
            monthtoprint2 = '0' + str(daytoprint2)  #
        printstring = 'The following file does not exist: ' + filetorun
        printmatrix.append(printstring)  #
    filecount = filecount + 1  #
    # Print final matrix summarizing what the code did.
print('Parsing Summary:')
for element in printmatrix:  #
    print(element)

#
a = (time.time() - start_time)
print(a)

# --------------------------------------------------------------------------------------------- #
