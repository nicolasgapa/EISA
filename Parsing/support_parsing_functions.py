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
from gnsscal import gpswd2date
import ntpath
import os
import pandas as pd
from shutil import move
import subprocess

filesep = os.sep


def parse_file(binary_dir, output_dir, exe_dir, prns_to_parse, week_number, week_day_number, reduced_or_raw='reduced',
               time_range=False, start_time=0, end_time=24, print_header=True):
    """
    Function to parse a binary file and obtain CSV files.

    :param binary_dir: (str) Input (binary) file, including directory.
    :param output_dir: (str) Output directory, where the CSV files will be saved.
    :param exe_dir: (str) Directory to where the C++ and .exe parsing files are located (not including the name of the
                          files).
    :param prns_to_parse: (list) List of satellites to parse. For example: [G1, G10, R2, R5, E7, E14].
    :param week_number: (int) GPS Week.
    :param week_day_number: (int) Day of the week (i.e. 0: Monday, 1: Tuesday, ..., 6: Sunday).
    :param reduced_or_raw: (str) Either 'reduced' or 'raw'. Default: 'reduced'.
    :param time_range: (boolean) Parse a specific time range. Default: False.
    :param start_time: (float) If time_range is True, the start time of the time range to parse (in hours). Default: 0.
    :param end_time: (float) If time_range is True, the end time of the time range to parse (in hours). Default: 24.

    :return: boolean, str: Fist value indicates if the function ran properly (True) or not (False). Second value is
             a msg (string). If the first value is False, the error message indicates what went wrong.
             Moreover, the CSV Files are saved to the specified directory (output_dir).
    """
    # Obtain directory to the exe parsing files.
    if reduced_or_raw == 'reduced':
        exe_file = exe_dir + filesep + 'ParseReduced.exe'
        file_types = ['REDTEC', 'REDOBS']
    elif reduced_or_raw == 'raw':
        exe_file = exe_dir + filesep + 'ParseRaw.exe'
        file_types = ['ismRawTec', 'ismRawObs', 'ismDetObs']
    else:
        return False, "File type must be defined: Either 'reduced' or 'raw'."

    # Obtain the binary file name, from the directory.
    binary_file = ntpath.basename(binary_dir)

    # Determine if the binary file exists, otherwise return an error.
    if not os.path.exists(binary_dir):
        return False, 'The following binary file does not exist: {}.'.format(binary_dir)

    # The Raw file type names are modified when the CSV files are created. Define the new names (for later use).
    new_raw_names = {'ismRawTec': 'RAWTEC', 'ismRawObs': 'RAWOBS', 'ismDetObs': 'DETOBS'}

    # Obtain week number, day-of-the-week number, and date.
    date = gpswd2date(week_number, week_day_number)
    year, month, day = date.year, date.month, date.day

    # Add a trailing zero to the day (or month), if it is a number smaller than 10. Convert all values to strings. The
    # date string is used later to generate the names of the csv files.
    if day <= 9:
        day = "0" + str(day)
    if month <= 9:
        month = "0" + str(month)
    date_str = str(year) + str(month) + str(day)

    # Print intro log.
    if print_header:
        if reduced_or_raw == 'reduced':
            print('\n ----- GPStation-6 Reduced Observation Post-Processing Utility. Date: {} -----'.format(date))
        elif reduced_or_raw == 'raw':
            print('\n ----- GPStation-6 Raw Observation Post-Processing Utility. Date: {} -----'.format(date))

    # Parse the binary file for each of the selected satellites (PRNs). Keep track of the PRNs that are parsed.
    parsed_PRNs = []
    for satellite in prns_to_parse:

        # Obtain the command to run in the exe.
        CSV_name = binary_file + "_" + satellite + ".csv"
        exe_command = satellite + " " + binary_dir + " " + CSV_name

        # For raw files only: If the user selects a specific period of time to parse, add the parameter to the command.
        if time_range and reduced_or_raw == 'raw':
            start_time_GPS_TOW = week_day_number * 86400 + start_time * 3600
            end_time_GPS_TOW = week_day_number * 86400 + end_time * 3600
            exe_command = exe_command + " " + str(start_time_GPS_TOW) + " " + str(end_time_GPS_TOW) + " " + str(
                week_number) + " " + str(week_number)

        # Parse the file by running the command.
        subprocess.call(exe_file + ' ' + exe_command)

        # Process each of the file types (e.g. REDTEC and REDOBS for reduced files).
        for file_type in file_types:
            # Identify the name of the CSV file.
            csv_file = file_type + '_' + CSV_name

            # Process the csv file (if it exists). Otherwise, print an error message. The CSV file, which is the output
            # of the exe file is initially placed in the working directory.
            if os.path.exists(csv_file):
                # Open the CSV file.
                # print('Processing:', csv_file)
                DF = pd.read_csv(csv_file)

                # If the DF is empty, print an error msg.
                if len(DF) == 0:
                    os.remove(csv_file)
                    print('The following file (corresponding to satellite {}) was discarded, because it was '
                          'empty: {}. The file was deleted.'.format(satellite, CSV_name))
                    continue

                # Identify the directory where the new csv file will be saved (given by the user).
                new_csv_file_path = output_dir + filesep + date_str

                # Create the directory if it does not exist yet.
                if not os.path.exists(new_csv_file_path):
                    os.makedirs(new_csv_file_path)

                # Update the file type name (only for Raw file types).
                if reduced_or_raw == 'raw':
                    file_type = new_raw_names[file_type]

                # Create the new CSV file by moving the old file and renaming it.
                new_csv_file = new_csv_file_path + filesep + file_type + "_" + satellite + "_" + date_str + ".csv"
                move(csv_file, new_csv_file)
            else:
                print('The {} data corresponding to satellite {} could not be parsed'.format(file_type, satellite))

        # Add the parsed PRN to the list.
        parsed_PRNs.append(satellite)

    # Print return message.
    parsed_PRNs = ', '.join(parsed_PRNs) if parsed_PRNs else None
    print('Date: {} - The data of the following satellites was processed: {}.'.format(date, parsed_PRNs))

    # Return.
    return True, 'Success'
