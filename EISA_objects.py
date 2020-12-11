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
import os
import datetime


# Graph settings (This object contains all the settings used to create plots).
class GraphSettings:
    def __init__(self):
        # Directories.
        self.CSV_dir = os.getcwd() + r'\EISA_OUTPUT\RX1\CSVFILES'
        self.output_dir = os.getcwd() + r'\EISA_OUTPUT\RX1\GRAPHS'

        # File and graph type (REDTEC and Azimuth as default)
        self.file_type = 'REDTEC'
        self.graph_type = 'Azimuth'

        # Date (Today as default)
        today = datetime.datetime.now()
        self.date = [today.year, today.month, today.day]

        # Predefined attributes.
        self.graph_types_REDTEC = ['Azimuth', 'Elevation', 'SecSig Lock', 'SecSig CNo', 'TEC15', 'TECRate15', 'TEC30',
                                   'TECRate30', 'TEC45', 'TECRate45', 'TECTOW', 'TECRateTOW']
        self.graph_types_REDOBS = ['Azimuth', 'Elevation', 'CNo', 'Lock Time', 'CMC avg', 'CMC std', 'S4', 'S4 Cor',
                                   '1secsigma', '3secsigma', '10secsigma', '30secsigma', '60secsigma']
        self.graph_types_RAWTEC = ['TEC', 'TECdot']
        self.graph_types_RAWOBS = ['ADR', 'Power']
