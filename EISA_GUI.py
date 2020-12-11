"""

Embry-Riddle Ionospheric Scintillation Algorithm (EISA)
Version 2
Graphical User Interface

Embry-Riddle Aeronautical University 
Department of Physical Sciences
Space Physics Research Lab (SPRL)
Author: Nicolas Gachancipa

"""

# Imports
from EISA_objects import GraphSettings
from Graphing.graphing import run_graphing
import datetime
import wx


# Graphing panel.
class Graphing(wx.Panel):
    def __init__(self, parent, graph_settings):
        # Create panel & object.
        self.settings = graph_settings
        wx.Panel.__init__(self, parent)
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        # Obtain path to the input CSV files.
        text = wx.StaticText(self, label='Select the directory where the CSV files are located:')
        CSV_dir_btn = wx.DirPickerCtrl(self, wx.ID_ANY, self.settings.CSV_dir, u"Select a folder", wx.DefaultPosition,
                                       (550, 20), wx.DIRP_DEFAULT_STYLE)
        self.sizer.Add(text, 0, wx.ALL | wx.CENTER, 5)
        self.sizer.Add(CSV_dir_btn, 0, wx.ALL | wx.CENTER, 5)
        CSV_dir_btn.Bind(wx.EVT_DIRPICKER_CHANGED, self.set_csv_dir)

        # Obtain directory where the output plots are going to be saved.
        text = wx.StaticText(self, label='Select the directory where you want to save the plots:')
        output_dir_btn = wx.DirPickerCtrl(self, wx.ID_ANY, self.settings.output_dir, u"Select a folder",
                                          wx.DefaultPosition, (550, 20), wx.DIRP_DEFAULT_STYLE)
        self.sizer.Add(text, 0, wx.ALL | wx.CENTER, 5)
        self.sizer.Add(output_dir_btn, 0, wx.ALL | wx.CENTER, 5)
        output_dir_btn.Bind(wx.EVT_DIRPICKER_CHANGED, self.set_output_dir)

        # Obtain the file type (REDTEC, REDOBS, RAWTEC, or RAWOBS).
        text = wx.StaticText(self, label='Select the file type:')
        file_types = ['REDOBS - Reduced (low-rate) scintillation data.',
                      'REDTEC - Reduced (low-rate) TEC data.',
                      'RAWOBS - Raw (high-rate) scintillation data.',
                      'RAWTEC - Raw (high-rate) TEC data.']
        self.file_types_menu = wx.ComboBox(self, choices=file_types, value='REDTEC - Reduced (low-rate) TEC data.')
        self.sizer.Add(text, 0, wx.ALL | wx.CENTER, 5)
        self.sizer.Add(self.file_types_menu, 0, wx.ALL | wx.CENTER, 5)
        self.file_types_menu.Bind(wx.EVT_COMBOBOX_CLOSEUP, self.set_file_type)

        # Obtain the graph type.
        text = wx.StaticText(self, label='Select the graph type:')
        self.graph_types_menu = wx.ComboBox(self, choices=self.get_graph_choices(), value='Azimuth')
        self.sizer.Add(text, 0, wx.ALL | wx.CENTER, 5)
        self.sizer.Add(self.graph_types_menu, 0, wx.ALL | wx.CENTER, 5)
        self.graph_types_menu.Bind(wx.EVT_COMBOBOX_CLOSEUP, self.set_graph_type)

        # Obtain the date.
        text = wx.StaticText(self, label='Select the date that you want to process (year, month, day):')
        today = datetime.datetime.now()
        self.local_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.year = wx.ComboBox(self, choices=[str(today.year - i) for i in range(0, today.year - 2014)],
                                value=str(today.year))
        self.month = wx.ComboBox(self, choices=[str(13 - i) for i in range(1, 13)], value=str(today.month))
        self.day = wx.ComboBox(self,
                               choices=[str(i) for i in range(1, int(self.get_month_length(str(today.month))) + 1)],
                               value=str(today.day))
        self.sizer.Add(text, 0, wx.ALL | wx.CENTER, 5)
        self.local_sizer.Add(self.year, 0, wx.ALL | wx.CENTER, 5)
        self.local_sizer.Add(self.month, 0, wx.ALL | wx.CENTER, 5)
        self.local_sizer.Add(self.day, 0, wx.ALL | wx.CENTER, 5)
        self.sizer.Add(self.local_sizer, 0, wx.ALL | wx.CENTER, 5)
        self.year.Bind(wx.EVT_COMBOBOX_CLOSEUP, self.set_date)
        self.month.Bind(wx.EVT_COMBOBOX_CLOSEUP, self.set_month)
        self.day.Bind(wx.EVT_COMBOBOX_CLOSEUP, self.set_date)

        # Run EISA using the selected parameters.
        run_btn = wx.Button(self, label='Run EISA')
        self.sizer.Add(run_btn, 0, wx.ALL | wx.CENTER, 5)
        run_btn.Bind(wx.EVT_BUTTON, self.run)

        # Return to main menu.
        return_btn = wx.Button(self, label='Return')
        self.sizer.Add(return_btn, 0, wx.ALL | wx.CENTER, 5)
        return_btn.Bind(wx.EVT_BUTTON, parent.return_to_menu)

        # Show panel.
        self.SetSizer(self.sizer)
        self.Show(True)

    # Getters.
    def get_graph_choices(self):
        if self.settings.file_type == 'REDTEC':
            return self.settings.graph_types_REDTEC
        elif self.settings.file_type == 'REDOBS':
            return self.settings.graph_types_REDOBS
        elif self.settings.file_type == 'RAWOBS':
            return self.settings.graph_types_RAWOBS
        elif self.settings.file_type == 'RAWTEC':
            return self.settings.graph_types_RAWTEC
        else:
            print('Invalid file type.')

    def get_month_length(self, month):
        month_lengths = {'1': '31', '2': '29', '3': '31', '4': '30', '5': '31', '6': '30', '7': '31', '8': '31',
                         '9': '30', '10': '31', '11': '30', '12': '31', }
        return month_lengths[month]

    # Setters.
    def set_csv_dir(self, event):
        self.settings.CSV_dir = event.GetPath()

    def set_output_dir(self, event):
        self.settings.output_dir = event.GetPath()

    def set_file_type(self, _):
        self.settings.file_type = self.file_types_menu.GetStringSelection()[:6]
        self.graph_types_menu.Set(self.get_graph_choices())
        self.graph_types_menu.SetSelection(0)

    def set_graph_type(self, _):
        self.settings.graph_type = self.graph_types_menu.GetStringSelection()

    def set_month(self, _):
        # Update the days list corresponding to the selected month (e.g. January = 31 days).
        self.day.Set([str(i) for i in range(1, int(self.get_month_length(self.month.GetStringSelection())) + 1)])
        self.day.SetSelection(0)
        # Set the date.
        self.set_date(None)

    def set_date(self, _):

        # If one part of the date is not set, it must be defined by the code itself (default = today's date).
        today = datetime.datetime.now()
        if self.year.GetStringSelection() == "":
            self.year.SetStringSelection(str(today.year))
        if self.month.GetStringSelection() == "":
            self.month.SetStringSelection(str(today.month))
        if self.day.GetStringSelection() == "":
            self.day.SetStringSelection(str(today.day))

        # Update the model's date.
        self.settings.date = [self.year.GetStringSelection(), self.month.GetStringSelection(),
                              self.day.GetStringSelection()]

    def run(self, _):
        run_graphing(self.settings)


