from bokeh.plotting import figure
from bokeh.layouts import column, widgetbox, row, gridplot, layout
from bokeh.models import CustomJS, Slider, ColumnDataSource, ranges
from bokeh.io import output_file, show
import bokeh.palettes
from bokeh.models import (GMapPlot, GMapOptions, Circle, DataRange1d,
                            PanTool, WheelZoomTool, HoverTool, SaveTool, ResetTool)
import numpy as np
import pandas as pd

import webbrowser as wb
chrome_path = 'open -a /Applications/Google\ Chrome.app %s'

import folium
from folium import plugins
import branca.colormap as cm
from folium.plugins import MarkerCluster
from folium import Map, FeatureGroup, Marker, LayerControl

def dashboard(df, sim_time = 180, lat = 43.223628, lon = -90.294633,
            outfile = 'dashboard.html'):



    #Isolate the individual housing states
    df_onlyState = df[['inspection_get', 'claim_get', 'fema_get', 'sba_get',
                        'permit_get', 'repair_get', 'home_get', 'occupy_get']]

    #list of statuses in correct order for future reference
    statuses = ['inspection_get', 'claim_get', 'fema_get', 'sba_get',
                        'permit_get', 'repair_get', 'home_get', 'occupy_get']


    NUM_HOMES = df.shape[0] #the total number of entities
    NUM_CAT = len(statuses) #the total number of categories

    # assign colors to the sequential housing statuses.
    # colors are map-optimised, from ColorBrewer
    # palettes will scale to size automatically, max size is 20
    colors_only = bokeh.palettes.d3['Category20'][NUM_CAT]


    colors = {}

    for i in range(0,len(statuses)):
        colors[statuses[i]] = colors_only[i]


    # create a list to hold the status of all homes by day
    home_status_list = []

    for i in range(0, sim_time):

        single_home_status = np.empty(shape = [2860,1], dtype = object)
        curr_max = i
        curr = 0
        for row in df_onlyState.itertuples(index = False):
            #convert the row into a dictionary for key-value analysis
            row_asDict = row._asdict()

            #find the most recent status time of the home within currMax. ignores None and nan
            try:
                mostRecentTime = max(value for name, value in row_asDict.items() if value is not None and value < curr_max)
                #reverse key-value to determine actual status
                key = next(key for key, value in row_asDict.items() if value == mostRecentTime)
            except ValueError:
                key = 'no_status'

            single_home_status[curr] = key
            curr += 1

        home_status_list.append(pd.Series(data = single_home_status.ravel(), name = i))

    # create a single DataFrame for the home statuses at every unit of simulation time
    home_status = pd.concat(home_status_list, axis = 1)

    # dataframe for number of homes with a given status at every point of simulation time

    status_count_list = []
    for time in range(0, sim_time):
        status_count_list.append(pd.Series(data = home_status[time].value_counts(), name = str(time)))

    #concatenate and fill NaN with zeroes. re-index rows to correct order
    status_count_df = pd.concat(status_count_list, axis = 1).fillna(value = 0).reindex(statuses)

    #create a new dataframe with just the colors for the map
    #current colors: white to dark green, where dark green = home_get
    home_status_colors = home_status.replace(colors)

    # Interactive Barplot
    # Standalone HTML file using CustomJS

    #wrangle the data into a data source for the ColumnDataSource to work properly with Javascript
    per_day = status_count_df.transpose().values.tolist()
    data = dict({str(i): v for i, v in enumerate(per_day)})
    data['x'] = statuses #add the statuses to the data source
    data['y'] = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0] #dummy column for CustomJS to overwrite
    data['colors'] = colors_only

    source = ColumnDataSource(data)

    output_file(outfile)

    #plot setup
    barplot = figure(plot_width=800, plot_height=600, tools='pan, wheel_zoom, reset, save',
                  x_axis_label='Status', x_range=source.data['x'],
                  y_range=ranges.Range1d(start=0, end=len(data['y'])),
                  title="Number of Households by Status at Specified Time (Slider)")
    barplot.vbar(source=source, x='x', top='y', color='colors', width=0.6)
    bar_hover = HoverTool(tooltips=[('num','@y')])
    barplot.add_tools(bar_hover)

    lat = 43.223628
    lon = -90.294633
    #Map Setup
    map_options = GMapOptions(lat = lat, lng = lon, scale_control = True, map_type = "roadmap", zoom = 16)
    mapplot = GMapPlot(x_range=DataRange1d(), y_range=DataRange1d(), map_options=map_options)
    mapplot.title.text = "Locations of Modeled Homes (Marker Size Proportional to Original Damage State; Colors Defined Below)"

    # Set up tool tip with household stories
    hover = HoverTool()
    hover.tooltips = [("Household's Story:", "@story")]

    mapplot.add_tools(PanTool(), WheelZoomTool(), ResetTool(), hover, SaveTool())
    mapplot.min_border_top = 50
    mapplot.min_border_bottom = 0

    #set Google Maps API key
    mapplot.api_key = "AIzaSyBIwu-YI4jgBfzconosHqtQoeZ40oH-bhU"

    #data wrangling for JS interaction
    home_status_formap = pd.concat([home_status_colors.copy(), df['latitude'], df['longitude']], axis=1)
    home_status_formap['y'] = np.nan #dummy column
    home_status_formap['story'] = df['story']
    home_status_formap.columns = home_status_formap.columns.astype(str)

    # Reclassify damage states at start of simulation for each household to set
    # marker/circle size for mapping
    damage_size = dict({'None': 10,
                        'Slight': 15,
                        'Moderate': 20,
                        'Extensive': 25,
                        'Complete': 30})

    home_status_formap['circle_size'] = df['damage_state_start'].replace(
                                            list(damage_size.keys()),
                                            list(damage_size.values()))

    mapsource = ColumnDataSource(home_status_formap)

    circle = Circle(x ="longitude", y = "latitude", size = 'circle_size', fill_color = "y",
                    fill_alpha = 0.8, line_color = 'black')
    mapplot.add_glyph(mapsource, circle)

    # Javascript callback to enable and link interactivity between the two plots.
    callback = CustomJS(args=dict(s1=source, s2=mapsource), code="""
        console.log(' changed selected time', cb_obj.value);
        var data = s1.data;
        var data2 = s2.data;
        data['y'] = data[cb_obj.value];
        data2['y'] = data2[cb_obj.value];
        s1.change.emit()
        s2.change.emit()
    """)

    #Line Graph setup
    line_plot = figure(title='Number of Households By Status vs. Simulated Time',
                       y_range=ranges.Range1d(start=int(NUM_HOMES*0.1), end=int(NUM_HOMES*1.5)),
                       tools='pan, wheel_zoom, reset, save')
    all_line_data = status_count_df.values.tolist()

    day_range = np.linspace(0, sim_time, num=sim_time).tolist()

    # Generate a vertical bar to indicate current time within the line graph
    # Line is generated to 10% above the number of homes and 10% below zero
    currtime_list = {'x':[0, 0], 'y':[int(NUM_HOMES*1.1), int(NUM_HOMES*-0.1)]} #dummy column for js callback
    for i in range(0, sim_time):
        currtime_list[str(i)] = [i, i]

    currtime_source = ColumnDataSource(currtime_list)

    # Create set of line plots with ability to turn individual lines on/off
    for data, name, color in zip(all_line_data, statuses, colors_only):
        line_data = pd.DataFrame(data).values.tolist()
        line_plot.line(day_range, line_data, color=color, alpha=0.8, legend=name, line_width=2)

    line_plot.line(x='x', y='y', source=currtime_source, line_color='red')

    line_plot.legend.location = "top_left"
    line_plot.legend.click_policy = "hide"

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

    #slider
    time_slider = Slider(start=0, end=sim_time, value=0, step=1, callback=callback, title='DAY')

    #show entire layout
    show(layout([[mapplot],
        [line_plot, barplot],time_slider], sizing_mode = 'stretch_both'))

