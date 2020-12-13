"""
Other useful functions.
"""
# Imports.
import os
import csv
import numpy as np
import math
from scipy import signal
import operator
import matplotlib.pyplot as plt
import pandas as pd

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


def time_ranges(file, threshold=0, header=0, elev_col_name=' Elev', times_col_name='GPS TOW'):
    """
    This function is used to identify the different periods of time in which a satellite is over the given threshold.
    For example, if a satellite is above a given 30 degree threshold between 6-9 AM and 3-5PM, the function returns
    the following arrays: start_times = [6AM, 3PM] and end_times = [9AM, 5PM]. EISA creates one plot per period of time
    using the arrays returned by this function.

    :param file (string): Directory to the CSV file (including file name).
    :param threshold (float): Elevation threshold.
    :param header (int): Number of header rows in the CSV file (using Python indexing).
    :param elev_col_name (string): Name of the column that contains the elevation data.
    :param times_col_name (string): Name of the column that contains the timesteps.
    :return: start_times (list) and end_times (list): List of times when the satellite crosses the given threshold.
    """

    # Open the CSV file, and filter the data using the given elevation threshold.
    DF = pd.read_csv(file, header=header)
    filtered_DF = DF[DF[elev_col_name] >= threshold]
    filtered_DF = filtered_DF[[times_col_name, elev_col_name]]

    # Find the difference between one row and another.
    filtered_DF['Index difference'] = [2] + [x - y for x, y in zip(filtered_DF.index[1:], filtered_DF.index)]

    # Start rows (All those rows that have an index difference greater than 1 with respect to the previous row).
    # The difference > 1 indicates that the data was collected at a different time of the day, and the satellite
    # crossed the elevation theshold multiple times throughout the day.
    start_rows = filtered_DF[filtered_DF['Index difference'] > 1]
    start_times = list(start_rows[times_col_name])

    # End rows.
    end_times = []
    for index, row in start_rows.iloc[1:].iterrows():
        end_row = filtered_DF.loc[int(index - row['Index difference']), :]
        end_times.append(int(end_row[times_col_name]))
    end_times.append(int(filtered_DF.iloc[-1, :][times_col_name]))

    # Return.
    return start_times, end_times


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


def header_size(file_type):
    """
    Function to obtain the number of rows in the header of a CSV file (Output of a NovAtel GPStation 6).
    The function can be further modified for EISA to be capable of handling data from other receivers.

    :param file_type (string): File type (reduced/raw, or TEC/scintillation). E.g. "REDTEC"
    :return: header size (int): Number of rows in the header of such file.
    """
    if file_type == "REDTEC" or file_type == "ismRawTEC" or file_type == "ismRawTec" or file_type == "REDOBS":
        return 18
    elif file_type == "ismRawObs" or file_type == "ismRawOBS" or file_type == "ismDetObs" or file_type == "ismDetOBS":
        return 7
