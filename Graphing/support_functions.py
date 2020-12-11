import os
import csv
import numpy as np
import math
from scipy import signal
import operator
import matplotlib.pyplot as plt

""""
Other useful functions.
"""
filesep = os.sep


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


def values_above_threshold(file, threshold=0, header=0, times_column=0, elevations_column=0):
    with open(file) as csvfilethree:
        readCSVthree = csv.reader(csvfilethree, delimiter=',')

        # Cut the header off the csvfile cutting the first [header] rows and select the elevation's column.
        validelevcolumns = timescolumn = valuescolumn = []
        for counttwo, row in enumerate(readCSVthree, 1):
            if counttwo >= header:
                elevationforthresholdb = row[elevations_column]
                # Determine which rows of the elevation column have a value that exceeds the threshold set
                # by the user.
                if float(elevationforthresholdb) >= threshold:
                    validelevcolumns.append(counttwo)
                    valuescolumn.append(row)
                    if len(row) == 0:
                        timescolumnitem = "0"
                    else:
                        timescolumnitem = row[times_column]
                    timescolumn.append(timescolumnitem)
    return times_column, validelevcolumns, valuescolumn


def times_cross_elevation(times_col, elevations_col):
    # Sometimes, satellites cross the elevation threshold multiple times within a day. E.G. PRN 2 is
    # above. Sometimes, satellites cross the elevation threshold multiple times within a day. E.G.
    # PRN 2 is above the elevation threshold between 1PM and 3PM, and then later between 7PM and 9PM.
    subtractthisvalue = 0
    rangestartrows = []

    # Identify the times at which satellites cross the elevation threshold and save those values into
    # variables.

    for itema in elevations_col:
        # e.g. in the previous example: rangestartrows:[1PM, 7PM] and rangefinalrows=[3PM, 9PM].
        if (itema - subtractthisvalue) != 1:
            rangestartrow = itema
            rangestartrows.append(rangestartrow)
        subtractthisvalue = itema

    if len(rangestartrows) > 1:
        rangefinalrows = []
        for j in range(len(rangestartrows) - 1):
            rangefinalrow = rangestartrows[1]
            rangefinalrows.append(rangefinalrow)
        rangefinalrows = (rangefinalrows, elevations_col[-1])
    elif len(rangestartrows) == 1:
        rangefinalrows = [elevations_col[-1]]

    # Determine the times (in seconds) for both start and final rows in the range variables.
    countfour = 0
    starttimes = []
    finaltimes = []
    if len(rangestartrows) > 1:
        for _ in len(rangestartrows):
            startselection = rangestartrows[countfour]
            finalselection = rangefinalrows[countfour]
            starttime = times_col[startselection]
            finaltime = times_col[finalselection - 1]
            starttimes.append(str(starttime))
            finaltimes.append(str(finaltime))
            countfour = countfour + 1
    elif len(rangestartrows) == 1:
        startselection = rangestartrows[0]
        finalselection = rangefinalrows[0]
        starttimes = [times_col[startselection]]
        finaltimes = [times_col[finalselection - 1]]
    starttimesflt = []  # Convert the times to float values.
    finaltimesflt = []
    for t in starttimes:
        starttimesflt.append(float(t))
    for u in finaltimes:
        finaltimesflt.append(float(u))

    return starttimesflt, finaltimesflt


def extract_data(file, header=0):
    data = []
    with open(file) as csvfilethree:
        readCSVthree = csv.reader(csvfilethree, delimiter=',')
        for i, row in enumerate(readCSVthree):
            if i >= header:
                data.append(row)
    return np.array(data)


def filter_data(data, column, comparison_type, comparison_value, columns_to_return):
    operators = {"=": operator.eq, ">=": operator.gt}
    op = operators[comparison_type]

    filtered_data = []
    for row in data:
        if op(float(row[column]), comparison_value):
            filtered_data.append(row)

    # Cut columns.
    final_filter = []
    for row in filtered_data:
        final_filter.append([row[i] for i, _ in enumerate(row) if i in columns_to_return])

    return np.array(filtered_data)


