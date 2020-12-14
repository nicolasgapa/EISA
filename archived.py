"""
Archived functions and code.
"""


def options_menu(file_type, no_menu, user_selec):
    # --------------------- SECTION 3: PRINTING THE MENU -------------------------- #
    y = file_type  # Set y=filetype. The filetype is selected by the user in the graphsettings.csv file.
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
                graphtype = "Elevation"
                units = "(Degrees)"
            elif ans == "3":
                graphtype = "SecSigLock"
                units = "(seconds)"
            elif ans == "4":
                graphtype = "SecSig_CNo"
                units = "(dB-Hz)"
            elif ans == "5":
                graphtype = "TEC15"
                units = "(TECU)"
            elif ans == "6":
                graphtype = "TECRate15"
                units = "(TECU)"
            elif ans == "7":
                graphtype = "TEC30"
                units = "(TECU)"
            elif ans == "8":
                graphtype = "TECRate30"
                units = "(TECU)"
            elif ans == "9":
                graphtype = "TEC45"
                units = "(TECU)"
            elif ans == "10":
                graphtype = "TECRate45"
                units = "(TECU)"
            elif ans == "11":
                graphtype = "TECTOW"
                units = "(TECU)"
            elif ans == "12":
                graphtype = "TECRateTow"
                units = "(TECU)"
            else:  #
                print("\nThis is an incorrect number")
            break  #
        column = int(ans) + 4
        # The column in the csvfile corresponding to the user selection. e.g. user selects "7" for
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
            elif ans == "2":
                graphtype = "Elevation"
                units = "(Degrees)"
            elif ans == "3":
                graphtype = "CNo"
                units = "(dB-Hz)"
            elif ans == "4":
                graphtype = "Lock_Time"
                units = '(seconds)'
            elif ans == "5":
                graphtype = "CMC_avg"
                units = "(m)"
            elif ans == "6":
                graphtype = "CMC_std"
                units = "(m)"
            elif ans == "7":
                graphtype = "S4"
                units = "Index"
            elif ans == "8":
                graphtype = "S4_Cor"
                units = "Index"
            elif ans == "9":
                graphtype = "1secsigma"
                units = "(radians)"
            elif ans == "10":
                graphtype = "3secsigma"
                units = "(radians)"
            elif ans == "11":
                graphtype = "10secsigma"
                units = "(radians)"
            elif ans == "12":
                graphtype = "30secsigma"
                units = "(radians)"
            elif ans == "13":
                graphtype = "60secsigma"
                units = "(radians)"
            else:  #
                print("\nThis is an incorrect number")
            break  #
        column = int(ans) + 3
        # The column in the csvfile corresponding to the user selection. e.g. user selects "8" for
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
            elif ans == "2":
                graphtype = "TECdot"
                units = "(TECU)"
            else:
                print("\nThis is an incorrect number")
            break
        column = int(ans) + 4
        # The column in the csvfile corresponding to the user selection. e.g. user selects "1" for
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
            elif ans == "2":
                graphtype = "(Power)"
                units = " "
            else:
                print("\nThis is an incorrect number")
            break
        column = int(ans) + 2

    return graphtype, units, column


def read_paths_csv():
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

    return outputfolderdirectory, graphsfolderdirectory


class Plot_Options(object):

    def __init__(self, output_folder_directory, graphs_folder_directory, file_type="REDOBS", graphtype="Elevation",
                 units="(Degrees)", column=5, PRNstograph="T", TECdetrending=False, threshold=30, normalize_data=False,
                 verticaltec=False, onlyonesignal=True, formattype='.png', shiftvalue=0, verticalline=0,
                 constellation="G", setxaxisrange=False, xaxisstartvalue=0, xaxisfinalvalue=24, setyaxisrange=False,
                 yaxisstartvalue=0, yaxisfinalvalue=1, summary_plot=False, legend=False, date="20200915"):
        self.graph_type = graphtype
        self.constellation = constellation
        self.file_type = file_type
        self.threshold = threshold
        self.normalize_data = normalize_data
        self.columna = column
        self.TECdetrending = TECdetrending
        self.verticaltec = verticaltec
        self.summary_plot = summary_plot
        self.onlyonesignal = onlyonesignal
        constellations = {"G": "GPS", "R": "GLONASS", "E": "GALILEO"}
        self.constellationtype = constellations[self.constellation]
        self.formattype = formattype
        self.shift_value = shiftvalue
        self.verticalline = verticalline
        self.units = units
        self.setxaxisrange = setxaxisrange
        self.xaxisstartvalue = xaxisstartvalue
        self.xaxisfinalvalue = xaxisfinalvalue
        self.setyaxisrange = setyaxisrange
        self.yaxisstartvalue = yaxisstartvalue
        self.yaxisfinalvalue = yaxisfinalvalue
        self.legend = legend
        self.raw_data_types = ["ismRawObs", "ismRawOBS", "ismDetObs", "ismDetOBS", "ismRawTEC", "ismRawTec"]
        self.reduced_data_types = ["REDTEC", "REDOBS"]
        self.output_folder_directory = output_folder_directory
        self.graphs_folder_directory = graphs_folder_directory
        self.minimum = 1000
        self.set_date(date)
        self.set_prns(PRNstograph)

    def set_date(self, date):
        self.date = date
        self.monthnumber = self.date[4:6]
        months = {'01': 'January', '02': 'February', '03': 'March', '04': 'April', '05': 'May', '06': 'June',
                  '07': 'July', '08': 'August', '09': 'September', '10': 'October', '11': 'November', '12': 'December'}
        self.monthname = months[self.monthnumber]
        self.directory = self.outputfolderdirectory + "/" + self.date

    def set_prns(self, prns):
        if prns == "T" or prns == "t":
            # GPS has a total of 32 satellites, GLONASS has 24, and GALILEO has 30.
            number_of_satellites = {"G": 32, "R": 24, "E": 30}
            self.PRNstograph = [i for i in range(1, number_of_satellites[self.constellation] + 1)]
        else:
            self.PRNstograph = prns


