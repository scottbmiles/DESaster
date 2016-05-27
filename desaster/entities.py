# -*- coding: utf-8 -*-
"""
Created on Wed Jan 20 09:54:53 2016

@author: Derek, Scott
Entities classes

"""

import pandas as pd
import numpy as np

class Household:
    """Define a Household class with attributes and visualization methods.

        Methods have yet to be defined, but will likely include putting data into
        a pandas dataframe and having the ability to show recovery trajectories
        for each household
    """
    def __init__(self, household):
        # Time paramaters
        # self.response_time = 14 # Initial wait time before inspection is requested
        # self.inspection_time = .5# Time it takes to inspect a house
        # self.claim_time = 90 # Time it takes to process insurance claim
        # self.assistance_time = 120 # Time required for FEMA to process assistance request
        # self.rebuild_time = 60 # Time required to rebuild house #### moved to config.py
        self.savings = np.random.normal(5000, 2500) # Pre-event household savings
        # self.insurance_coverage = np.random.normal(0.0, 0.0)
        self.insurance_coverage = 0.0

        # Inputs
        self.household = household
        self.name = household['Name']  # Name assigned to household
        self.damaged = household['Damaged'] # House damaged [True|False]
        self.damage_value = household['TotalRep'] # Amount needed to rebuild home/repair damage

        #Outputs
        self.story = [] # The story of events for each household
        self.inspection_put = 0.0 # Time put request in for house inspection
        self.inspection_get = 0.0 # Time get  house inspection
        self.claim_put = 0.0 # Time put request in for insurance settlement
        self.claim_get = 0.0 # Time get insurance claim settled
        self.claim_payout = 0.0 # Amount of insurance claim payout
        self.assistance_put = 0.0 # Time put request in for FEMA assistance
        self.assistance_get = 0.0 # Time get FEMA assistance
        self.assistance_request = 0.0 # Amount of money requested from FEMA
        self.assistance_payout = 0.0 # Amount of assistance provided by FEMA
        self.money_to_rebuild = 0 # Total funds available to household to rebuild house
        self.house_put = 0.0 # Time put request in for house rebuild
        self.house_get = 0.0 # Time get house rebuild completed
        self.loan_put = 0.0 # Time put request for loan
        self.loan_get = 0.0 # Time get requested loan
        self.permit_put = 0.0 # Time put request for building permit
        self.permit_get = 0.0 # Time get requested building permit



    def story_to_text(self):
        """Print out self.story to an output file in paragraph form."""
        pass

def imp_concat():
    input1 = pd.read_csv("../inputs/Work out of County Households.csv")
    input2 = pd.read_csv("../inputs/Work in County Households.csv")
    input3 = pd.read_csv("../inputs/Middle High School Households.csv")
    input4 = pd.read_csv("../inputs/Elementary School Households.csv")
    input5 = pd.read_csv("../inputs/Grocery Households.csv")
    all_inputs = [input1, input2, input3, input4, input5]
    data = pd.concat(all_total)
    return data

def get_names():
    lasts = pd.read_csv("../inputs/last_names.csv")
    data = lasts.iloc[0:1366]
    return data['name']
#data = imp_concat().drop_duplicates(subset="Address").reset_index()
#data = data.reset_index()
#lasts = get_names()
#data['names'] = lasts
#data.to_csv("output.csv")
#names = pd.Series()