# Main window frame.
class TopFrame(wx.Frame):
    def __init__(self, graph_settings):
        super().__init__(parent=None, title='Embry-Riddle Ionospheric Scintillation Algorithm (EISA) v2.0',
                         size=(600, 175))

        # Create panel.
        self.settings = graph_settings
        self.panel = wx.Panel(self)
        self.my_sizer = wx.BoxSizer(wx.VERTICAL)

        # Run EISA (for today).
        my_btn = wx.Button(self.panel, label='Run EISA')
        self.my_sizer.Add(my_btn, 0, wx.ALL | wx.CENTER, 5)

        # EISA default values.
        my_btn_2 = wx.Button(self.panel, label='Modify parameters')
        self.my_sizer.Add(my_btn_2, 0, wx.ALL | wx.CENTER, 5)

        # Parsing settings.
        my_btn_3 = wx.Button(self.panel, label='Parsing')
        self.my_sizer.Add(my_btn_3, 0, wx.ALL | wx.CENTER, 5)

        # Graphing settings.
        my_btn_4 = wx.Button(self.panel, label='Graphing')
        self.my_sizer.Add(my_btn_4, 0, wx.ALL | wx.CENTER, 5)
        my_btn_4.Bind(wx.EVT_BUTTON, self.graph)

        # Show panel.
        self.panel.SetSizer(self.my_sizer)
        self.Center()
        self.Show(True)

    def graph(self, _):
        # Hide the main panel and display the graphing panel.
        self.panel.Hide()
        self.panel = Graphing(self, self.settings)
        self.my_sizer = wx.BoxSizer(wx.VERTICAL)
        self.my_sizer.Add(self.panel, 1, wx.EXPAND | wx.ALL | wx.CENTER, 2)

        # Fit to window's size.
        self.SetSizerAndFit(self.my_sizer)
        self.SetSize((600, 150))

    def return_to_menu(self, _):
        self.Hide()
        self.__init__(self.settings)


# Run program.
if __name__ == '__main__':
    # Program.
    app = wx.App()
    frame = TopFrame(GraphSettings())
    app.MainLoop()
