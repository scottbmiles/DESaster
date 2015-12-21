# -*- coding: utf-8 -*-
"""
Created on Sun Dec 20 10:21:08 2015

@author: geomando
"""
# General dependencies
import pandas as pd

# Housing simulation specific dependencies
from housing_sim import simulate_housing


### Set up household inputs dictionary ###
households_dict = {'name' : ['Bill', 'Boyd', 'Bobby', 'Biff'],
                     'savings' : [100.0, 1000.0, 10000.0, 100000.0],
                    'damaged' : [1, 1, 1, 1],
                    'damage_value' : [10000.0, 10000.0, 20000.0, 20000.0],
                    'insurance_coverage' : [0.0, 0.0, 5000.0, 10000.0]
                    }

# Create households dataframe from dictionary.
households_df = pd.DataFrame(households_dict)
# Re-order dataframe columns
households_df = households_df[['name','savings','insurance_coverage','damaged','damage_value']]


### Set up resources inputs dictionaries ###

# Constants for durable resources
NUM_INSPECTORS = 1  #Number of Inspectors
NUM_FEMA_PROCESSORS = 4 #Number of FEMA assistance application processors
NUM_INSURANCE_ADJUSTERS = 4 #Number of insurance claim adjusters
NUM_CONTRACTORS = 4 #Number of Contractors

# Create dictionary of durables contants
durables_dict = {"inspectors": NUM_INSPECTORS,
             "fema processors": NUM_FEMA_PROCESSORS,
             "claim adjusters": NUM_INSURANCE_ADJUSTERS,
             "contractors": NUM_CONTRACTORS,
             }

# Constants for nondurable resources
FEMA_ASSISTANCE_BUDGET = 100000 # Budget allocated to FEMA to fund individual assistance

# Create dictionary of nondurables contants
nondurables_dict = {"fema assistance": FEMA_ASSISTANCE_BUDGET}


# Call simulate_housing function by passing households and resources inputs
# to produce housing recovery outputs dataframe.
# Join input table and output dataframes inline for easier analysis
households_df = households_df.join(
                            simulate_housing(households_df, durables_dict, nondurables_dict)
                            )
