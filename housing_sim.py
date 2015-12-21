# -*- coding: utf-8 -*-
"""
Created on Sun Dec 20 09:54:40 2015

@author: geomando, dhuling

Dependencies: pandas 17+, SimPy 3+, numpy
"""
# General dependencies
import simpy
import numpy
import pandas as pd

# housing_sim dependencies
import housing_entities
from housing_resources import DurableResource, NondurableResource
from housing_entities import Household

# Inputs for households must be a dataframe. Inputs for resources must be dictionaries
def simulate_housing(households_df, durables_dict, nondurables_dict):
    # create simulation environment
    simulation = simpy.Environment()

    # paramaterize resources and place in simulation environmentl
    durables = DurableResource(simulation, durables_dict)
    nondurables = NondurableResource(simulation, nondurables_dict)
    resources = {'durable': durables,
                     'nondurable': nondurables}

    # Instantiage household objects
    households = {}
    for i in households_df.index:
        households[i] = Household(households_df.loc[i])

    # paramaterize households objects and place in simulation environmentl
    for household in households.iterkeys():
        simulation.process(households[household].simulate(simulation, resources))

    # Run the simulation
    simulation.run()

    households_outputs = pd.DataFrame(data=None, index=households.keys(), columns=
                                     ['response_time','inspection_get','inspection_time','assistance_put','assistance_get'
                                      ,'assistance_time','assistance_request','assistance_payout','claim_put','claim_get',
                                      'claim_time','claim_payout','house_put','house_get','rebuild_time','story'])

    for i, house in households.iteritems():
        households_outputs.loc[i]['response_time'] = house.response_time
        households_outputs.loc[i]['inspection_put'] = house.inspection_put
        households_outputs.loc[i]['inspection_get'] = house.inspection_get
        households_outputs.loc[i]['inspection_time'] = house.inspection_time
        households_outputs.loc[i]['claim_put'] = house.claim_put
        households_outputs.loc[i]['claim_get'] = house.claim_get
        households_outputs.loc[i]['claim_time'] = house.claim_time
        households_outputs.loc[i]['claim_payout'] = house.claim_payout
        households_outputs.loc[i]['assistance_put'] = house.assistance_put
        households_outputs.loc[i]['assistance_get'] = house.assistance_get
        households_outputs.loc[i]['assistance_time'] = house.assistance_time
        households_outputs.loc[i]['assistance_request'] = house.assistance_request
        households_outputs.loc[i]['assistance_payout'] = house.assistance_payout
        households_outputs.loc[i]['house_put'] = house.house_put
        households_outputs.loc[i]['house_get'] = house.house_get
        households_outputs.loc[i]['rebuild_time'] = house.rebuild_time
        households_outputs.loc[i]['story'] = ''.join(house.story)

    return households_outputs