def folium_map(df, lat = 43.223628, lon = -90.294633, outfile = 'folium_map.html'):

    map = folium.Map(location=(lat, lon), tiles='Stamen Terrain', zoom_start=18)


    folium.TileLayer('Stamen Terrain').add_to(map)
    folium.TileLayer('OpenStreetMap').add_to(map)
    # folium.TileLayer('Cartodb Positron').add_to(map)

    repair_group = FeatureGroup(name='Mean Home Repair Time')

    # map.choropleth(geo_str=blocks_pts_mean_joined.to_json(), data=blocks_pts_mean_joined,
    #              columns=['BLOCK_ID', 'home_get'],
    #              fill_color='PuBu', fill_opacity=0.5,
    #              key_on='properties.BLOCK_ID',
    #              legend_name='Mean Home Repair Time')


    complete_group = FeatureGroup(name='Complete Damage')
    extensive_group = FeatureGroup(name='Extensive Damage')
    moderate_group = FeatureGroup(name='Moderate Damage')
    slight_group = FeatureGroup(name='Slight Damage')
    none_group = FeatureGroup(name='No Damage')

    count = 0

    for i in df.iterrows():
        count += 1

        if i[1].damage_state_start == 'Complete':
            try:
                folium.Marker(location = [i[1].latitude, i[1].longitude],
                              popup=i[1].story, icon=folium.Icon("darkred", icon='home')).add_to(complete_group)
            except AttributeError:
                folium.Marker(location = [i[1].latitude, i[1].longitude],
                              icon=folium.Icon("darkred", icon='home')).add_to(complete_group)
        elif i[1].damage_state_start == 'Extensive':
            try:
                folium.Marker(location = [i[1].latitude, i[1].longitude],
                              popup=i[1].story, icon=folium.Icon("red", icon='home')).add_to(extensive_group)
            except AttributeError:
                folium.Marker(location = [i[1].latitude, i[1].longitude],
                              icon=folium.Icon("red", icon='home')).add_to(extensive_group)
        elif i[1].damage_state_start == 'Moderate':
            try:
                folium.Marker(location = [i[1].latitude, i[1].longitude],
                              popup=i[1].story, icon=folium.Icon("orange", icon='home')).add_to(moderate_group)
            except AttributeError:
                folium.Marker(location = [i[1].latitude, i[1].longitude],
                              icon=folium.Icon("orange", icon='home')).add_to(moderate_group)
        elif i[1].damage_state_start == 'Slight':
            try:
                folium.Marker(location = [i[1].latitude, i[1].longitude],
                              popup=i[1].story, icon=folium.Icon("lightgreen", icon='home')).add_to(slight_group)
            except AttributeError:
                folium.Marker(location = [i[1].latitude, i[1].longitude],
                              icon=folium.Icon("lightgreen", icon='home')).add_to(slight_group)
        else:
            try:
                folium.Marker(location = [i[1].latitude, i[1].longitude],
                              popup=i[1].story, icon=folium.Icon("green", icon='home')).add_to(none_group)
            except AttributeError:
                folium.Marker(location = [i[1].latitude, i[1].longitude],
                              icon=folium.Icon("green", icon='home')).add_to(none_group)

    #     if count > 50:
    #         break
    #     else:
    #         continue

    map.add_child(complete_group)
    map.add_child(extensive_group)
    map.add_child(moderate_group)
    map.add_child(slight_group)
    map.add_child(none_group)
    map.add_child(folium.map.LayerControl())
    map.add_child(plugins.Fullscreen())

    map_name = outfile
    map.save(outfile)
    wb.get(chrome_path).open(outfile, new=2, autoraise = True)
