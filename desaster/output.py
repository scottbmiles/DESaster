# Outputs for the DESaster discrete disaster simulation package (github.com/milessb/DESaster)
# Ostin Kurniawan, March 2018
# Requires: numpy, pandas, uszipcode, bokeh==0.12.9
# Only works for US-based locales

# Usage #
# def __init__(self, source, desiredStates, statusOrder, simTime, outputFileName, zipFilter=None)
#
# where:
# source – the data source either as a path to a CSV or a passed DataFrame
#       column requirements: relevant statuses, 'latitude', 'longitude', 'damage_state_start'
# desiredStates – an ordered list of just the desired home statuses from the source.
#       e.g. ['inspection_get', 'assistance_get', 'assessment_get', 'permit_get', 'claim_get', 'loan_get', 'home_get']
# simTime – how much of the simulation you want to process to
# outputFileName – string representing path to desired file or just the file name
# zipFilter – the ZIP code to filter by. If it is not provided or is passed None, it processes the entire data source
# mapHoverOptions – a list of column names from the data source that are desired for output in the hover tooltips. default: ['story']
#
# And the three main functions:
# getUniqueZipcodes() — prints the unique ZIP codes contained within the data
# filterByZip(zipcode) — re-filters the data by the provided zipcode (string format)
# visualize() — generate the visualisation!
# exportVisData(filepath) – export the current vis data (statuses of each entity by day) to CSV

# sample use:
# from output import *
# states = ['inspection_get', 'assistance_get', 'assessment_get', 'permit_get', 'claim_get', 'loan_get', 'home_get']
# a = Output("~/Desktop/data.csv", states, 140, "plotme.html")
# a.getUniqueZipcodes()
# a.filterByZip(97103)
# a.visualize()
# a.exportVisData()

import numpy as np
import pandas as pd
from uszipcode import ZipcodeSearchEngine

from bokeh.models import BooleanFilter, CDSView, CustomJS, Slider, ColumnDataSource, ranges, HoverTool, GMapPlot, GMapOptions, Circle, DataRange1d, PanTool, WheelZoomTool
from bokeh.io import output_file, show
from bokeh.layouts import column, row, gridplot, layout
from bokeh.plotting import figure
import bokeh.palettes

