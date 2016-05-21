# -*- coding: utf-8 -*-
"""
Created on Fri Apr 15 13:04:41 2016

@author: Derek
"""

import pandas as pd

routes_path = "C:/Users/Derek/Dropbox/Simulation/SeaGrantSimulation/desaster/output.csv"

value_data_path = "C:/Users/Derek/Dropbox/Simulation/SeaGrantSimulation/inputs/situ_parcelnum.csv"


routes = pd.read_csv(routes_path)
values = pd.read_csv(value_data_path)

#new_frame = routes.join(values, on='Address', how = )
newframe = pd.merge(routes, values, how='outer', on='Address')