def read_graph_settings(model):
    m = model
    # Import the graphsettings.csv file.
    with open("graphsettings.csv") as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')  # Read the csv file.
        count = 1  # Start a count for every row in the excel file.
        # Start a FOR loop (FOR LOOP A) that will repeat n times, being n the amount of rows in the csv file.
        # For row 2, extract cell 1 and cell 2 and put them together. This is the file type selected by the user.
        for row in readCSV:
            if count == 2:
                m.file_type = row[0] + row[1]
            elif count == 4:
                m.threshold = float(row[0])
            elif count == 6:
                m.constellation = row[0]
            elif count == 8:
                m.PRNstograph = [i for i in row if len(i) != 0]
            elif count == 10:
                monthi, dayi = str(row[0]), str(row[1])
                if len(str(monthi)) == 1:
                    monthi = '0' + str(monthi)
                if len(str(dayi)) == 1:
                    dayi = '0' + str(dayi)
            elif count == 12:  # Final Date.
                monthf, dayf = str(row[0]), str(row[1])
                if len(str(monthf)) == 1:
                    monthf = '0' + str(monthf)
                if len(str(dayf)) == 1:
                    dayf = '0' + str(dayf)
            elif count == 14:
                yeari = row[0]
            elif count == 16:
                m.summary_plot = True if int(row[0]) == 1 else False
                m.shift_value = float(row[1])
            elif count == 18:
                m.normalize_data = int(row[0])
            elif count == 20:  # Set limits for the x-axis.
                m.setxaxisrange = True if int(row[0]) == 1 else False
                m.xaxisstartvalue = float(row[1])
                m.xaxisfinalvalue = float(row[2])
            elif count == 21:
                m.setyaxisrange = True if int(row[0]) == 1 else False
                m.yaxisstartvalue = float(row[1])
                m.yaxisfinalvalue = float(row[2])
            elif count == 23:
                m.TECdetrending = True if int(row[0]) == 1 else False
            elif count == 25:
                m.PRNlabeling = True if int(row[0]) == 1 else False
            elif count == 27:
                m.legend = True if int(row[0]) == 1 else 0
            elif count == 29:
                m.verticalline = [True if int(row[0]) == 1 else 0, float(row[1])]
            elif count == 31:
                m.verticaltec = True if int(row[0]) == 1 else False
            elif count == 33:
                m.onlyonesignal = True if int(row[0]) == 1 else False
            elif count == 35:
                m.formattype = row[0]
            elif count == 37:
                m.titlefontsize = float(row[0])
                m.subtitlefontsize = float(row[1])
            elif count == 39:
                m.location = row[0]
            count = count + 1  # Add 1 to the count and END FOR LOOP A.

    # Generate day and month matrices, contianing all the dates that will be processed.
    daymatrix, monthmatrix = dates([yeari, monthi, dayi], [yeari, monthf, dayf])

    return m, daymatrix, monthmatrix, yeari


def validate_dates(daymatrix, monthmatrix, yeari, outputfolderdirectory):
    dcount = 0
    valid_dates = []
    for element in daymatrix:
        monthint = monthmatrix[dcount]
        dayint = element
        if len(str(monthint)) == 1:
            monthint = '0' + str(monthint)
        if len(str(dayint)) == 1:
            dayint = '0' + str(dayint)
            # Identify the csv files present within the selected folder.
        readdirectorya = outputfolderdirectory + str(yeari) + str(monthint) + str(dayint)
        if os.path.exists(readdirectorya):
            validfolder = str(yeari) + str(monthint) + str(dayint)
            valid_dates.append(validfolder)
        dcount = dcount + 1
    return valid_dates


def dates(start_date, end_date):
    yeari, monthi, dayi = start_date
    _, monthf, dayf = end_date

    daymatrix = []  # Create two matrices: One for the months and the other one for the days.
    monthmatrix = []
    numberofmonths = int(monthf) - int(monthi)  # How many months will be plotted?
    monthcount = 0
    rangea = numberofmonths + 1
    if numberofmonths != 0:  # If there is more than one month:
        # Start a for loop for each month.
        for month in range(rangea):  # Start a for loop for each month.
            if monthcount <= numberofmonths:
                if monthcount == 0:
                    month = int(monthi)
                else:
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
                    numofdays1 = numofdays - int(dayi)
                elif monthcount != 0 and month != int(monthf):
                    numofdays1 = numofdays
                elif month == int(monthf):
                    numofdays1 = int(dayf)
                for day in range(numofdays1 + 1):
                    if monthcount == 0:
                        daytoadd = int(dayi) + day
                        daymatrix.append(daytoadd)
                    elif monthcount != 0 and month != int(monthf):
                        if day != 0:
                            daytoadd = day
                            daymatrix.append(daytoadd)
                    elif month == int(monthf) and monthcount == numberofmonths:
                        if day <= int(dayf) and day != 0:
                            daytoadd = day
                            daymatrix.append(daytoadd)
                    monthmatrix.append(month)
                monthcount = monthcount + 1
    elif numberofmonths == 0:  # Elseif the range includes only one month:
        month = monthi
        numberofdays = int(dayf) - int(dayi)  # Add each day of the month to the matrix.
        for day in range(numberofdays + 1):
            daytoadd = day + int(dayi)
            monthmatrix.append(int(month))
            daymatrix.append(daytoadd)

    return daymatrix, monthmatrix
