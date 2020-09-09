import csv
import matplotlib.pyplot as plt
import os
import platform
import sys
import numpy as np

filesep = os.sep


#
#  Graphingmain.py code for ionospheric scintillation and Total Electron Content. BETA VERSION.
#  GPStation-6 multi-constellation receiver.
#  JOSE NICOLAS GACHANCIPA - Embry-Riddle Aeronautical University
#
# CREDITS
# The Butterworth filter used for TEC detrending was based on a Matlab function written by Dr. Kshitija Deshpande,
# Professor of Engineering Physics at Embry-Riddle Aeronautical University.
#
# DO NOT HARD CODE ANYTHING BELOW THIS POINT.
#

# --------------------- Section 0: FUNCTIONS --------------------- #


def plot(x_values, y_values, file_type, graph_type, directory, axes_ranges, include_legend=False,
         summary_plot=False, vertical_line=False, vertical_line_x_value=0):
    """"
    Function used for plotting and saving a graph.
    Inputs:
        file_type (string): One of the following: 'REDOBS', 'REDTEC', 'ismRawObs', 'ismRawOBS', 'ismDetObs',
                                                  'ismDetOBS', 'ismRawTEC' or 'ismRawTec'.
        graph_type (string): The type of graph that is being generated (e.g. 'Azymuth', or 'Tecdot')
        include_legend (boolean): Add a legend to the plot.
    Output:
        This function will save the plot to the predetermined directory, but the function itself does not return
        anything.
    """
    # If the user wants a legend, put it on the right, next to the graph. Then, plot.
    if include_legend:
        plt.plot(x_values, y_values, label=str(savedPRNnumber))
    else:
        plt.plot(x_values, y_values)

    # For sigma only: compute the rate of change.
    set_x_axis_range, x_axis_start_value, x_axis_final_value = axes_ranges[0]
    set_y_axis_range, y_axis_start_value, y_axis_final_value = axes_ranges[1]
    if file_type == "REDOBS":
        if "secsigma" in graph_type:

            # If the maximum secsigma value > 100, set the y axis max to 3.
            if max(y_values) > 100:
                set_y_axis_range, y_axis_final_value = 1, 2

    # Add the X and Y-axis labels.
    plt.ylabel(str(graph_type) + " - " + str(units))
    plt.xlabel('Time (UTC)')

    # If graphtype is TECDOT, change the name to 'High Rate TEC Rate of change'.
    if graph_type == 'TECdot':
        graph_type = 'High Rate TEC Rate of change'

    # Set the title  and subtitle of the plot.
    title = monthname + " " + str(daynumber) + " - " + "Time (UTC) vs. " + graph_type
    subtitle = "Elevation threshold: " + str(threshold)
    if summary_plot:
        titletoprint = title + " - Summary Plot - " + constellationtype
        subtitletoprint = subtitle + " - Loc: " + location
    else:
        titletoprint = title + " - " + constellationtype + " " + str(savedPRNnumber) + " (" + lettername + ")"
        subtitletoprint = subtitle + " - Signal type: " + str(sttp) + " - Loc: " + location
    if verticaltec == 1 and normalizedcount == 2:
        subtitletoprint = subtitletoprint + " - Vertical TEC"

    # Change the limits of the axes based on line 20 and 21 of the GRAPHSETTINGS.csv file.
    if set_x_axis_range == 1:
        plt.xlim([x_axis_start_value, x_axis_final_value])
    if set_y_axis_range == 1:
        plt.ylim([y_axis_start_value, y_axis_final_value])

    # If the user wants to print a vertical line, use the axvline function - Line 29 of the GRAPHSETTINGS.csv file.
    if vertical_line:
        plt.axvline(x=vertical_line_x_value, color='K', linewidth=0.5)

    # Label the plot lines (in-plot legends) - Line 25 of the GRAPHSETTINGS.csv file.
    if len(x_values) != 0:
        if PRNlabeling == 1:
            xdatapoint, ydatapoint = x_values[int(len(x_values) / 2)], y_values[int(len(y_values) / 2)]
            plt.text(xdatapoint, ydatapoint, savedPRNnumber)

    # Print the title and subtitle in the plot.
    plt.suptitle(titletoprint, fontsize=titlefontsize)
    plt.title(subtitletoprint, fontsize=subtitlefontsize)

    # Set the directory, and create it if it does not exist.
    if summary_plot:
        ftype = "TEC" if file_type in ["REDTEC", 'ismRawTEC', 'ismRawTec'] else "OBS"
        directory = directory + filesep + "Summary_Plots" + filesep + ftype
    else:
        directory = directory + filesep + graph_type
    if not os.path.exists(directory):
        os.makedirs(directory)
    directory = directory + filesep + graphname

    # Print the directory in the command window.
    print(directory)

    # Print the legend on the plot if legend == True.
    if include_legend:
        plt.legend()

    # Save the figure.
    if not summary_plot:
        plt.savefig(directory)

    # If the summary plot option is not active, clear the graph.
    if not summary_plot:
        plt.clf()


# --------------------- SECTION 1: READING THE GRAPHSETTINGS.CSV FILE --------------------- #
no_menu = 0
if len(sys.argv) > 1:
    if sys.argv[1] == "no_menu":
        no_menu = 1
        user_selec = sys.argv[2]
    else:
        print("The purpose of this code is to plot and save ionospheric scintillation and TEC graphs.")
        print("The directories can be changed by modifying the paths.csv file.")
        print("The settings can be changed by modifying the graphsettings.csv file.")
        # Set the file separator to work in both Linux and Windows.
filesep = os.sep  # Save the file separator into a variable.

