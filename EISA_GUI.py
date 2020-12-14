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
from Graphing import run_graphing
import datetime
import wx


# Graphing panel.
class Graphing(wx.Panel):

    # Initializer.
    def __init__(self, parent, graph_settings):
        # Create panel & object.
        self.settings = graph_settings
        wx.Panel.__init__(self, parent)
        self.container = wx.BoxSizer(wx.VERTICAL)
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

        # PRNs - Select all.
        text = wx.StaticText(self, label='Select the satellites that you want to plot: \n'
                                         'G: GPS, R: GLONASS, E: GALILEO')
        text_2 = wx.StaticText(self, label='Select all:')
        self.sizer.Add(text, 0, wx.ALL | wx.CENTER, 5)
        self.local_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.local_sizer.Add(text_2, 0, wx.ALL | wx.CENTER, 5)
        self.GPS_check = wx.CheckBox(self, label="G")
        self.GLONASS_check = wx.CheckBox(self, label="R")
        self.GALILEO_check = wx.CheckBox(self, label="E")
        self.local_sizer.Add(self.GPS_check, 0, wx.ALL | wx.CENTER, 5)
        self.local_sizer.Add(self.GLONASS_check, 0, wx.ALL | wx.CENTER, 5)
        self.local_sizer.Add(self.GALILEO_check, 0, wx.ALL | wx.CENTER, 5)
        self.sizer.Add(self.local_sizer, 0, wx.ALL | wx.CENTER, 5)
        self.GPS_check.Bind(wx.EVT_CHECKBOX, self.set_GPS_PRNs)
        self.GLONASS_check.Bind(wx.EVT_CHECKBOX, self.set_GLONASS_PRNs)
        self.GALILEO_check.Bind(wx.EVT_CHECKBOX, self.set_GALILEO_PRNs)

        # PRNs - Select individual satellites.
        self.local_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.GPS_satellites_menu = wx.ListBox(self, style=wx.LB_MULTIPLE, choices=['G' + str(i) for i in range(1, 33)])
        self.GLONASS_satellites_menu = wx.ListBox(self, style=wx.LB_MULTIPLE,
                                                  choices=['R' + str(i) for i in range(1, 25)])
        self.GALILEO_satellites_menu = wx.ListBox(self, style=wx.LB_MULTIPLE,
                                                  choices=['E' + str(i) for i in range(1, 31)])
        self.local_sizer.Add(self.GPS_satellites_menu, 0, wx.ALL | wx.CENTER, 5)
        self.local_sizer.Add(self.GLONASS_satellites_menu, 0, wx.ALL | wx.CENTER, 5)
        self.local_sizer.Add(self.GALILEO_satellites_menu, 0, wx.ALL | wx.CENTER, 5)
        self.sizer.Add(self.local_sizer, 0, wx.ALL | wx.CENTER, 5)
        self.GPS_satellites_menu.Bind(wx.EVT_LISTBOX, self.set_PRNs_to_plot)
        self.GLONASS_satellites_menu.Bind(wx.EVT_LISTBOX, self.set_PRNs_to_plot)
        self.GALILEO_satellites_menu.Bind(wx.EVT_LISTBOX, self.set_PRNs_to_plot)

        # Threshold.
        text = wx.StaticText(self, label='Select the elevation threshold:')
        self.threshold_slider = wx.Slider(self, value=30, minValue=0, maxValue=90, style=wx.SL_LABELS)
        self.sizer.Add(text, 0, wx.ALL | wx.CENTER, 5)
        self.sizer.Add(self.threshold_slider, 0, wx.ALL | wx.CENTER | wx.EXPAND, 5)
        self.threshold_slider.Bind(wx.EVT_SCROLL, self.set_threshold)

        """
        Other Options
        """
        # Sizer 2.
        self.sizer_2 = wx.BoxSizer(wx.VERTICAL)
        text = wx.StaticText(self, label='Other options:')
        self.sizer_2.Add(text, 0, wx.ALL | wx.CENTER, 5)

        # Location.
        self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        text = wx.StaticText(self, label='Location:')
        self.location_text = wx.TextCtrl(self, value=self.settings.location, size=(150, 20))
        self.location_text.SetFocus()
        self.hbox1.Add(text, 0, wx.ALL | wx.CENTER, 5)
        self.hbox1.Add(self.location_text, 0, wx.ALL | wx.CENTER | wx.EXPAND, 5)
        self.sizer_2.Add(self.hbox1, 0, wx.ALL | wx.CENTER, 5)
        self.location_text.Bind(wx.EVT_TEXT, self.set_location)

        # Summary plot.
        self.summary_plot_check = wx.CheckBox(self, label="Summary plot")
        self.sizer_2.Add(self.summary_plot_check, 0, wx.ALL | wx.CENTER, 5)
        self.summary_plot_check.Bind(wx.EVT_CHECKBOX, self.set_summary_plot)

        # TEC Detrending (Only for Raw Data).
        self.TEC_detrending_check = wx.CheckBox(self, label="TEC Detrending (Only for high-rate TEC data)")
        self.sizer_2.Add(self.TEC_detrending_check, 0, wx.ALL | wx.CENTER, 5)
        self.TEC_detrending_check.Bind(wx.EVT_CHECKBOX, self.set_TEC_detrending)

        # Night subtraction (Low-rate TEC only).
        self.night_subtraction_check = wx.CheckBox(self, label="Night Subtraction (Only for low-rate TEC data)")
        self.sizer_2.Add(self.night_subtraction_check, 0, wx.ALL | wx.CENTER, 5)
        self.night_subtraction_check.Bind(wx.EVT_CHECKBOX, self.set_night_subtraction)

        # Vertical TEC (Low-rate TEC only).
        self.vertical_TEC_check = wx.CheckBox(self, label="Vertical TEC (Only for low-rate TEC data)")
        self.sizer_2.Add(self.vertical_TEC_check, 0, wx.ALL | wx.CENTER, 5)
        self.vertical_TEC_check.Bind(wx.EVT_CHECKBOX, self.set_vertical_TEC)

        """
        Plot visual settings.
        """

        # Plot visual settings.
        text = wx.StaticText(self, label='\n\nPlot visual settings:')
        self.sizer_2.Add(text, 0, wx.ALL | wx.CENTER, 5)

        # Label PRNs on the plot.
        self.label_prns_check = wx.CheckBox(self, label="Label PRNs")
        self.sizer_2.Add(self.label_prns_check, 0, wx.ALL | wx.CENTER, 5)
        self.label_prns_check.Bind(wx.EVT_CHECKBOX, self.set_label_prns)

        # Show legend.
        self.legend_check = wx.CheckBox(self, label="Include legend")
        self.sizer_2.Add(self.legend_check, 0, wx.ALL | wx.CENTER, 5)
        self.legend_check.Bind(wx.EVT_CHECKBOX, self.set_legend)

        # Title font size.
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        text = wx.StaticText(self, label='Title font size:')
        self.title_font_size_text = wx.TextCtrl(self, self.settings.title_font_size, size=(35, 20))
        self.hbox.Add(text, 0, wx.ALL | wx.CENTER, 5)
        self.hbox.Add(self.title_font_size_text, 0, wx.ALL | wx.CENTER, 5)
        self.sizer_2.Add(self.hbox, 0, wx.ALL | wx.CENTER, 5)
        self.title_font_size_text.Bind(wx.EVT_TEXT, self.set_title_font_size)

        # Subtitle font size.
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        text = wx.StaticText(self, label='Subtitle font size:')
        self.subtitle_font_size_text = wx.TextCtrl(self, self.settings.subtitle_font_size, size=(35, 20))
        self.hbox.Add(text, 0, wx.ALL | wx.CENTER, 5)
        self.hbox.Add(self.subtitle_font_size_text, 0, wx.ALL | wx.CENTER, 5)
        self.sizer_2.Add(self.hbox, 0, wx.ALL | wx.CENTER, 5)
        self.subtitle_font_size_text.Bind(wx.EVT_TEXT, self.set_subtitle_font_size)

        # X-axis limits.
        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        text = wx.StaticText(self, label='X-axis range:')
        text2 = wx.StaticText(self, label='min:')
        text3 = wx.StaticText(self, label='max:')
        self.x_axis_limits_check = wx.CheckBox(self)
        self.x_axis_min = wx.TextCtrl(self, self.settings.x_axis_start_value, size=(35, 20))
        self.x_axis_max = wx.TextCtrl(self, self.settings.x_axis_final_value, size=(35, 20))
        self.hbox2.Add(text, 0, wx.ALL | wx.CENTER, 5)
        self.hbox2.Add(self.x_axis_limits_check, 0, wx.ALL | wx.CENTER, 5)
        self.hbox2.Add(text2, 0, wx.ALL | wx.CENTER, 5)
        self.hbox2.Add(self.x_axis_min, 0, wx.ALL | wx.CENTER, 5)
        self.hbox2.Add(text3, 0, wx.ALL | wx.CENTER, 5)
        self.hbox2.Add(self.x_axis_max, 0, wx.ALL | wx.CENTER, 5)
        self.sizer_2.Add(self.hbox2, 0, wx.ALL | wx.CENTER, 5)
        self.x_axis_limits_check.Bind(wx.EVT_CHECKBOX, self.set_x_axis_limit_check)
        self.x_axis_min.Bind(wx.EVT_TEXT, self.set_x_axis_start_value)
        self.x_axis_max.Bind(wx.EVT_TEXT, self.set_x_axis_final_value)

        # Y-axis limits.
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        text = wx.StaticText(self, label='Y-axis range:')
        text2 = wx.StaticText(self, label='min:')
        text3 = wx.StaticText(self, label='max:')
        self.y_axis_limits_check = wx.CheckBox(self)
        self.y_axis_min = wx.TextCtrl(self, self.settings.y_axis_start_value, size=(35, 20))
        self.y_axis_max = wx.TextCtrl(self, self.settings.y_axis_final_value, size=(35, 20))
        self.hbox.Add(text, 0, wx.ALL | wx.CENTER, 5)
        self.hbox.Add(self.y_axis_limits_check, 0, wx.ALL | wx.CENTER, 5)
        self.hbox.Add(text2, 0, wx.ALL | wx.CENTER, 5)
        self.hbox.Add(self.y_axis_min, 0, wx.ALL | wx.CENTER, 5)
        self.hbox.Add(text3, 0, wx.ALL | wx.CENTER, 5)
        self.hbox.Add(self.y_axis_max, 0, wx.ALL | wx.CENTER, 5)
        self.sizer_2.Add(self.hbox, 0, wx.ALL | wx.CENTER, 5)
        self.y_axis_limits_check.Bind(wx.EVT_CHECKBOX, self.set_y_axis_limit_check)
        self.y_axis_min.Bind(wx.EVT_TEXT, self.set_y_axis_start_value)
        self.y_axis_max.Bind(wx.EVT_TEXT, self.set_y_axis_final_value)

        # Vertical line.
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        text = wx.StaticText(self, label='Vertical line:')
        text2 = wx.StaticText(self, label='X-value:')
        self.vertical_line_check = wx.CheckBox(self)
        self.x_value_vertical_line_text = wx.TextCtrl(self, self.settings.x_value_vertical_line, size=(35, 20))
        self.hbox.Add(text, 0, wx.ALL | wx.CENTER, 5)
        self.hbox.Add(self.vertical_line_check, 0, wx.ALL | wx.CENTER, 5)
        self.hbox.Add(text2, 0, wx.ALL | wx.CENTER, 5)
        self.hbox.Add(self.x_value_vertical_line_text, 0, wx.ALL | wx.CENTER, 5)
        self.sizer_2.Add(self.hbox, 0, wx.ALL | wx.CENTER, 5)
        self.vertical_line_check.Bind(wx.EVT_CHECKBOX, self.set_vertical_line)
        self.x_value_vertical_line_text.Bind(wx.EVT_TEXT, self.set_x_value_vertical_line)

        # Format type (png, pdf, jpg, etc).
        text = wx.StaticText(self, label='Select the plot format type:')
        self.format_type_check = wx.ComboBox(self, choices=['png', 'pdf', 'jpg'], value=self.settings.format_type)
        self.sizer_2.Add(text, 0, wx.ALL | wx.CENTER, 5)
        self.sizer_2.Add(self.format_type_check, 0, wx.ALL | wx.CENTER, 5)
        self.format_type_check.Bind(wx.EVT_COMBOBOX_CLOSEUP, self.set_format_type)

        # Show plots in the screen.
        self.show_plots_check = wx.CheckBox(self, label="Show plots")
        self.sizer_2.Add(self.show_plots_check, 0, wx.ALL | wx.CENTER, 5)
        self.show_plots_check.Bind(wx.EVT_CHECKBOX, self.set_show_plots)

        """
        Run EISA, or return to main menu.
        """

        # Run EISA using the selected parameters.
        run_btn = wx.Button(self, label='Run EISA')
        run_btn.Bind(wx.EVT_BUTTON, self.run)

        # Return to main menu.
        return_btn = wx.Button(self, label='Return')
        return_btn.Bind(wx.EVT_BUTTON, parent.return_to_menu)

        # Place everything into the container.
        self.options = wx.BoxSizer(wx.HORIZONTAL)
        self.options.Add(self.sizer, 0, wx.ALL | wx.CENTER, 5)
        self.options.Add(wx.StaticLine(self, -1, size=(3, 600), style=wx.LI_VERTICAL), 0, wx.ALL | wx.CENTER, 5)
        self.options.Add(self.sizer_2, 0, wx.ALL | wx.CENTER, 5)
        self.container.Add(self.options, 0, wx.ALL | wx.CENTER, 5)
        self.container.Add(run_btn, 0, wx.ALL | wx.CENTER, 5)
        self.container.Add(return_btn, 0, wx.ALL | wx.CENTER, 5)

        # Show panel.
        self.SetSizer(self.container)
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

    def set_GPS_PRNs(self, _):

        # GPS.
        for i in range(32):
            if self.GPS_check.IsChecked():
                self.GPS_satellites_menu.SetSelection(i)
            else:
                if i in self.GPS_satellites_menu.GetSelections():
                    self.GPS_satellites_menu.Deselect(i)

        # Set PRNs.
        self.set_PRNs_to_plot(None)

    def set_GLONASS_PRNs(self, _):

        # GLONASS.
        for i in range(24):
            if self.GLONASS_check.IsChecked():
                self.GLONASS_satellites_menu.SetSelection(i)
            else:
                if i in self.GLONASS_satellites_menu.GetSelections():
                    self.GLONASS_satellites_menu.Deselect(i)

        # Set PRNs.
        self.set_PRNs_to_plot(None)

    def set_GALILEO_PRNs(self, _):

        # GALILEO.
        for i in range(30):
            if self.GALILEO_check.IsChecked():
                self.GALILEO_satellites_menu.SetSelection(i)
            else:
                if i in self.GALILEO_satellites_menu.GetSelections():
                    self.GALILEO_satellites_menu.Deselect(i)

        # Set PRNs.
        self.set_PRNs_to_plot(None)

    def set_PRNs_to_plot(self, _):
        GPS_selections = ['G' + str(i + 1) for i in self.GPS_satellites_menu.GetSelections()]
        GLONASS_selections = ['R' + str(i + 1) for i in self.GLONASS_satellites_menu.GetSelections()]
        GALILEO_selections = ['E' + str(i + 1) for i in self.GALILEO_satellites_menu.GetSelections()]
        self.settings.PRNs_to_plot = GPS_selections + GLONASS_selections + GALILEO_selections

    def set_threshold(self, _):
        self.settings.threshold = self.threshold_slider.GetValue()

    def set_TEC_detrending(self, _):
        self.settings.TEC_detrending = self.TEC_detrending_check.IsChecked()

    def set_night_subtraction(self, _):
        self.settings.night_subtraction = self.night_subtraction_check.IsChecked()

    def set_vertical_TEC(self, _):
        self.settings.vertical_TEC = self.vertical_TEC_check.IsChecked()

    def set_summary_plot(self, _):
        self.settings.summary_plot = self.summary_plot_check.IsChecked()

    def set_location(self, _):
        self.settings.location = self.location_text.GetLineText(0)

    def set_x_axis_limit_check(self, _):
        self.settings.set_x_axis_range = self.x_axis_limits_check.IsChecked()

    def set_x_axis_start_value(self, _):
        self.settings.x_axis_start_value = self.x_axis_min.GetLineText(0)

    def set_x_axis_final_value(self, _):
        self.settings.x_axis_final_value = self.x_axis_max.GetLineText(0)

    def set_y_axis_limit_check(self, _):
        self.settings.set_y_axis_range = self.y_axis_limits_check.IsChecked()

    def set_y_axis_start_value(self, _):
        self.settings.y_axis_start_value = self.y_axis_min.GetLineText(0)

    def set_y_axis_final_value(self, _):
        self.settings.y_axis_final_value = self.y_axis_max.GetLineText(0)

    def set_vertical_line(self, _):
        self.settings.vertical_line = self.vertical_line_check.IsChecked()

    def set_x_value_vertical_line(self, _):
        self.settings.x_value_vertical_line = self.x_value_vertical_line_text.GetLineText(0)

    def set_label_prns(self, _):
        self.settings.label_prns = self.label_prns_check.IsChecked()

    def set_title_font_size(self, _):
        self.settings.title_font_size = self.title_font_size_text.GetLineText(0)

    def set_subtitle_font_size(self, _):
        self.settings.subtitle_font_size = self.subtitle_font_size_text.GetLineText(0)

    def set_legend(self, _):
        self.settings.legend = self.legend_check.IsChecked()

    def set_format_type(self, _):
        self.settings.format_type = self.format_type_check.GetStringSelection()

    def set_show_plots(self, _):
        self.settings.show_plots = self.show_plots_check.IsChecked()

    def run(self, _):
        # Catch selection errors. Run only if all stteings have been properly selected.
        if len(self.settings.PRNs_to_plot) == 0:
            wx.MessageDialog(self, 'Error: Please select at least one satellite (PRN) to continue.').ShowModal()
        else:
            run_graphing(self.settings)


# Main window frame.
class TopFrame(wx.Frame):

    # Initializer.
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

    # Graphing.
    def graph(self, _):
        # Hide the main panel and display the graphing panel.
        self.panel.Hide()
        self.my_sizer = wx.BoxSizer(wx.VERTICAL)
        self.my_sizer.Add(Graphing(self, self.settings), 1, wx.EXPAND | wx.ALL, 2)

        # Fit to window's size.
        self.SetSizerAndFit(self.my_sizer)
        self.Center()

    # Retunr to main menu.
    def return_to_menu(self, _):
        self.Hide()
        self.__init__(self.settings)


# Run program.
if __name__ == '__main__':
    # Program.
    app = wx.App()
    frame = TopFrame(GraphSettings(predefined_settings='Graphing/graph_settings_default.csv'))
    app.MainLoop()