def naming(prn, signal_type, normalize, time_period, model):
    # --------------------------------- SECTION 4L: NAMING ------------------------------ #
    constellations = {"G": "GPS", "R": "GLONASS", "E": "GALILEO"}
    constellation_type = constellations[model.constellation]

    # Select a letter. This letter will be printed in the title of the plot.
    # The letter represents the time period. e.g. if there are two time periods for one PRN,
    # the plot showing time period 1 will have "A" in the title. Time period 2 will have "B".
    # Refer to Section 4G to see the definition of a time period.
    letters = {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E', 6: 'F', 7: 'G', 8: 'H', 9: 'I', 10: 'J'}
    lettername = letters[time_period]

    if model.summary_plot:  # Determine the name of the graph.
        graphname = model.file_type + "_SummaryPlot_" + model.date
        graphname = graphname + "_" + model.graphtype + "_" + constellation_type
    else:
        graphname = model.file_type + "_" + model.constellation + str(prn) + "_" + model.date
        graphname = graphname + "_" + model.graphtype + "_" + "Signal" + str(signal_type) + "_" + lettername

    if normalize == 1:
        graphname = graphname + "_Normalized"
    if model.verticaltec == 1 and normalize == 1:
        graphname = graphname + "_verticalTEC"

    graphname = graphname + str(model.formattype)
    savinggraphs = model.graphsfolderdirectory + model.date

    # Set the title  and subtitle of the plot.
    title = model.monthname + " " + str(model.daynumber) + " - " + "Time (UTC) vs. " + model.graphtype
    subtitle = "Elevation threshold: " + str(model.threshold)
    if model.summary_plot:
        titletoprint = title + " - Summary Plot - " + constellation_type
        subtitletoprint = subtitle + " - Loc: " + model.location
    else:
        titletoprint = title + " - " + constellation_type + " " + str(model.savedPRNnumber) + " (" + lettername + ")"
        subtitletoprint = subtitle + " - Signal type: " + str(signal_type) + " - Loc: " + model.location
    if model.verticaltec == 1 and normalize == 1:
        subtitletoprint = subtitletoprint + " - Vertical TEC"

    return graphname, savinggraphs, titletoprint, subtitletoprint


def tec_detrending(x_values, y_values):
    """"
    Fuction: Detrend the TEC data using a butterworth filter.

    Inputs:
        x_values (list): time values
        y_values (list): TEC values
    Output:
        This function returns the detrended TEC (y-axis) values only.
    """

    # Convert all values to float.
    bftimes = [float(x) for x in x_values]
    bfTEC = [float(y) for y in y_values]

    # TEC: Polyfit subtraction and then a type of Butterworth filtering/ Sliding Avg
    poly_degree = 3  # Filtering on TEC time series (TEC_ts values).
    poly_coef = np.polyfit(bftimes, bfTEC, poly_degree)  # Degree of the polynomial.
    poly = np.polyval(poly_coef, bftimes)  # In this case, y-axis is the TEC vector.
    poly_sub_tec = bfTEC - poly
    polyfit_tec = signal.detrend(poly_sub_tec)
    Tdata = bftimes[-2] - bftimes[0]
    dfreq = 1 / Tdata
    LP = len(polyfit_tec)
    tec_fft = np.fft.fftshift(np.fft.fft(np.fft.ifftshift(polyfit_tec)))

    # ------------------- Butterworth filter -------------------------- #
    cutoff = 0.1  # Desired cut off frequency [Hz]
    order = 6  # Order of the butterworth filter.

    # This extract creates a kernel for low pass butterworth filter.
    freq = np.arange(-LP / 2 * dfreq + dfreq, (LP / 2 * dfreq) + dfreq, dfreq)  # Create frequency array
    butterlow = np.divide(1, np.sqrt(1 + (np.power((freq / cutoff), (2 * order)))))  # Size(freq)
    butterhi = 1.0 - butterlow
    # ----------------------------------------------------------------- #
    tec_filt = np.fft.fftshift(np.fft.ifft(np.fft.ifftshift(np.multiply(tec_fft, butterhi))))
    Detrended_TEC = (np.real(tec_filt))

    # Return the detrendet TEC vector (y-axis values).
    return Detrended_TEC


def slant_to_vertical_tec(y_values, elevations, min_value, vertical_tec=0):
    # For every element in listforyaxisflt, convert to vertical TEC (if vertical
    # TEC==1) and do the night-subtraction.
    normalizedaxis = []
    if vertical_tec == 1:
        for i, e in enumerate(y_values):
            # This section uses geometry to get rid of the effects due to the variable
            # thickness of the atmosphere.
            minimumvaluetouse = min(float(s) for s in y_values)
            e -= minimumvaluetouse
            elevationtouse = elevations[i] * 0.0174533
            coselev = math.cos(elevationtouse)
            obliquity = 1 / (math.sqrt(1 - (0.947979 * coselev)))
            newelement = (e / obliquity) + minimumvaluetouse
            elementtoappend = newelement - min_value
            normalizedaxis.append(elementtoappend)
    else:
        normalizedaxis = [e - min_value for e in y_values]
    return normalizedaxis


def seconds_to_utc(y_values):
    newtimesUTC = []
    for numbertoconvert in y_values:  # Convert the times to UTC.
        numbertoconvert = float(numbertoconvert)  # 86400 sec = 1 day.

        if numbertoconvert >= 86400:
            remainder = numbertoconvert % 86400
            if remainder == 0:
                remainder = 86400
        elif numbertoconvert < 86400:
            remainder = numbertoconvert
        howmanyhoursflt = remainder / 3600  # Determine the amount of hours.
        newtimesUTC.append(howmanyhoursflt)
    return newtimesUTC


def plot(x_values, y_values, directory, graphname, title, subtitle, model):
    """"
    Function used for plotting and saving a graph.
    Inputs:
        file_type (string): One of the following: 'REDOBS', 'REDTEC', 'ismRawObs', 'ismRawOBS', 'ismDetObs',
                                                  'ismDetOBS', 'ismRawTEC' or 'ismRawTec'.
        graph_type (string): The type of graph that is being generated (e.g. 'Azymuth', or 'Tecdot')
        include_legend (boolean): Add a legend to the plot.
    Output:
        This function saves the plot to the predetermined directory, but the function itself does not return
        anything.
    """
    # If the user wants a legend, put it on the right, next to the graph. Then, plot.
    if model.legend:
        if model.summary_plot:
            plt.plot(x_values, y_values, label=str(model.savedPRNnumber), linewidth=0.4)
        else:
            plt.plot(x_values, y_values, label=str(model.savedPRNnumber))
    else:
        if model.summary_plot:
            plt.plot(x_values, y_values, linewidth=0.4)
        else:
            plt.plot(x_values, y_values)

    # For sigma only: compute the rate of change.
    if model.filetype == "REDOBS":
        if "secsigma" in model.graphtype:

            # If the maximum secsigma value > 100, set the y axis max to 3.
            if max(y_values) > 100:
                set_y_axis_range, y_axis_final_value = 1, 2

    # Add the X and Y-axis labels.
    plt.ylabel(str(model.graphtype) + " - " + str(model.units))
    plt.xlabel('Time (UTC)')

    # If graphtype is TECDOT, change the name to 'High Rate TEC Rate of change'.
    if model.graphtype == 'TECdot':
        graph_type = 'High Rate TEC Rate of change'

    # Change the limits of the axes based on line 20 and 21 of the GRAPHSETTINGS.csv file.
    if model.set_x_axis_range == 1:
        plt.xlim([model.x_axis_start_value, model.x_axis_final_value])
    if set_y_axis_range == 1:
        plt.ylim([model.y_axis_start_value, model.y_axis_final_value])

    # If the user wants to print a vertical line, use the axvline function - Line 29 of the GRAPHSETTINGS.csv file.
    if model.verticalline:
        plt.axvline(x=model.vertical_line_x_value, color='K', linewidth=0.5)

    # Label the plot lines (in-plot legends) - Line 25 of the GRAPHSETTINGS.csv file.
    if len(x_values) != 0:
        if model.PRNlabeling == 1:
            xdatapoint, ydatapoint = x_values[int(len(x_values) / 2)], y_values[int(len(y_values) / 2)]
            plt.text(xdatapoint, ydatapoint, model.savedPRNnumber)

    # Print the title and subtitle in the plot.
    plt.suptitle(title, fontsize=model.titlefontsize)
    plt.title(subtitle, fontsize=model.subtitlefontsize)

    # Set the directory, and create it if it does not exist.
    if model.summary_plot:
        ftype = "TEC" if model.filetype in ["REDTEC", 'ismRawTEC', 'ismRawTec'] else "OBS"
        directory = directory + filesep + "Summary_Plots" + filesep + ftype
    else:
        directory = directory + filesep + graph_type
    if not os.path.exists(directory):
        os.makedirs(directory)
    directory = directory + filesep + graphname

    # Print the directory in the command window.
    print(directory)

    # Print the legend on the plot if legend == True.
    if model.legend:
        plt.legend()

    # Save the figure.
    plt.savefig(directory)


    # If the summary plot option is not active, clear the graph.
    if not model.summary_plot:
        plt.clf()


def obtain_column_numbers(y):
    if y == "REDTEC" or y == "ismRawTEC" or y == "ismRawTec":
        variablesignal = 4
        variable = 20
        elevationvar = 6
    elif y == "REDOBS":
        variablesignal = 3
        variable = 20
        elevationvar = 5
    elif y == "ismRawObs" or y == "ismRawOBS" or y == "ismDetObs" or y == "ismDetOBS":
        variablesignal = 2
        variable = 9
        elevationvar = None
    return variable, variablesignal, elevationvar