import csv
from .support_functions import dates
import os

filesep = os.sep


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
