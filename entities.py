# -*- coding: utf-8 -*-
"""
Created on Wed Jan 20 09:54:53 2016

@author: Derek
Entities classes

"""

import pandas as pd

class Household:
    """Define a Household class with attributes and visualization methods.
    
        Methods have yet to be defined, but will likely include putting data into
        a pandas dataframe and having the ability to show recovery trajectories
        for each household
    """
    def __init__(self, household):
        # Time paramaters
        self.response_time = 14 # Initial wait time before inspection is requested
        self.inspection_time = 1 # Time it takes to inspect a house
        self.claim_time = 90 # Time it takes to process insurance claim
        self.assistance_time = 120 # Time required for FEMA to process assistance request
        self.rebuild_time = 60 # Time required to rebuild house

        # Inputs
        self.name = household['name']  # Name assigned to household
        self.damaged = household['damaged'] # House damaged [True|False]
        self.damage_value = household['damage_value'] # Amount needed to rebuild home/repair damage
        self.savings = household['savings'] # Pre-event household savings
        self.insurance_coverage = household['insurance_coverage'] # Amount of earthquake insurance coverage

        #Outputs
        self.story = [] # The story of events for each household
        self.inspection_put = 0 # Time that house inspection occurred
        self.inspection_get = 0 # Time that house inspection occurred
        self.claim_put = 0 # Start time for insurance claim processing
        self.claim_get = 0 # Stop time for insurance claim processing
        self.claim_payout = 0 # Amount of insurance claim payout
        self.assistance_put = 0 # Time FEMA assistance request is put in
        self.assistance_get = 0 # Time FEMA assistance is received
        self.assistance_request = 0 # Amount of money requested from FEMA
        self.assistance_payout = 0 # Amount of assistance provided by FEMA
        self.house_put = 0 # Start time for house rebuild
        self.house_get = 0 # Stop time for house rebuild
        self.money_to_rebuild = 0 # Total funds available to household to rebuild house
        
        
    def story_to_text(self):
        """Print out self.story to an output file in paragraph form."""
        pass
