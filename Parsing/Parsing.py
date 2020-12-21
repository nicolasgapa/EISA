# Import modules.
import os
import time
from datetime import date, timedelta
from gnsscal import date2gpswd
from Parsing.support_parsing_functions import parse_file

filesep = os.sep

start_time = time.time()


def parse_binary_file(binary_file, model):
    # Obtain directory to file.
    week_number, week_day_number = int(binary_file[:4]), int(binary_file[5])
    binary_dir = model.binary_dir + filesep + str(week_number) + filesep + binary_file

    # Determine if the file exists within binary_dir. Otherwise, return an error.
    if model.reduced:
        success, msg = parse_file(binary_dir, model.CSV_dir, os.getcwd(), model.PRNs_to_parse, week_number,
                                  week_day_number, time_range=model.set_time_range, start_time=model.time_start_value,
                                  end_time=model.time_end_value)
        if not success:
            return False, msg
    if model.raw:
        success, msg = parse_file(binary_dir, model.CSV_dir, os.getcwd(), model.PRNs_to_parse, week_number,
                                  week_day_number, reduced_or_raw='raw', time_range=model.set_time_range,
                                  start_time=model.time_start_value, end_time=model.time_end_value)
        if not success:
            return False, msg
    return True, 'Success'


# ----------- PARSING (NovAtel receivers only) ------------ #
def run_parsing(model):
    # Process the dates. Obtain the names of the binary files.
    start_year, start_month, start_day = model.start_date
    end_year, end_month, end_day = model.end_date
    number_of_days = (date(end_year, end_month, end_day) - date(start_year, start_month, start_day)).days
    if number_of_days < 0:
        print('Error: The selected end date must be after the start date.')
    days = [date(start_year, start_month, start_day) + timedelta(days=i) for i in range(number_of_days + 1)]
    binary_files = [str(date2gpswd(day)[0]) + '_' + str(date2gpswd(day)[1]) + '_00_' + model.receiver_name + '.GPS' for
                    day in days]

    # Parse the binary files.
    for binary_file in binary_files:

        # Parse file.
        success, error = parse_binary_file(binary_file, model)
        if not success:
            print(error)