# Import the graphsettings.csv file.
with open("graphsettings.csv") as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')  # Read the csv file.
    count = 1  # Start a count for every row in the excel file.
    # Start a FOR loop (FOR LOOP A) that will repeat n times, being n the amount of rows in the csv file.
    # For row 2, extract cell 1 and cell 2 and put them together. This is the file type selected by the user.
    for row in readCSV:
        if count == 2:
            filetyperow = row
            firstpart = filetyperow[0]
            secondpart = filetyperow[1]
            filetype = firstpart + secondpart
        elif count == 4:  # For row 4, extract cell 1 and convert the character to a float.
            thresholdrow = row
            threshold = thresholdrow[0]
            threshold = float(threshold)
        elif count == 6:  # For row 6, identify the constellation system selected by the user.
            constellation = row[0]
            constellations = {"G": "GPS", "R": "GLONASS", "E": "GALILEO"}
            constellationtype = constellations[constellation]
        elif count == 8:  # Row 8. Extract all PRN codes from the row and save them to a variable PRNstograph.
            PRNnumber = row[0]
            savedPRNnumber = PRNnumber
            PRNstographrow = row
            PRNstograph = []
            for a in range(len(PRNstographrow)):
                toappendPRNs = PRNstographrow[a]
                if len(toappendPRNs) != 0:
                    PRNstograph.append(toappendPRNs)
        elif count == 10:  # Initial date.
            monthi = str(row[0])
            dayi = str(row[1])
            if len(str(monthi)) == 1:
                monthi = '0' + str(monthi)
            if len(str(dayi)) == 1:
                dayi = '0' + str(dayi)
        elif count == 12:  # Final Date.
            monthf = str(row[0])
            dayf = str(row[1])
            if len(str(monthf)) == 1:
                monthf = '0' + str(monthf)
            if len(str(dayf)) == 1:
                dayf = '0' + str(dayf)
        elif count == 14:  # Extract the year from row 14.
            year = row[0]
            yeari = year
        # Extract the values from column 1 and 2. Column 1 is the summary plot option. Column 2 is the shift value.
        elif count == 16:
            summaryplot = True if int(row[0]) == 1 else False
            shiftvalue = float(row[1])
        elif count == 18:  # Normalize the data (Night-subtraction).
            normalizedata = int(row[0])
        elif count == 20:  # Set limits for the x-axis.
            setxaxisrange = int(row[0])
            xaxisstartvalue = float(row[1])  # X-axis start value.
            xaxisfinalvalue = float(row[2])  # X-axis final value.
        elif count == 21:
            setyaxisrange = int(row[0])  # Set limits for the y-axis.
            yaxisstartvalue = float(row[1])  # Y-axis star value.
            yaxisfinalvalue = float(row[2])  # Y-axis final value.
        elif count == 23:
            TECdetrending = int(row[0])  # TEC detrending for High-Rate TEC.
        elif count == 25:
            PRNlabeling = int(row[0])  # Labeling the PRN's next to the lines on the graph.
        elif count == 27:
            # Include a legend next to the graph showing the differnt lines being plotted (for summary plots).
            legend = True if int(row[0]) == 1 else 0
        elif count == 29:
            # Vertical line across the graph.
            verticalline = [True if int(row[0]) == 1 else 0, float(row[1])]
        elif count == 31:
            # Convert Slant to Vertical TEC
            verticaltec = int(row[0])
        elif count == 33:
            # int(row[0])  # Get rid of the duplicates - Only plot ONE signal combination per PRN.
            onlyonesignal = int(row[0])
        elif count == 35:
            formattype = row[0]  # Plot format (.png, .pdf, etc).
        elif count == 37:  # Title and Subtitle font Size.
            titlefontsize = float(row[0])  #
            subtitlefontsize = float(row[1])  #
        elif count == 39:  #
            location = row[0]  #
        count = count + 1  # Add 1 to the count and END FOR LOOP A.
        # ----------------------------------------- SECTION 1B: DATES ----------------------------------------------- #
daymatrix = []  # Create two matrices: One for the months and the other one for the days.
monthmatrix = []  #
numberofmonths = int(monthf) - int(monthi)  # How many months will be plotted?
monthcount = 0  #
rangea = numberofmonths + 1  #
if numberofmonths != 0:  # If there is more than one month:
    # Start a for loop for each month.
    for month in range(rangea):  # Start a for loop for each month.
        if monthcount <= numberofmonths:
            if monthcount == 0:
                month = int(monthi)
            else:  #
                month = int(monthi) + monthcount  # Determine the number of days for each specific month.
            if month == 1 or month == 3 or month == 5 or month == 7 or month == 8 or month == 10 or month == 12:
                numofdays = 31
            elif month == 4 or month == 6 or month == 9 or month == 11:
                numofdays = 30
            elif month == 2:
                remainder = int(yeari) % 4
                if remainder == 0:
                    numofdays = 29
                elif remainder != 0:
                    numofdays = 28
            if monthcount == 0:  # Determine all the days inside the range given by the user.
                numofdays1 = numofdays - int(dayi)  #
            elif monthcount != 0 and month != int(monthf):  #
                numofdays1 = numofdays  #
            elif month == int(monthf):  #
                numofdays1 = int(dayf)  #
            for day in range(numofdays1 + 1):  #
                if monthcount == 0:  #
                    daytoadd = int(dayi) + day  #
                    daymatrix.append(daytoadd)  #
                elif monthcount != 0 and month != int(monthf):  #
                    if day != 0:  #
                        daytoadd = day  #
                        daymatrix.append(daytoadd)  #
                elif month == int(monthf) and monthcount == numberofmonths:  #
                    if day <= int(dayf) and day != 0:  #
                        daytoadd = day  #
                        daymatrix.append(daytoadd)  #
                monthmatrix.append(month)  #
            monthcount = monthcount + 1  #
elif numberofmonths == 0:  # Elseif the range includes only one month:
    month = monthi  #
    numberofdays = int(dayf) - int(dayi)  # Add each day of the month to the matrix.
    for day in range(numberofdays + 1):
        daytoadd = day + int(dayi)
        monthmatrix.append(int(month))
        daymatrix.append(daytoadd)

# ----------------- SECTION 2: READING THE PATHS.CSV FILE ----------------- #
osname = platform.system()