class Output():

    def __init__(self, source, desiredStates, simTime, outputFileName, zipFilter=None, mapHoverOptions=['story']):

        # Passed Parameters #

        self._allData = self._loadData(source)
        self._desiredStates = desiredStates
        self._statuses = ['no_status'] + self._desiredStates + ['latitude', 'longitude', 'zip', 'damage_state_start']
        self._simTime = simTime
        self._outputFileName = outputFileName
        self._desiredZipcode = zipFilter
        self._mapHoverOptions = mapHoverOptions

        # Check that all parameters are valid #

        self._checkParams()
        self._checkStateValidity()

        # Further Processing #

        # Sizing for intitial Damage States
        self._damageStates = {'None':6, 'Slight':8, 'Moderate':10, 'Extensive':12, 'Complete':14}

        # States that will be outputted
        self._desiredStates_ns = (['no_status'] + self._desiredStates)

        # Global counts
        self._numCategories = len(self._desiredStates_ns)
        self._numHomes = self._allData.shape[0]

        # Generate the colors based on the number of categories
        self._colorsOnly = bokeh.palettes.d3['Category20'][self._numCategories]
        self._assignedColors = self._assignColors() #assign colors to categories

        # Generate zipcodes
        self._zipSearch = ZipcodeSearchEngine()
        self._allData['zip'] = self._allData.apply(self._getZipcode, axis = 1)
        self._uniqueZipcodes = sorted(self._allData['zip'].unique().tolist())

        # Filter data
        self._filteredData = self._filterByZip(zipFilter).reset_index(drop=True)
        self._filteredNumHomes = len(self._filteredData)
        self._onlyStateData = self._filteredData[desiredStates].reset_index(drop=True)


        if self._desiredZipcode is None:
            print("Entire data source will be processed.")
            print("If you would like to filter the data by a specific ZIP code:\nUse getUniqueZipcodes() to get a list of unique ZIP codes or use filterByZip({ZIPCODE}) to filter the data.")
        else:
            print("Data is currently filtered by the following ZIP code: " + str(zipFilter))
            print("If you would like to filter the data by a differnt ZIP code:\nUse getUniqueZipcodes() to get a list of unique ZIP codes or use filterByZip({ZIPCODE}) to filter the data.")

        self._run()

    def _checkParams(self):
        if (type(self._outputFileName) != str) or (self._outputFileName[-5:] != ".html"):
            raise BaseException("Invalid output file name. Output file name must end in '.html'")
        if type(self._simTime) != int:
            raise BaseException("Invalid simulation time. Simulation time must be an integer.")

    def _checkStateValidity(self):
        missing = [state for state in self._desiredStates if state not in self._statuses]
        if (len(missing) != 0):
            raise BaseException("Elements of the state order must also be in the desired state list.\nCurrent inconsistencies: ", missing)

    # Initialisation: Data sources.
    # returns None if there is an invalid source.
    def _loadData(self, source):
        if type(source) is str:
            try:
                return pd.read_csv(source)
            except BaseException as e:
                print("Unsupported file type or file was not found.")
                return None
        elif type(source) is pandas.core.frame.DataFrame:
            try:
                return source
            except BaseException as e:
                print("Error loading DataFrame. ", e)
                return None

    # Initialisation: Assign colors to desired data categories.
    # returns a dictionary in form {state:color}
    def _assignColors(self):
        colors = {}
        for i in range(0, len(self._desiredStates_ns)):
            colors[self._statuses[i]] = self._colorsOnly[i]
        return colors

    # Initialisation: Find the zipcode based on lat/long.
    # This method is used in DataFrame.apply
    def _getZipcode(self, data):
        lat = data['latitude']
        lng = data['longitude']
        zipcode = self._zipSearch.by_coordinate(lat, lng, returns=1)[0]['Zipcode']
        zipcode = int(zipcode)
        return zipcode

    # Initialisation: Filter the data source by the desired ZIP code
    def _filterByZip(self, desiredZipcode):
        if desiredZipcode is None:
            return self._allData
        elif int(desiredZipcode) in self._uniqueZipcodes:
            fltr = self._allData['zip'] == desiredZipcode
            return self._allData[fltr]
        else:
            raise TypeError('Invalid Zipcode. Zipcodes currently available: ' + str(self._uniqueZipcodes) +
            "\nIf you would like to process the entire data source, pass None")

    # Initialisation: Generate a DataFrame that shows the status of every entity
    # at every point of time.
    # returns a single DataFrame
    def _generateHomeStatus(self):
        home_status_list = []
        for i in range(1, self._simTime):
            single_home_status = np.empty(shape = [self._onlyStateData.shape[0],1], dtype = object)
            curr_max = i
            curr = 0
            for row in self._onlyStateData.itertuples(index = False):
                row_asDict = row._asdict()
                try:
                    mostRecentTime = max(value for name, value in row_asDict.items() if value is not None and value < curr_max)
                    key = next(key for key, value in row_asDict.items() if value == mostRecentTime)
                except ValueError:
                    key = 'no_status'
                single_home_status[curr] = key
                curr += 1
            home_status_list.append(pd.Series(data = single_home_status.ravel(), name = i))
        result = pd.concat(home_status_list, axis = 1)
        return result

    # Initialisation: Generate a DataFrame that counts the number of each status
    # at every point in time. This is used for the line graph.
    # returns a single DataFrame
    def _generateStatusCounts(self):
        status_count_list = []
        for time in range(1, self._simTime):
            status_count_list.append(pd.Series(data = self._allHomeStates[time].value_counts(), name = str(time)))
        status_count_df = pd.concat(status_count_list, axis = 1).fillna(value = 0)
        missing = [status for status in self._desiredStates if status not in status_count_df.index]
        return status_count_df.reindex(status_count_df.index.union(missing)).fillna(value = 0).reindex(self._desiredStates_ns)


    # Initialisation: Generate a DataFrame that mirrors allHomeStates but with
    # categorical colors to display on a map.
    # returns a single DataFrame
    def _generateHomeStatusColors(self):
        return self._allHomeStates.replace(self._assignedColors)

    # Initialisation: Generate sources for the plots.
    # returns a single DataFrame
    def _run(self):
        self._allHomeStates = self._generateHomeStatus()
        self._stateCounts = self._generateStatusCounts()
        self._allHomeStateColors = self._generateHomeStatusColors()

    # Client-facing: Get a list of the ZIP codes in the data.
    # prints: list
    def getUniqueZipcodes(self):
        print("ZIP codes in this dataset:")
        print(self._uniqueZipcodes)

    # Client-facing: Filter or re-filter the data by a different ZIPcode
    # refilters and prints confirmation
    def filterByZip(self, desiredZipcode):
        self._filteredData = self._filterByZip(desiredZipcode).reset_index(drop=True)
        self._filteredNumHomes = len(self._filteredData)
        self._desiredZipcode = desiredZipcode
        self._onlyStateData = self._filteredData[self._desiredStates].reset_index(drop=True)
        self._run()
        if desiredZipcode is None:
            print("Data is not filtered. All data will be shown.")
        else:
            print("Data now filtered by Zipcode:", desiredZipcode)

    # Client-facing: export the current vis data (statuses of each entity by day) to CSV
    def exportVisData(self, fileName="statusByDay.csv"):
        data = self._generateHomeStatus()
        data.to_csv(fileName)
        print("Exported the Status By Day file to " + fileName + ".")

    # Client-facing: Generate the vis!
    def visualize(self):

        # Set up the output file
        output_file(self._outputFileName)

        ## BARPLOT ##

        per_day = self._stateCounts.transpose().values.tolist()
        data = dict({str(i): v for i, v in enumerate(per_day)})
        data['x'] = self._desiredStates_ns #add the statuses to the data source
        data['y'] = [0.0 for i in range(len(self._desiredStates_ns))] #dummy column for CustomJS to overwrite
        data['colorsOnly'] = self._colorsOnly

        source = ColumnDataSource(data)

        #plot setup
        barplot = figure(plot_width=800, plot_height=600, tools='pan',
                         x_axis_label='Status', x_range=source.data['x'],
                         y_range=ranges.Range1d(start=0, end=int(self._filteredNumHomes*1.1)), title="Number of Homes by Status at Current Day")

        barplot.vbar(source=source, x='x', top='y', width=0.6, fill_color='colorsOnly', line_color=None)
        bar_hover = HoverTool(tooltips=[('num','@y')])
        barplot.yaxis.axis_label = "Number of Homes"
        barplot.add_tools(bar_hover)

        ## MAPS ##


        mapHoverInfo = self._mapHoverOptions
        options_html = ""
        for option in mapHoverInfo:
            options_html += "<span style=\"font-weight: bold;\">%s: </span><span>%s<br></span>"%(str(option), "@" + str(option))

        mapHoverInfo_html = "<div style=\"width: 450px\">" + options_html + "</div>"

        map_hover = HoverTool(tooltips=mapHoverInfo_html)

        #get average lat, long
        mean_lat = self._filteredData['latitude'].mean()
        mean_long = self._filteredData['longitude'].mean()

        #get the zip area name
        if self._desiredZipcode is None:
            areaData = self._zipSearch.by_coordinate(mean_lat, mean_long, returns=1)[0]
            areaName = "Greater " + areaData['City'] + " Area"
        else:
            areaData = self._zipSearch.by_zipcode(self._desiredZipcode)
            areaName = areaData['City'] + ", " + str(areaData['Zipcode'])

        map_options = GMapOptions(lat = mean_lat, lng = mean_long, map_type = "roadmap")
        mapplot = GMapPlot(x_range=ranges.Range1d(), y_range=ranges.Range1d(), map_options=map_options)
        mapplot.title.text = areaName
        mapplot.add_tools(PanTool(), WheelZoomTool(), map_hover)

        #set Google Maps API key
        mapplot.api_key = "AIzaSyAr5Z6tbpyDQLPyD4PQmrxvqn6VEN_3vnU"

        #data wrangling for JS interaction
        home_data_for_map_list = [self._allHomeStateColors.copy(), self._filteredData['latitude'], self._filteredData['longitude']]
        for option in self._mapHoverOptions:
            home_data_for_map_list += [self._filteredData[str(option)]]

        home_status_colors_formap = pd.concat(home_data_for_map_list, axis=1)
        initialDamageStateData = self._filteredData['damage_state_start'].replace(self._damageStates)
        home_status_colors_formap = pd.concat([home_status_colors_formap, initialDamageStateData], axis = 1)
        home_status_colors_formap['y'] = np.nan #dummy column
        home_status_colors_formap.columns = home_status_colors_formap.columns.astype(str)

        mapsource = ColumnDataSource(home_status_colors_formap)
        circle = Circle(x ="longitude", y = "latitude", size = 'damage_state_start', fill_color = "y", fill_alpha = 0.8, line_color = None)
        mapplot.add_glyph(mapsource, circle)


        ## LINE GRAPH ##

        # LINE GRAPH - CURRENT TIME INDICATOR #
        # Generate a vertical bar to indicate current time within the line graph
        # Line is generated to 10% above the number of homes and 10% below zero
        currtime_list = {'x':[0, 0], 'y':[int(self._filteredNumHomes*1.1), int(self._filteredNumHomes*-0.1)]} #dummy column for js callback
        for i in range(0, self._simTime):
            currtime_list[str(i)] = [i, i]

        currtime_source = ColumnDataSource(currtime_list)

        # LINE GRAPH - DATA #

        line_plot = figure(title='Overall House Status vs Time', y_range=ranges.Range1d(start=int(self._filteredNumHomes*0.1), end=int(self._filteredNumHomes*1.5)))
        all_line_data = self._stateCounts.values.tolist()

        day_range = np.linspace(1,self._simTime-2, num=self._simTime-1).tolist()

        for data, name, color in zip(all_line_data, self._statuses, self._colorsOnly):
            line_data = pd.DataFrame(data).values.tolist()
            line_plot.line(day_range, line_data, color=color, alpha=0.8, legend=name, line_width=2)

        line_plot.line(x='x', y='y', source=currtime_source, line_color='red')

        line_plot.legend.location = "top_center"
        line_plot.legend.click_policy = "hide"
        line_plot.legend.orientation = "horizontal"
        line_plot.yaxis.axis_label = "Number of Homes"
        line_plot.xaxis.axis_label = "Day"

        # Requires Bokeh 0.12.7
        # Javascript callback to enable and link interactivity between the two plots.
        callback = CustomJS(args=dict(s1=source, s2=mapsource, s3=currtime_source), code="""
            console.log(' changed selected time', cb_obj.value);
            var data = s1.data;
            var data2 = s2.data;
            var data3 = s3.data;
            data['y'] = data[cb_obj.value];
            data2['y'] = data2[cb_obj.value];
            data3['x'] = data3[cb_obj.value];
            s1.change.emit();
            s2.change.emit();
            s3.change.emit();
        """)

        ## SLIDER ##
        # This slider manages one callback which updates all three graphics.
        time_slider = Slider(start=1, end=self._simTime-1, value=0, step=1, callback=callback, title='DAY')

        show(gridplot([[mapplot],
            [line_plot, barplot],[time_slider]], sizing_mode = 'stretch_both'))
