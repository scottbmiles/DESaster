# -*- coding: utf-8 -*-
"""
Created on Wed Jan 20 09:54:53 2016

@author: Derek, Scott
Entities classes

"""
from simpy import Interrupt
from desaster.capitals import Residence

class Household(object):
    """Define a Household class with attributes and visualization methods.

        Methods have yet to be defined, but will likely include putting data into
        a pandas dataframe and having the ability to show recovery trajectories
        for each household
    """
    def __init__(self, simulation, household):

        # Household Attributes
        self.household = household
        self.name = household['Name']  # Name assigned to household
        self.income = household['Income'] # --+ added +--
        self.savings = household['Savings'] # --% Modified to read input data %--
        self.insurance = household['Insurance'] # --% Modified to read input data %--
        
        
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
        self.money_to_rebuild = self.savings # Total funds available to household to rebuild house
        self.house_put = 0.0 # Time put request in for house rebuild
        self.house_get = 0.0 # Time get house rebuild completed
        self.loan_put = 0.0 # Time put request for loan
        self.loan_get = 0.0 # Time get requested loan
        self.loan_amount = 0.0 # Amount of loan
        self.permit_put = 0.0 # Time put request for building permit
        self.permit_get = 0.0 # Time get requested building permit
        
        # Function calls
        self.residence = Residence(simulation, household) # Assign residence to the household
        self.setStory() # Start stories with non-disaster attributes
    
    def setStory(self):
        
        # Start stories with non-disaster attributes
        self.story.append(
        '{0} lives in a {1} bedroom {2} Home ({3}). '.format(self.name, 
                                                        self.residence.bedrooms, 
                                                        self.residence.occupancy,
                                                        self.residence.address
                                                        )
        )

    def story_to_text(self): # --% modified %--
        '''
            Function to join the strings within the story list created during DESaster processes
        '''
        
        return ''.join(self.story)