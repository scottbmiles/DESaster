# -*- coding: utf-8 -*-
"""
Module of classes for implementing DESaster entities, such as households and 
businesses.

Classes: 
Household(object)

@author: Derek Huling, Scott Miles
"""
# Import Residence() class in order to assign households a residence.
from desaster.capitals import Residence 

class Household(object):
    """Define a Household() class to represent a group of persons that reside 
    together as a single analysis unit with attributes and methods.
    """
    def __init__(self, simulation, household_df, write_story = False):
        """Define household inputs and outputs attributes.
        Initiate household's story list string. 
        
        simulation -- Pointer to SimPy simulation environment.
        household_df -- Dataframe row w/ household input attributes.
        write_story -- Boolean indicating whether to track a households story.
        """
         # Household simulation inputs
        self.household = household_df  # Dataframe w/ household input attributes
        self.name = household_df['Name']   # Name associated with household
        self.savings = household_df['Savings']  # Amount of household savings in $
        self.insurance = household_df['Insurance']  # Hazard-specific insurance coverage in $
        self.residence = Residence(simulation, household_df)  # Pointer to household's Residence() object
        
        # Household simulation outputs
        self.story = []  # The story of events for each household
        self.inspection_put = None  # Time put request in for house inspection
        self.inspection_get = None  # Time get  house inspection
        self.claim_put = None  # Time put request in for insurance settlement
        self.claim_get = None  # Time get insurance claim settled
        self.claim_payout = 0  # Amount of insurance claim payout
        self.assistance_put = None  # Time put request in for FEMA assistance
        self.assistance_get = None  # Time get FEMA assistance
        self.assistance_request = 0  # Amount of money requested from FEMA
        self.assistance_payout = 0  # Amount of assistance provided by FEMA
        self.money_to_rebuild = self.savings  # Total funds available to household to rebuild house
        self.home_put = None  # Time put request in for house rebuild
        self.home_get = None  # Time get house rebuild completed
        self.loan_put = None  # Time put request for loan
        self.loan_get = None  # Time get requested loan
        self.loan_amount = 0  # Amount of loan received
        self.permit_put = None  # Time put request for building permit
        self.permit_get = None  # Time get requested building permit
        self.home_search_start = None  # Time started searching for a new home
        self.home_search_stop = None  # Time found a new home
        self.money_search_start = None  # Time that household started search for money
        self.money_search_stop = None  # Time that household found rebuild money
        self.gave_up_money_search = False  # Whether household gave up search for money
        self.gave_up_home_search = False  # Whether household gave up search for home 
        self.old_house = None #Location of old house, in a tuple
        # Initial method calls
        self.setStory(write_story)  # Start stories with non-disaster attributes
    
    def setStory(self, write_story):
        """Initiate the household's story based on input attributes.
        
        Keyword Arguments:
        write_story -- Boolean indicating whether to track a households story.
        """
        if write_story == True:
            # Set story with non-disaster attributes.
            self.story.append(
            "{0} lives in a {1} bedroom {2} at {3} worth ${4:,.0f}. Its damage level from the event was {5}.".format(self.name.title(), 
                                                            self.residence.bedrooms, 
                                                            self.residence.occupancy,
                                                            self.residence.address,
                                                            self.residence.value,
                                                            self.residence.damage_state
                                                            )
            )

    def story_to_text(self): 
        """Join list of story strings into a single story string."""
        return ''.join(self.story)

def importHouseholds(simulation, households_df, write_story = False):
    """Return list of entities.Household() objects from dataframe containing
    data describing households.
    
    Keyword Arguments:
    simulation -- Pointer to SimPy simulation environment.
    household_df -- Dataframe row w/ household input attributes.
    write_story -- Boolean indicating whether to track a households story.
    """
    
    households = []

    # Population the simulation with households from the households dataframe
    for i in households_df.index:
        households.append(Household(simulation, households_df.iloc[i], write_story))
    
    return households