# Open the paths .csv file.
with open("PATHS.csv") as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    count = 1
    for row in readCSV:  # Identify the path to the CSV folder and save it to a variable.
        if count == 2:  # This folder is where all CSV files are located.
            outputfolderpath = row
            lengthoutput = len(outputfolderpath)
            outputfolderdirectory = ""
            for a in range(lengthoutput):
                toappendoutput = outputfolderpath[a]
                toappendoutput = toappendoutput + filesep
                outputfolderdirectory = outputfolderdirectory + toappendoutput
        elif count == 4:  # Identify the path to the Graphs folder.
            graphsfolderpath = row  # This folder is where the graphs will be saved.
            lengthgraphs = len(graphsfolderpath)
            graphsfolderdirectory = ""
            for b in range(lengthgraphs):
                toappendgraphs = graphsfolderpath[b]
                if len(toappendgraphs) != 0:
                    toappendgraphs = toappendgraphs + filesep
                graphsfolderdirectory = graphsfolderdirectory + toappendgraphs
        count = count + 1
dcount = 0
validdates = []

for element in daymatrix:  #
    monthint = monthmatrix[dcount]
    dayint = element  #
    if len(str(monthint)) == 1:
        monthint = '0' + str(monthint)
    if len(str(dayint)) == 1:
        dayint = '0' + str(dayint)
        # Identify the csv files present within the selected folder.
    readdirectorya = outputfolderdirectory + str(yeari) + str(monthint) + str(dayint)
    if os.path.exists(readdirectorya):
        validfolder = str(yeari) + str(monthint) + str(dayint)
        validdates.append(validfolder)
    dcount = dcount + 1

# --------------------- SECTION 3: PRINTING THE MENU -------------------------- #
y = filetype  # Set y=filetype. The filetype is selected by the user in the graphsettings.csv file.
if y == 'REDTEC':  # IF THE FILE TYPE IS REDTEC, PRINT THE OPTIONS FOR LOW-RATE TEC.
    ans = True  # EACH OF THESE OPTIONS IS EXPLAINED IN DETAIL IN THE GPSTATION-6 USER MANUAL.
    while ans:  # SEE THE "INSTRUCTIONS" WORD DOCUMENT TO ACCESS AND DOWNLOAD THIS MANUAL.
        if no_menu == 1:
            ans = user_selec
        else:
            print("""                                                      
            1. Azimuth                                                          
            2. Elevation                                                          
            3. SecSig Lock                                                          
            4. SecSig CNo                                                          
            5. TEC15                                                          
            6. TECRate15                                                          
            7. TEC30                                                          
            8. TECRate30
            9. TEC45
            10. TECRate45
            11. TECTOW
            12. TECRateTOW
            """)
            ans = input("What would you like to plot? ")  # Ask the user for an input.
        if ans == "1":  #
            graphtype = "Azymuth"  # Determine the graph type selected by the user.
            units = "(Degrees)"  # Set the units for each graph type.
        elif ans == "2":  # DO THE SAME WITH ALL THE POSSIBLE SELECTIONS...
            graphtype = "Elevation"  #
            units = "(Degrees)"  #
        elif ans == "3":  #
            graphtype = "SecSigLock"  #
            units = "(seconds)"  #
        elif ans == "4":  #
            graphtype = "SecSig_CNo"  #
            units = "(dB-Hz)"  #
        elif ans == "5":  #
            graphtype = "TEC15"  #
            units = "(TECU)"  #
        elif ans == "6":  #
            graphtype = "TECRate15"  #
            units = "(TECU)"  #
        elif ans == "7":  #
            graphtype = "TEC30"  #
            units = "(TECU)"  #
        elif ans == "8":  #
            graphtype = "TECRate30"  #
            units = "(TECU)"  #
        elif ans == "9":  #
            graphtype = "TEC45"  #
            units = "(TECU)"  #
        elif ans == "10":  #
            graphtype = "TECRate45"  #
            units = "(TECU)"  #
        elif ans == "11":  #
            graphtype = "TECTOW"  #
            units = "(TECU)"  #
        elif ans == "12":  #
            graphtype = "TECRateTow"  #
            units = "(TECU)"  #
        else:  #
            print("\nThis is an incorrect number")  #
        break  #
    columna = int(ans) + 4  # The column in the csvfile corresponding to the user selection. e.g. user selects "7" for
    # "TEC30" - column 7 in the csvfile corresponds to the TEC30 values.
if y == 'REDOBS':  # IF THE FILE TYPE IS REDOBS, PRINT THE OPTIONS FOR LOW-RATE SCINTILLATION.
    ans = True  # EACH OF THESE OPTIONS IS EXPLAINED IN DETAIL IN THE GPSTATION-6 USER MANUAL.
    while ans:  # SEE THE "INSTRUCTIONS" WORD DOCUMENT TO ACCESS AND DOWNLOAD THIS MANUAL.
        if no_menu == 1:
            ans = user_selec
        else:
            print("""                                               
            1. Azimuth
            2. Elevation
            3. CNo
            4. Lock Time
            5. CMC avg
            6. CMC std
            7. S4
            8. S4 Cor
            9. 1secsigma
            10. 3secsigma
            11. 10secsigma
            12. 30secsigma
            13. 60secsigma
            """)
            ans = input("What would you like to plot? ")  # Ask the user for an input.
        if ans == "1":  # Determine the graph type selected by the user.
            graphtype = "Azymuth"  # Set the units for each graph type.
            units = "(Degrees)"  # Print the type of plot that will be generated by the code in the command window.
            # DO THE SAME WITH ALL THE POSSIBLE SELECTIONS...
        elif ans == "2":  #
            graphtype = "Elevation"  #
            units = "(Degrees)"  #
        elif ans == "3":  #
            graphtype = "CNo"  #
            units = "(dB-Hz)"  #
        elif ans == "4":  #
            graphtype = "Lock_Time"  #
            units = '(seconds)'  #
        elif ans == "5":  #
            graphtype = "CMC_avg"  #
            units = "(m)"  #
        elif ans == "6":  #
            graphtype = "CMC_std"  #
            units = "(m)"  #
        elif ans == "7":  #
            graphtype = "S4"  #
            units = " "  #
        elif ans == "8":  #
            graphtype = "S4_Cor"  #
            units = " "  #
        elif ans == "9":  #
            graphtype = "1secsigma"  #
            units = "(radians)"  #
        elif ans == "10":  #
            graphtype = "3secsigma"  #
            units = "(radians)"  #
        elif ans == "11":  #
            graphtype = "10secsigma"  #
            units = "(radians)"  #
        elif ans == "12":  #
            graphtype = "30secsigma"  #
            units = "(radians)"  #
        elif ans == "13":  #
            graphtype = "60secsigma"  #
            units = "(radians)"  #
        else:  #
            print("\nThis is an incorrect number")  #
        break  #
    columna = int(ans) + 3  # The column in the csvfile corresponding to the user selection. e.g. user selects "8" for
    # "S4_Cor" - column 11 (8+3) in the csvfile corresponds to the S4_Cor values.
