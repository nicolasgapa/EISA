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
