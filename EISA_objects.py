"""

Embry-Riddle Ionospheric Scintillation Algorithm (EISA)
Version 2
Objects

Embry-Riddle Aeronautical University
Department of Physical Sciences
Space Physics Research Lab (SPRL)
Author: Nicolas Gachancipa

"""

# Imports
import datetime
import os
import pandas as pd


# Graph settings (This object contains all the settings used to create plots).
class GraphSettings:
    def __init__(self, predefined_settings='Graphing/graph_settings_default.csv'):

        # Open the settings CSV file.
        DF = pd.read_csv(predefined_settings)

        # Directories.
        self.CSV_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir)) + r'\EISA_OUTPUT\RX1\CSVFILES'
        self.output_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir)) + r'\EISA_OUTPUT\RX1\GRAPHS'

        # File and graph type (REDTEC and Azimuth as default)
        self.file_type = 'REDTEC'
        self.graph_type = 'Azimuth'

        # Date (Today as default)
        today = datetime.datetime.now()
        self.date = [today.year, today.month, today.day]
        self.date = [2020, 8, 22]

        # Select the PRNs to plot.
        self.PRNs_to_plot = []

        # Data pre-processing options.
        self.threshold = int(DF.iloc[0][0])

        # Other plot options.
        self.location = DF.iloc[23][0]
        self.summary_plot = False if int(DF.iloc[2][0]) == 0 else True
        self.TEC_detrending = False if int(DF.iloc[9][0]) == 0 else True
        self.night_subtraction = False if int(DF.iloc[4][0]) == 0 else True
        self.vertical_TEC = False if int(DF.iloc[17][0]) == 0 else True
        self.one_plot_per_prn = False if int(DF.iloc[27][0]) == 0 else True

        # Plot visual settings.
        self.set_x_axis_range = False if int(DF.iloc[6][0]) == 0 else True
        self.set_y_axis_range = False if int(DF.iloc[7][0]) == 0 else True
        self.x_axis_start_value = float(DF.iloc[6][1])
        self.x_axis_final_value = float(DF.iloc[6][2])
        self.y_axis_start_value = float(DF.iloc[7][1])
        self.y_axis_final_value = float(DF.iloc[7][2])
        self.vertical_line = False if int(DF.iloc[15][0]) == 0 else True
        self.x_value_vertical_line = float(DF.iloc[15][1])
        self.label_prns = False if int(DF.iloc[11][0]) == 0 else True
        self.title_font_size = float(DF.iloc[21][0])
        self.subtitle_font_size = float(DF.iloc[21][1])
        self.legend = False if int(DF.iloc[13][0]) == 0 else True
        self.format_type = DF.iloc[19][0]
        self.show_plots = False if int(DF.iloc[25][0]) == 0 else True

        # Predefined attributes (NovAtel GPStation-6 receiver).
        self.graph_types_REDTEC = ['Azimuth', 'Elevation', 'SecSig Lock Time', 'SecSig CNo', 'TEC15', 'TECRate15',
                                   'TEC30', 'TECRate30', 'TEC45', 'TECRate45', 'TECTOW', 'TECRateTOW']
        self.graph_types_REDOBS = ['Azimuth', 'Elevation', 'CNo', 'Lock Time', 'CMC Avg', 'CMC Std', "S4", "S4 Cor",
                                   "1SecSigma", "3SecSigma", "10SecSigma", "30SecSigma", "60SecSigma"]
        self.graph_types_RAWTEC = ['TEC', 'TECdot']
        self.graph_types_RAWOBS = ['ADR', 'Power']
        self.scintillation_types = ["S4", "S4 Cor", "1SecSigma", "3SecSigma", "10SecSigma", "30SecSigma", "60SecSigma"]
        self.TEC_types = ['TEC15', 'TEC30', 'TEC45', 'TECTOW', 'TEC']
        self.elevation_column_name = 'Elevation'
        self.times_column_name = 'GPS TOW'
        self.signal_column_name = 'SigType'
        self.signal_types = {"G": {"1": "L1CA", "4": "L2Y", "5": "L2C", "6": "L2P", "7": "L5Q"},
                             "R": {"1": "L1CA", "3": "L2CA", "4": "L2P"},
                             "E": {"1": "E1", "2": "E5A", "3": "E5B", "4": "AltBOC"}}
        self.units = {'Azimuth': '°', 'Elevation': '°', 'SecSig Lock Time': 'seconds',
                      'SecSig CNo': None, 'TEC15': 'TECU', 'TECRate15': 'TECU', 'TEC30': 'TECU',
                      'TECRate30': 'TECU', 'TEC45': 'TECU', 'TECRate45': 'TECU', 'TECTOW': 'TECU', 'TECRateTOW': 'TECU',
                      'CNo': None, 'Lock Time': 'seconds', 'CMC Avg': 'm.', 'CMC Std': 'm.', "S4": None, "S4 Cor": None,
                      "1SecSigma": 'radians', "3SecSigma": 'radians', "10SecSigma": 'radians', "30SecSigma": 'radians',
                      "60SecSigma": 'radians', 'TEC': 'TECU', 'TECdot': 'TECU', 'ADR': None, 'Power': None}

    def get_date_str(self):
        year, month, day = [str(i) for i in self.date]
        if len(month) == 1:
            month = '0' + str(month)
        if len(day) == 1:
            day = '0' + str(day)
        return year + month + day


# Parse settings (This object contains all the settings to parse binary files and create CSVs).
class ParseSettings:
    def __init__(self, predefined_settings='Parsing/parse_settings_default.csv'):
        # Open the settings CSV file.
        DF = pd.read_csv(predefined_settings)

        # Receiver name.
        self.receiver_name = DF.iloc[0][0]

        # Directories.
        self.binary_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir)) + '\\' + self.receiver_name
        self.CSV_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir)) + r'\EISA_OUTPUT\{}\GRAPHS'.format(
            self.receiver_name)

        # Dates.
        self.start_date = [2020, 8, 22]
        self.end_date = [2020, 8, 22]

        # File types.
        self.reduced = False if int(DF.iloc[2][0]) == 0 else True
        self.raw = False if int(DF.iloc[4][0]) == 0 else True

        # Select the PRNs to parse.
        self.PRNs_to_parse = []

        # Time range to parse.
        self.set_time_range = False if int(DF.iloc[6][0]) == 0 else True
        self.time_start_value = float(DF.iloc[6][1])
        self.time_end_value = float(DF.iloc[6][2])