elif y == 'ismRawTEC' or y == 'ismRawTec':  # IF THE FILE TYPE IS ISMRAWTEC, PRINT THE OPTIONS FOR HIGH-RATE TEC.
    ans = True  # EACH OF THESE OPTIONS IS EXPLAINED IN DETAIL IN THE GPSTATION-6 USER MANUAL.
    while ans:  # SEE THE "INSTRUCTIONS" WORD DOCUMENT TO ACCESS AND DOWNLOAD THIS MANUAL.
        if no_menu == 1:
            ans = user_selec
        else:
            print("""
            1. TEC
            2. TECdot
            """)
            ans = input("What would you like to plot? ")  # Ask the user for an input.
        if ans == "1":  # Determine the graph type selected by the user.
            graphtype = "TEC"  # Set the units for each graph type.
            units = "(TECU)"  # Print the type of plot that will be generated by the code in the command window.
            # DO THE SAME WITH ALL THE POSSIBLE SELECTIONS...
        elif ans == "2":  #
            graphtype = "TECdot"  #
            units = "(TECU)"  #
        else:  #
            print("\nThis is an incorrect number")  #
        break  #
    columna = int(ans) + 4  # The column in the csvfile corresponding to the user selection. e.g. user selects "1" for
    # "TEC" - column 5 (1+4) in the csvfile corresponds to the TEC values.
# IF THE FILE TYPE IS ISMRAWOBS OR ISMDETOBS, PRINT THE OPTIONS FOR HIGH-RATE SCINTILLATION.
elif y == 'ismRawObs' or y == 'ismRawOBS' or y == 'ismDetObs' or y == 'ismDetOBS':
    ans = True  # EACH OF THESE OPTIONS IS EXPLAINED IN DETAIL IN THE GPSTATION-6 USER MANUAL.
    while ans:  # SEE THE "INSTRUCTIONS" WORD DOCUMENT TO ACCESS AND DOWNLOAD THIS MANUAL.
        if no_menu == 1:
            ans = user_selec
        else:
            print("""                         
            1. ADR
            2. Power
            """)
            ans = input("What would you like to plot? ")  # Ask the user for an input.
        if ans == "1":  # Determine the graph type selected by the user.
            graphtype = "(ADR)"  # Set the units for each graph type.
            units = " "  # Print the type of plot that will be generated by the code in the command window.
            # DO THE SAME WITH ALL THE POSSIBLE SELECTIONS...
        elif ans == "2":  #
            graphtype = "(Power)"  #
            units = " "  #
        else:  #
            print("\nThis is an incorrect number")  #
        break  #
    columna = int(ans) + 2  #
    #

