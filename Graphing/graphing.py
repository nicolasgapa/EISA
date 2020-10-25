import matplotlib.pyplot as plt
import os
import sys
from .support_classes import Plot_Options
from .support_functions import (options_menu, values_above_threshold, times_cross_elevation, extract_data,
                                filter_data, naming, tec_detrending, slant_to_vertical_tec, seconds_to_utc, plot,
                                obtain_column_numbers, validate_dates)
from .read_csv import read_graph_settings, read_paths_csv

filesep = os.sep

#  2018
#  Graphingmain.py code for ionospheric scintillation and Total Electron Content. BETA VERSION.
#  GPStation-6 multi-constellation receiver.
#  JOSE NICOLAS GACHANCIPA - Embry-Riddle Aeronautical University
#
# CREDITS
# The Butterworth filter used for TEC detrending was based on a Matlab function written by Dr. Kshitija Deshpande,
# Professor of Engineering Physics at Embry-Riddle Aeronautical University.
#
# DO NOT HARD CODE ANYTHING BELOW THIS POINT.

# ----------- SECTION 1: READING THE COMMAND WINDOW ARGUMENTS ------------- #
no_menu = user_selec = 0
if len(sys.argv) > 1:
    if sys.argv[1] == "no_menu":
        no_menu = 1
        user_selec = sys.argv[2]
else:
    print("The purpose of this code is to plot and save ionospheric scintillation and TEC graphs.")
    print("The directories can be changed by modifying the paths.csv file.")
    print("The settings can be changed by modifying the graphsettings.csv file.")
    # Set the file separator to work in both Linux and Windows.

# -------------------- SECTION 2: READING THE CSV FILES ------------------- #
outputfolderdirectory, graphsfolderdirectory = read_paths_csv()
m = Plot_Options(outputfolderdirectory, graphsfolderdirectory)
m, daymatrix, monthmatrix, yeari = read_graph_settings(m)
valid_dates = validate_dates(daymatrix, monthmatrix, yeari, outputfolderdirectory)

# --------------------- SECTION 3: PRINTING THE MENU ---------------------- #
graph_type, units, column = options_menu(m.file_type, no_menu, user_selec)


