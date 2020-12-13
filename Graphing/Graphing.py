"""

Embry-Riddle Ionospheric Scintillation Algorithm (EISA)
Version 2
Graphing

Embry-Riddle Aeronautical University
Department of Physical Sciences
Space Physics Research Lab (SPRL)
Author: Nicolas Gachancipa

CREDITS:
The Butterworth filter used for TEC detrending was based on a Matlab function written by Dr. Kshitija Deshpande,
Professor of Engineering Physics at Embry-Riddle Aeronautical University.

"""
# External imports.
import os

# Internal imports.
from support_functions import (values_above_threshold, times_cross_elevation, extract_data,
                               filter_data, naming, tec_detrending, slant_to_vertical_tec, seconds_to_utc,
                               plot, obtain_column_numbers)

# Set the file separator to work in both Linux and Windows.
filesep = os.sep


# Functions.
def plot_prn(model, prn, normalize=0):
    # Set the directory to the output csv file.
    csv_to_graph = model.file_type + "_" + prn + "_" + model.get_date_str() + ".csv"
    csv_file = model.CSV_dir + filesep + csv_to_graph

    # -------------------------- SECTION: TIME RANGES ---------------------- #
    # For raw data files, extract the elevation column for the corresponding REDTEC file and determine a range of
    # times that are above the elevation threshold.
    if model.file_type in model.raw_data_types:
        reduced_file = model.CSV_dir + filesep + "REDTEC" + "_" + prn + "_" + model.get_date_str() + ".csv"
        if not os.path.isfile(reduced_file):
            return "Could not find the REDTEC file corresponding to the raw data."
    else:
        reduced_file = csv_file

    times_col, valid_col, _ = values_above_threshold(reduced_file, threshold=model.threshold, header=20, times_column=0,
                                                     elevations_column=6)
    starttimesflt, finaltimesflt = times_cross_elevation(times_col, valid_col)

    # ----------------- SECTION: EXTRACTING THE COLUMNS FROM THE CSV FILE ------------------- #
    # Import and read the csv (if it exists).
    if not os.path.isfile(csv_file):
        return "The following directory does not exist: " + csv_file
    header, signal_column, elev_column = obtain_column_numbers(model.filetype)
    data = extract_data(csv_file, header=header)
    filtered_data = filter_data(data, elev_column, ">=", model.threshold, [0, signal_column,
                                                                           elev_column,
                                                                           model.column])
    varsignaltypecolumn = [r[1] for r in filtered_data]

    # There are 7 types of signals (1 through 7).
    # Determine how many types of signals (and which ones) are present in the selected file.
    # Save the present signal types into a variable calles saves.
    saves = [it for it in range(1, 8) if it in list(map(int, varsignaltypecolumn))]

    # ---------------- SECTION: FOR LOOP FOR SIGNAL TYPE ------------------ #
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
            sttp = signal_types[prn[0]][str(signal_type)]

            # Name the plot.
            graph_name, directory, title, subtitle = naming(prn, sttp, normalize, i, model)

            # Plot.
            if len(yaxiscolumn) != 0:
                plot(times, yaxiscolumn, directory, graph_name, title, subtitle, model)


# ----------- GRAPHING ------------ #
def run_graphing(model):
    # Print start message to terminal.
    print("\n\n# --- " + model.file_type + ": Plotting Time vs. " + model.graph_type + " --- #")
    print('Date (year, month, day): {}, {}, {}'.format(model.date[0], model.date[1], model.date[2]))

    # Add a folder the output directory.
    model.output_dir = model.output_dir + filesep + model.get_date_str()
    print(model.output_dir)

    # Generate plots for the given date and PRNs.
    for prn in model.PRNs_to_plot:
        plot_prn(model, prn, normalize=0)

# ------------------------- SECTION 5: PLOTTING --------------------------- #
#    # Generate plots for the given date.
#    for prn in settings.PRNstograph:
#        plot_per_prn(settings, prn, normalize=0)
#    if settings.normalize_data == 1:
#        plt.clf()
#        for prn in settings.PRNstograph:
#            plot_per_prn(m, prn, normalize=1)
#
#    # Print message to the terminal.
#    print("The following day has been processed: " + settings.monthname + " " + str(settings.daynumber) +
#          " - Graph Type: " + str(graph_type) + " - Constellation: " + settings.constellationtype)