# FOR EVERY VALID DATE (EXISTENT CSVFILE FOLDERS), RUN THE CODE.
for eachdate in validdates:
    year, monthnumber, daynumber = eachdate[0:4], eachdate[4:6], eachdate[6:8]
    readdirectory = outputfolderdirectory + str(year) + str(monthnumber) + str(daynumber)
    months = {'01': 'January', '02': 'February', '03': 'March', '04': 'April', '05': 'May', '06': 'June',
              '07': 'July', '08': 'August', '09': 'September', '10': 'October', '11': 'November', '12': 'December'}
    monthname = months[monthnumber]

    # ------------------------------------------- SECTION 4: PLOTTING ----------------------------------------------- #
    # ---------------------------------------- SECTION 4A: NUMBER OF PRNs ------------------------------------------- #
    print("\n\n")
    print("# --- " + y + ": Plotting Time vs. " + graphtype + " --- #")
    print("\n\n")

    minimum = 1000  # Set minimum=big number (like 1000) - FOR FURTHER USE IN SECTION 4M.
    # First, identify how many PRNs the user wants to plot from their selection in the graphsettings.csv file.
    if PRNstograph[0] != "T" and PRNstograph[0] != "t":
        # If the user DID NOT insert "T" ("T" means plot all satellites), determine how many PRNs are to be plotted.
        limit = len(PRNstograph)

    elif PRNstograph[0] == "T" or PRNstograph[0] == "t":
        # GPS has a total of 32 satellites, GLONASS has 24, and GALILEO has 30.
        number_of_satellites = {"G": 32, "R": 24, "E": 30}
        limit = number_of_satellites[constellation]

    # -------------------------------- SECTION 4B: FOR LOOP B FOR NIGHT SUBTRACTION --------------------------------- #
    # If the user selectes to do night subtraction for TEC (normalizedata==1), run the code twice using a for loop:
    if normalizedata == 1:
        # One time for regular data (normalizedcount==1), and the second time for the normalized data
        # (normalizedcount==2).
        torepeat = 3
    # This will generate two plots: One for regular data, and one with night-subtraction.
    else:
        torepeat = 2
    for normalizedcount in range(1, torepeat):  # START FOR LOOP B.
        count = 1  # Start a count.
        # If normalizedata==1 the code will run twice. After running once for regular data, clear the plot and create a
        # new one with normalized data.
        if normalizedcount == 2:
            plt.clf()

        # ---------------------------------- SECTION 4C: FOR LOOP C FOR NUMBER OF PRNs ------------------------------ #
        # START FOR LOOP C - It will repeat N times, where N is the number of PRNs selected by the user (Section 4A).
        for prn in range(limit):
            # Save the count into a variable calles savedPRNnumber. This variable will be used later to show the PRN
            # number
            if PRNstograph[0] == "T" or PRNstograph[0] == "t":
                # In the title of the plot, to include the PRN# in the legends, among other uses. If the user selects
                # to plot all satellites.
                savedPRNnumber = count
            # This number is equal to the count started in Section 4B. If the user inputs specific PRN numbers in
            # the graphsettings.csv.
            elif len(PRNstograph) > 1:
                # file, select the value from the PRNstograph vector from Section 1.
                savedPRNnumber = PRNstograph[count - 1]
                # Set the directory to the csv file.
            csvtograph = filetype + "_" + constellation + str(savedPRNnumber) + "_" + str(year) + str(
                monthnumber) + str(daynumber) + ".csv"
            csvtographdirectory = readdirectory + filesep + csvtograph

            # ------------------------------ SECTION 4D: ELEVATION THRESHOLD FOR RAW DATA FILES ---------------------- #
            # For raw data files, extract the elevation column for the REDTEC file and determine a range of times that
            # are above the elevation threshold. Save the directory to the REDTEC into a variable called
            # readreducedfile.
            if y == "ismRawObs" or y == "ismRawOBS" or y == "ismDetObs" or y == "ismDetOBS" or y == "ismRawTEC" or y == "ismRawTec":
                readreducedfile = readdirectory + filesep + "REDTEC" + "_" + constellation + str(
                    savedPRNnumber) + "_" + str(year) + "_" + str(monthnumber) + "_" + str(
                    daynumber) + ".csv"
                if not os.path.isfile(readreducedfile):
                    continue

                with open(readreducedfile) as csvfilethree:
                    readCSVthree = csv.reader(csvfilethree, delimiter=',')
                    # Cut the header off the csvfile cutting the first 20 rows and select the elevation's column.
                    counttwo = 1
                    validcolumns = []
                    timescolumn = []
                    for row in readCSVthree:
                        if len(row) == 0:
                            timescolumnitem = "0"
                        else:
                            timescolumnitem = row[0]
                        timescolumn.append(timescolumnitem)
                        if counttwo >= 20:
                            elevationforthresholdb = row[6]
                            # Determine which rows of the elevation column have a value that exceeds the threshold set
                            # by the user.
                            if float(elevationforthresholdb) >= threshold:
                                validcolumns.append(counttwo)
                        counttwo = counttwo + 1

                # Sometimes, satellites cross the elevation threshold multiple times within a day. E.G. PRN 2 is
                # above. Sometimes, satellites cross the elevation threshold multiple times within a day. E.G.
                # PRN 2 is above the elevation threshold between 1PM and 3PM, and then later between 7PM and 9PM.
                subtractthisvalue = 0
                rangestartrows = []
                # Identify the times at which satellites cross the elevation threshold and save those values into
                # variables.
                for itema in validcolumns:
                    # e.g. in the previous example: rangestartrows:[1PM, 7PM] and rangefinalrows=[3PM, 9PM].
                    if (itema - subtractthisvalue) != 1:
                        rangestartrow = itema  #
                        rangestartrows.append(rangestartrow)  #
                    subtractthisvalue = itema  #
                if len(rangestartrows) > 1:  #
                    rangefinalrows = []  #
                    for j in range(len(rangestartrows) - 1):
                        rangefinalrow = rangestartrows[1]
                        rangefinalrows.append(rangefinalrow)
                    rangefinalrows = (rangefinalrows, validcolumns[-1])
                elif len(rangestartrows) == 1:
                    rangefinalrows = [validcolumns[-1]]
                # Determine the times (in seconds) for both start and final rows in the range variables.
                countfour = 0
                starttimes = []
                finaltimes = []
                if len(rangestartrows) > 1:
                    for itemb in len(rangestartrows):
                        startselection = rangestartrows[countfour]
                        finalselection = rangefinalrows[countfour]
                        starttime = timescolumn[startselection]
                        finaltime = timescolumn[finalselection - 1]
                        starttimes.append(str(starttime))
                        finaltimes.append(str(finaltime))
                        countfour = countfour + 1
                elif len(rangestartrows) == 1:
                    startselection = rangestartrows[0]
                    finalselection = rangefinalrows[0]
                    starttimes = [timescolumn[startselection]]
                    finaltimes = [timescolumn[finalselection - 1]]
                starttimesflt = []  # Convert the times to float values.
                finaltimesflt = []
                for t in starttimes:
                    starttimesflt.append(float(t))
                for u in finaltimes:
                    finaltimesflt.append(float(u))

            # ----------------------- SECTION 4E: EXTRACTING THE COLUMNS FROM THE CSV FILE --- #
            # Import and read the csv (if it exists) If not, jump to SECTION 5.
            if os.path.isfile(csvtographdirectory):

                with open(csvtographdirectory) as csvfiletwo:
                    readCSVtwo = csv.reader(csvfiletwo, delimiter=',')
                    if y == "REDTEC" or y == "ismRawTEC" or y == "ismRawTec":  # Set the variable numbers - These nunmbers will be used later for multiple purposes and vary
                        variablesignal = 4
                        variable = 20
                        elevationvar = 6
                    elif y == "REDOBS":
                        variablesignal = 3
                        variable = 20
                        elevationvar = 5
                    elif y == "ismRawObs" or y == "ismRawOBS" or y == "ismDetObs" or y == "ismDetOBS":  #
                        variablesignal = 2
                        variable = 9
                    rawyaxiscolumn = []  # Select the column within the csv file based on the user selection in part 3.
                    # Cut off the header using the variable from 11ac. Do the same with the "times" column.
                    varsignaltypecolumn = []
                    elevationcolumn = []
                    times = []
                    countone = 1
                    for row in readCSVtwo:
                        if countone >= variable:
                            selectedrowitem = row[columna]
                            signaltypeitem = row[variablesignal]
                            if y == "REDTEC" or y == "REDOBS":
                                elevationcolumn.append(row[elevationvar])
                            time = row[0]
                            # Save the column to a variable called "rawyaxiscolumn".
                            rawyaxiscolumn.append(selectedrowitem)
                            # Read the signal type column. This variable will be used later to determine the signal
                            # types for the selected PRN.
                            varsignaltypecolumn.append(signaltypeitem)
                            times.append(time)
                        countone = countone + 1

                # There are 7 types of signals (1 through 7).
                # Determine how many types of signals (and which ones) are present in the selected file.
                # Save the present signal types into a variable calles saves.
                varsignaltypecolumn = list(map(int, varsignaltypecolumn))
                saves = [it for it in range(1, 8) if it in varsignaltypecolumn]

                # ----------------------- SECTION 4F: FOR LOOP D FOR SIGNAL TYPE ----------------------- #
                # START FOR LOOP D that will repeat for each signal type (selection) for the selected PRN.
                for selection in saves:

                    # First, determine which rows correspond to the selected signal type.
                    # Save the row numbers to a variable called listofrows.
                    listofrows = [c for c, i in enumerate(varsignaltypecolumn, variable) if int(i) == int(selection)]

                    # ---------------------------- SECTION 4G: TIME PERIODS ---------------------------- #
                    # Use the listofrows variable from section 4f and cut the rawyaxiscolumn from section 4e with
                    # the respective rows.
                    redyaxiscolumn = []
                    newelevations = []
                    newtimes = []
                    for rowitem in listofrows:
                        rowitemint = int(rowitem) - variable

                        # Cut the times column with the respective rows.
                        newtime = times[rowitemint]
                        redyaxisitem = rawyaxiscolumn[rowitemint]
                        if y == "REDTEC" or y == "REDOBS":
                            newelevation = elevationcolumn[rowitemint]
                            newelevations.append(newelevation)
                        newtimes.append(newtime)

                        # Save the new column as "redyaxiscolumn". Save the new times column as "newtimes".
                        redyaxiscolumn.append(redyaxisitem)

                    # Sometimes, satellites cross the elevation threshold multiple times within a day. E.G. PRN 2
                    # is above the elevation threshold between 1PM and 3PM, and then later between 7PM and 9PM.
                    # Each of these times is called a TIME PERIOD.
                    countsix = 1
                    biggerdiference = 1

                    # Identify the times at which satellites cross the elevation threshold and save those values
                    # into a variable.
                    listofpositions = []
                    firstselection = 0
                    for timeinsec in newtimes:
                        # Determine the difference between each data value and the next one in the newtimes vector.
                        difference = float(timeinsec) - firstselection
                        # If the difference is bigger than 1200 (i.e 1200 seconds), save the position into a
                        # variable called listofpositions.
                        if difference > 1200:
                            biggerdifference = 1
                        elif difference <= 1200:
                            biggerdifference = 0
                        if countsix == 1 or biggerdifference == 1:
                            listofpositions.append(countsix)
                        firstselection = float(timeinsec)
                        countsix = countsix + 1

                    # ---------------------------- SECTION 4H: FOR LOOP E FOR TIME PERIOD ------------------------ #
                    # Determine the amount of time periods by finding the length of the listofpositions variable.
                    lengthofthelist = len(listofpositions)
                    countseven = 1
                    countfifteen = 1
                    if y == "ismRawObs" or y == "ismDetObs" or y == "ismDetOBS" or y == "ismRawTEC" or y == "ismRawTec":
                        # If the selected file is a raw data file, set listofpositions equal to the starttimesflt
                        # variable from Section 4D.
                        listofpositions = starttimesflt
                    if onlyonesignal == 1 and not summaryplot:
                        # If the plot to be created is NOT a summary plot and onlyonesignal=1 from section 1,
                        # listofpositions=first value in listofpositions (listofpositions[0])
                        listofpositions = [listofpositions[0]]
                        lengthofthelist = len(listofpositions)

                    # START FOR LOOP E THAT WILL REPEAT FOR EVERY TIME PERIOD.
                    for timestartposition in listofpositions:
                        # Start this section ONLY if the user selected a reduced file, either REDOBS or REDTEC.
                        if y == "REDTEC" or y == "REDOBS":
                            # Each time period has a different start time and end time. The start time will change
                            # automatically.
                            if countseven < lengthofthelist:
                                timefinalposition = listofpositions[countseven] - 1
                            elif countseven == lengthofthelist:
                                timefinalposition = len(newtimes)
                            finalelevationcolumn = []

                            # Start another for loop to create the new x and y axes.
                            # Cut the newtimes and redyaxiscolumn from section 4G.
                            finaltimes = [it for c, it in enumerate(newtimes, 1) if
                                          timestartposition <= c <= timefinalposition]
                            finalyaxis = [it for c, it in enumerate(redyaxiscolumn, 1) if
                                          timestartposition <= c <= timefinalposition]

                            # Cut off the rows that have an elevation under the threshold.
                            counteleven = 1
                            for itemf in newelevations:
                                if timestartposition <= counteleven <= timefinalposition:
                                    finalelevationcolumn.append(itemf)
                                counteleven = counteleven + 1
                            addvariablestart = timestartposition + variable - 1
                            addvariablefinal = timefinalposition + variable - 1
                            counttwelve = 1
                            validelevpositions = []
                            correctedelevation = []
                            finalelevationcolumn = list(map(float, finalelevationcolumn))
                            for itemg in finalelevationcolumn:
                                if itemg >= threshold:
                                    validelevpositions.append(counttwelve)
                                    # Create a new variable (vector) containing all elevations above the threshold.
                                    correctedelevation.append(itemg)
                                counttwelve = counttwelve + 1

                            # Cut the finaltimes/finalyaxis vectors to include only the times at which the
                            # elevation is above the threshold. Save it to new arrays.
                            validelevs = list(map(int, validelevpositions))
                            finaltimescorrected = [it for c, it in enumerate(finaltimes, 1) if c in validelevs]
                            finalyaxiscorrected = [it for c, it in enumerate(finalyaxis, 1) if c in validelevs]

                        # --------------------------------- SECTION 4J: MODIFY RAW DATA ------------------------- #
                        elif y == "ismRawObs" or y == "ismRawOBS" or y == "ismDetObs" or y == "ismDetOBS" or y == "ismRawTEC" or y == "ismRawTec":
                            # Start this section if the user selects a raw data file type.
                            starttimetocompare = starttimesflt[countseven - 1]
                            # Extract the final time from the starttimesflt from Section 4D.
                            finaltimetocompare = finaltimesflt[countseven - 1]
                            countfive = 0
                            validpositions = []
                            # Determine which rows have time values within the specified range.
                            for itemc in newtimes:
                                itemc = float(itemc)
                                if starttimetocompare <= itemc <= finaltimetocompare:
                                    validpositions.append(countfive)
                                countfive = countfive + 1
                            finaltimescorrected = []
                            finalyaxiscorrected = []
                            # Correct the x and y axes to include only values within the specified range.
                            for itemj in validpositions:
                                timetoappend = newtimes[itemj]
                                yaxistoappend = redyaxiscolumn[itemj]
                                finaltimescorrected.append(timetoappend)
                                finalyaxiscorrected.append(yaxistoappend)
                                # If TEC detrending is activated, from Section 1, run Section 4K:

                            # ------------------------ SECTION 4K: TEC DETRENDING -------------------------- #
                            # For TEC: If TECdetrending=1 in the GRAPHSETTINGS csv file, detrend the TEC data.
                            # Convert the elements of finaltimescorrected and finalyaxiscorrected into float values
                            # before applying the butterworth filter.
                            if TECdetrending == 1:
                                bftimes = []
                                bfTEC = []
                                for itemk in finaltimescorrected:
                                    bftimes.append(float(itemk))
                                for iteml in finalyaxiscorrected:
                                    bfTEC.append(float(iteml))
                                # Print the times and TEC vectors into two columns in a new csv file.
                                # This file can be later called from MATLAB for a better TEC detrending.
                                matrixtoprint = []
                                counteighteen = 0
                                # This CSV file is saved in the same folder as the graphingmain.py code.
                                for itemm in range(len(bftimes)):
                                    row = [bftimes[counteighteen], bfTEC[counteighteen]]
                                    matrixtoprint.append(row)
                                    counteighteen = counteighteen + 1
                                import csv

                                namedetrending = "TECdetrending" + constellation + str(savedPRNnumber) + str(
                                    selection) + "-" + str(year) + str(monthnumber) + str(daynumber) + ".csv"
                                with open(namedetrending, "w+", newline='') as csvfile:
                                    writer = csv.writer(csvfile)
                                    writer.writerows(matrixtoprint)
                                # TEC: Polyfit subtraction and then a type of Butterworth filtering/ Sliding Avg

                                poly_degree = 3  # filtering on TEC time series (TEC_ts values).
                                poly_coef = np.polyfit(bftimes, bfTEC, poly_degree)  # Degree of the polynomial.
                                poly = np.polyval(poly_coef,
                                                  bftimes)  # In this case, finalyaxiscorrected is the TEC vector.
                                poly_sub_tec = bfTEC - poly  #
                                from scipy import signal  #

                                polyfit_tec = signal.detrend(poly_sub_tec)  #
                                Tdata = bftimes[-2] - bftimes[0]  #
                                dfreq = 1 / Tdata  #
                                LP = len(polyfit_tec)  #
                                tec_fft = np.fft.fftshift(np.fft.fft(np.fft.ifftshift(polyfit_tec)))
                                if Tdata <= 60:  # Desired cut off frequency [Hz]
                                    cutoff = 0.1  # Higher cut off for shorter lengths
                                else:  #
                                    cutoff = 0.1  #
                                order = 6  # Order of the butterworth filter
                                # ------------------- Butterworth filter -------------------------- #
                                # This extract creates a kernel for low pass butterworth filter.
                                freq = np.arange(-LP / 2 * dfreq + dfreq, (LP / 2 * dfreq) + dfreq,
                                                 dfreq)  # Create frequency array
                                butterlow = np.divide(1, np.sqrt(
                                    1 + (np.power((freq / cutoff), (2 * order)))))  # Size(freq)
                                butterhi = 1.0 - butterlow
                                # ----------------------------------------------------------------- #
                                tec_filt = np.fft.fftshift(
                                    np.fft.ifft(np.fft.ifftshift(np.multiply(tec_fft, butterhi))))
                                Detrended_TEC = (np.real(tec_filt))  #
                                finalyaxiscorrected = Detrended_TEC  # Set the Detrended TEC as the new finalyaxiscorrected.
                            # ------------------ END OF TEC DETRENDING -------------------- #

                        # --------------------------------- SECTION 4L: FINAL FIXES ------------------------------ #

                        # Select a letter. This letter will be printed in the title of the plot.
                        # The letter represents the time period. e.g. if there are two time periods for one PRN,
                        # the plot showing time period 1 will have "A" in the title. Time period 2 will have "B".
                        # Refer to Section 4G to see the definition of a time period.
                        letters = {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E', 6: 'F', 7: 'G', 8: 'H'}
                        lettername = letters[countfifteen]
                        countfifteen += 1

                        listtoreferto = finaltimescorrected  # Rename the x-axis values to "listtoreferto".
                        listforyaxis = finalyaxiscorrected  # Rename the y-axis values to "listforyaxis".
                        newtimesUTC = []
                        for numbertoconvert in listtoreferto:  # Convert the times to UTC.
                            numbertoconvert = float(numbertoconvert)  # 86400 sec = 1 day.
                            if numbertoconvert >= 86400:
                                remainder = numbertoconvert % 86400
                                if remainder == 0:
                                    remainder = 86400
                            elif numbertoconvert < 86400:
                                remainder = numbertoconvert  #
                            howmanyhoursflt = remainder / 3600  # Determine the amount of hours.
                            newtimesUTC.append(howmanyhoursflt)  #
                        if summaryplot:  # Determine the name of the graph.
                            csvtograph = filetype + "_SummaryPlot_" + str(year) + str(monthnumber) + str(
                                daynumber) + ".csv"
                        else:
                            csvtograph = filetype + "_" + constellation + str(savedPRNnumber) + "_" + str(
                                year) + str(monthnumber) + str(daynumber) + ".csv"
                        lengthtocutname = len(csvtograph) - 4
                        graphname = csvtograph[:lengthtocutname]
                        if summaryplot:
                            graphname = graphname + "_" + graphtype + "_" + constellationtype
                        else:
                            graphname = graphname + "_" + graphtype + "_" + "Signal" + str(
                                selection) + "_" + lettername
                        if normalizedcount == 2:  #
                            graphname = graphname + "_Normalized"
                        if verticaltec == 1 and normalizedcount == 2:
                            graphname = graphname + "_verticalTEC"
                        graphname = graphname + str(formattype)
                        savinggraphs = graphsfolderdirectory + str(year) + str(monthnumber) + str(daynumber)
                        listforyaxisflt = [float(e) for e in listforyaxis]

                        # ------------------ SECTION 4M: NIGHT SUBTRACTION AND VERTICAL TEC -------------------- #
                        # Run this part of the code ONLY if listforyaxisflt is not an empty vector.
                        if len(listforyaxisflt) != 0:
                            # Run this part of the code ONLY for low-rate TEC data.
                            if y == "REDTEC" or y == "REDOBS":
                                if normalizedata == 1:  # Run this part of the code ONLY if nigh-subtraction is selected (normalizedata==1).
                                    if normalizedcount == 1:  # When normalizedcount==1 (regular data), select the minimum value. Refer to section 4B.
                                        minimumvalueyaxis = min(float(s) for s in listforyaxisflt)
                                        if minimumvalueyaxis < minimum:  #
                                            minimum = minimumvalueyaxis  # After FOR LOOP B (SECTION 4B) runs completely for the first time, it will calculate the minimum TEC value from ALL PRNs.
                                    elif normalizedcount == 2:  # When normalizedcount==2 (i.e. when FOR LOOP B runs for the second time):
                                        normalizedaxis = []  #
                                        countthirty = 0  #
                                        for elementa in listforyaxisflt:  # For every element in listforyaxisflt, convert to vertical TEC (if vertical TEC==1) and do the night-subtraction.
                                            # ----------------------------------------------- SLANT  TO VERTICAL TEC --------------------------------------------- #
                                            if verticaltec == 1:  # This section uses geometry to get rid of the effects due to the variable thickness of the atmosphere.
                                                import math  #

                                                minimumvaluetouse = min(float(s) for s in listforyaxisflt)
                                                elementa = elementa - minimumvaluetouse  #
                                                elevationtouse = correctedelevation[countthirty] * 0.0174533
                                                coselev = math.cos(elevationtouse)  #
                                                obliquity = 1 / (math.sqrt(1 - (0.947979 * (coselev))))  #
                                                newelement = elementa / obliquity  #
                                                newelement = newelement + minimumvaluetouse  #
                                                countthirty = countthirty + 1  #
                                                # --------------------------------------------------------------------------------------------------------------------- #
                                            else:  #
                                                newelement = elementa  #
                                            elementtoappend = newelement - minimum  # Subtract the minimum value (computed at the beginning of section 4M) from each element.
                                            normalizedaxis.append(
                                                elementtoappend)  # Append the element to a new vector called normalized axis.
                                        listforyaxisflt = normalizedaxis  # Set listforyaxisflt==normalizedaxis.

                        # If the user is doing a summary plot add the shift value to every element in the
                        # listforyaxisflt vector. See Section 1.
                        if summaryplot:
                            summaryplotaxis = []  #
                            for elementa in listforyaxisflt:  #
                                elementtoappend = elementa + (count * shiftvalue)  #
                                summaryplotaxis.append(elementtoappend)  #
                            listforyaxisflt = summaryplotaxis  #

                        # ------------------------------------- SECTION 4N: PLOTTING ---------------------------- #
                        # From the selection from FOR LOOP D, determine the signal type (L1, L2, ETC).
                        signal_types = {"G": {"1": "L1CA", "4": "L2Y", "5": "L2C", "6": "L2P", "7": "L5Q"},
                                        "R": {"1": "L1CA", "3": "L2CA", "4": "L2P"},
                                        "E": {"1": "E1", "2": "E5A", "3": "E5B",  "4": "AltBOC"}}
                        sttp = signal_types[constellation][str(selection)]

                        if len(listforyaxisflt) != 0:
                            plot(newtimesUTC, listforyaxisflt, y, graphtype, savinggraphs,
                                 [[setxaxisrange, xaxisstartvalue, xaxisfinalvalue],
                                  [setyaxisrange, yaxisstartvalue, yaxisfinalvalue]],
                                 include_legend=legend, summary_plot=summaryplot, vertical_line=verticalline[0],
                                 vertical_line_x_value=verticalline[1])

                        countseven += 1  # END OF FOR LOOP D.

            # ------------------------------ SECTION 5: THE DIRECTORY DOES NOT EXIST ------------------------------- #
            # If the directory does NOT exist (from section 4E), print "THE DIRECTORY DOES NOT EXIST"
            elif not os.path.isfile(csvtographdirectory):
                toprint = "The following directory does not exist: " + csvtographdirectory  # in the command window.
                # print(toprint)
            count = count + 1
            # END OF FOR LOOP B - END OF FOR LOOP C.

    # Print message to the terminal.
    print("The following day has been processed: " + monthname + " " + str(daynumber) + " - Graph Type: " +
          str(graphtype) + " - Constellation: " + constellationtype)