# ------------------------- SECTION 4: FUNCTIONS -------------------------- #
def plot_per_prn(model, prn, normalize=0):
    # Set the directory to the csv file.
    csvtograph = model.filetype + "_" + model.constellation + str(prn) + "_" + model.date + ".csv"
    csv_directory = model.directory + filesep + csvtograph

    # -------------------------- SECTION 4A: TIME RANGES ---------------------- #
    # For raw data files, extract the elevation column for the corresponding REDTEC file and determine a range of
    # times that are above the elevation threshold.
    if model.filetype in model.raw_data_types:
        reducedfile = model.directory + filesep + "REDTEC" + "_" + model.constellation + str(
            prn) + "_" + model.date + ".csv"
        if not os.path.isfile(reducedfile):
            return "Could not find the REDTEC file corresponding to the raw data."
    else:
        reducedfile = csv_directory
    times_col, valid_col, _ = values_above_threshold(reducedfile, threshold=m.threshold, header=20, times_column=0,
                                                     elevations_column=6)
    starttimesflt, finaltimesflt = times_cross_elevation(times_col, valid_col)

    # ----------------------- SECTION 4B: EXTRACTING THE COLUMNS FROM THE CSV FILE ---------------------------- #
    # Import and read the csv (if it exists).
    if not os.path.isfile(csv_directory):
        return "The following directory does not exist: " + csv_directory
    header, signal_column, elev_column = obtain_column_numbers(model.filetype)
    data = extract_data(csv_directory, header=header)
    filtered_data = filter_data(data, elev_column, ">=", model.threshold, [0, signal_column,
                                                                           elev_column,
                                                                           model.column])
    varsignaltypecolumn = [r[1] for r in filtered_data]

    # There are 7 types of signals (1 through 7).
    # Determine how many types of signals (and which ones) are present in the selected file.
    # Save the present signal types into a variable calles saves.
    saves = [it for it in range(1, 8) if it in list(map(int, varsignaltypecolumn))]

    # ----------------------- SECTION 4C: FOR LOOP D FOR SIGNAL TYPE ----------------------- #
    # FOR LOOP THAT REPEATS FOR EACH SIGNAL TYPE.
    for signal_type in saves:
        signal_data = filter_data(filtered_data, 2, "=", signal_type, [0, 2, 3])
        times, elevations, yaxiscolumn = [r[0] for r in signal_data], [r[1] for r in signal_data], [r[2] for r in
                                                                                                    signal_data]

        # START FOR LOOP THAT REPEATS FOR EVERY TIME PERIOD.
        for i, (timestartposition, timefinalposition) in enumerate(zip(starttimesflt, finaltimesflt)):

            # Cut the times and y-axis columns for the current time period.
            times = [it for c, it in enumerate(times, 1) if timestartposition <= c <= timefinalposition]
            yaxiscolumn = [it for c, it in enumerate(yaxiscolumn, 1) if timestartposition <= c <= timefinalposition]

            # For scintillation data, get rid of non-sense values (e.g. values above a value of 5).
            # These values may come from errors in the reciever/computer or signal interferencies and
            # are not representative of S4/sigma scintillation values.
            if model.graph_type in ["S4", "S4_Cor", "1secsigma", "3secsigma", "10secsigma", "30secsigma",
                                    "60secsigma"]:
                new_x = new_y = []
                for t, y_value in zip(times, yaxiscolumn):
                    if float(y_value) < 5:
                        new_x.append(t)
                        new_y.append(y_value)
                times, yaxiscolumn = new_x, new_y

            # ------------------------ SECTION 4D: TEC DETRENDING -------------------------- #
            # For TEC: If TECdetrending=1 in the GRAPHSETTINGS csv file, detrend the TEC data.
            if model.TECdetrending == 1 and model.filetype in model.raw_data_types:
                yaxiscolumn = tec_detrending(times, yaxiscolumn)

            # ------------------ SECTION 4E: NIGHT SUBTRACTION AND VERTICAL TEC ------------ #
            # Run this part of the code ONLY for low-rate TEC data.
            if model.filetype == "REDTEC":

                # Run this part of the code ONLY if listforyaxisflt is not an empty vector.
                if len(yaxiscolumn) > 0:

                    # When normalize==0 (regular data), select the minimum value.
                    if normalize == 0:

                        # After FOR LOOP  runs completely for the first time, it will calculate the
                        # minimum TEC value from ALL PRNs.
                        minimumvalueyaxis = min(float(s) for s in yaxiscolumn)
                        if minimumvalueyaxis < model.minimum:
                            model.minimum = minimumvalueyaxis

                    # When normalize==1 (i.e. when FOR LOOP B runs for the second time):
                    elif normalize == 1:
                        yaxiscolumn = slant_to_vertical_tec(yaxiscolumn, elevations, model.minimum,
                                                            vertical_tec=model.verticaltec)

            # Convert times to UTC.
            yaxiscolumn = [float(e) for e in yaxiscolumn]
            times = seconds_to_utc(times)

            # If the user is doing a summary plot add the shift value to every element in the
            # listforyaxisflt vector. See Section 1.
            if model.summaryplot:
                yaxiscolumn = [z + (prn * model.shiftvalue) for z in yaxiscolumn]

            # Determine the signal type (L1, L2, ETC).
            signal_types = {"G": {"1": "L1CA", "4": "L2Y", "5": "L2C", "6": "L2P", "7": "L5Q"},
                            "R": {"1": "L1CA", "3": "L2CA", "4": "L2P"},
                            "E": {"1": "E1", "2": "E5A", "3": "E5B", "4": "AltBOC"}}
            sttp = signal_types[model.constellation][str(signal_type)]

            # Name the plot.
            graph_name, directory, title, subtitle = naming(prn, sttp, normalize, i, model)

            # Plot.
            if len(yaxiscolumn) != 0:
                plot(times, yaxiscolumn, directory, graph_name, title, subtitle, model)


# ------------------------- SECTION 5: PLOTTING --------------------------- #
for date in valid_dates:

    # Print start messate to terminal.
    print("\n\n# --- " + m.file_type + ": Plotting Time vs. " + graph_type + " --- #\n\n")
    m.set_date(date)

    # Generate plots for the given date.
    for prn in m.PRNstograph:
        plot_per_prn(m, prn, normalize=0)
    if m.normalize_data == 1:
        plt.clf()
        for prn in m.PRNstograph:
            plot_per_prn(m, prn, normalize=1)

    # Print message to the terminal.
    print("The following day has been processed: " + m.monthname + " " + str(m.daynumber) +
          " - Graph Type: " + str(graph_type) + " - Constellation: " + m.constellationtype)
