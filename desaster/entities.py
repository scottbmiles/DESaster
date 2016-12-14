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
import names

#class Household(object):
#    """Define a Household() class to represent a group of persons that reside 
#    together as a single analysis unit with attributes and methods.
#    """
#    def __init__(self, simulation, housing_stock, household_df, write_story = False):
#        """Define household inputs and outputs attributes.
#        Initiate household's story list string. 
#        
#        simulation -- Pointer to SimPy simulation environment.
#        household_df -- Dataframe row w/ household input attributes.
#        housing_stock -- a SimPy FilterStore that acts as an occupied housing stock
#        write_story -- Boolean indicating whether to track a households story.
#        """
#        
#        # Household simulation inputs
#        self.household = household_df  # Dataframe w/ household input attributes
#        self.name = household_df['Name']   # Name associated with household
#        self.savings = household_df['Savings']  # Amount of household savings in $
#        self.insurance = household_df['Insurance']  # Hazard-specific insurance coverage in $
#        self.tenure_pref = household_df['Tenure Pref'] # Indicator of the household's preference between rent or own %***%
#        self.tenure = household_df['Tenure'] # Indicator of the household's *actual* tenure between rent or own %***%
#        self.occupancy_pref = household_df['Occupancy Pref'] # Indicator of the household's preference between occupancy types %***%
#        
#        self.owner = [] # %***%
#         
#        # Household simulation outputs
#        self.story = []  # The story of events for each household
#        self.inspection_put = 0.0  # Time put request in for house inspection
#        self.inspection_get = 0.0  # Time get  house inspection
#        self.claim_put = 0.0  # Time put request in for insurance settlement
#        self.claim_get = 0.0  # Time get insurance claim settled
#        self.claim_payout = 0.0  # Amount of insurance claim payout
#        self.assistance_put = 0.0  # Time put request in for FEMA assistance
#        self.assistance_get = 0.0  # Time get FEMA assistance
#        self.assistance_request = 0.0  # Amount of money requested from FEMA
#        self.assistance_payout = 0.0  # Amount of assistance provided by FEMA
#        self.money_to_rebuild = self.savings  # Total funds available to household to rebuild house
#        self.home_put = 0.0  # Time put request in for house rebuild
#        self.home_get = 0.0  # Time get house rebuild completed
#        self.loan_put = 0.0  # Time put request for loan
#        self.loan_get = 0.0  # Time get requested loan
#        self.loan_amount = 0.0  # Amount of loan received
#        self.permit_put = 0.0  # Time put request for building permit
#        self.permit_get = 0.0  # Time get requested building permit
#        self.home_search_start = 0.0  # Time started searching for a new home
#        self.home_search_stop = 0.0  # Time found a new home
#        self.money_search_start = 0.0  # Time that household started search for money
#        self.money_search_stop = 0.0  # Time that household found rebuild money
#        self.gave_up_money_search = False  # Whether household gave up search for money
#        self.gave_up_home_search = False  # Whether household gave up search for home 
#        
#        # Initial method calls
#        
#        self.setResidence(simulation, housing_stock, household_df)
#        self.setStory(write_story)  # Start stories with non-disaster attributes
#    
#    def setResidence(self, simulation, housing_stock, household_df):
#        """Initiate the household's residence based on input attributes
#        then add their residence to the housing stock FilterStore.
#        
#        Keyword Arguments:
#        simulation -- Pointer to SimPy simulation environment.
#        household_df -- Dataframe row w/ household input attributes.
#        housing_stock -- a SimPy FilterStore that acts as an occupied housing stock
#        """
#        self.residence = Residence(simulation, household_df) 
#        housing_stock.put(self.residence)
#        
#    def setStory(self, write_story):
#        """Initiate the household's story based on input attributes.
#        
#        Keyword Arguments:
#        write_story -- Boolean indicating whether to track a households story.
#        """
#        if write_story == True:
#            # Set story with non-disaster attributes.
#            self.story.append(
#            '{0} lives in a {1} bedroom {2} at {3} worth ${4:,.0f}. '.format(self.name, 
#                                                            self.residence.bedrooms, 
#                                                            self.residence.occupancy,
#                                                            self.residence.address,
#                                                            self.residence.value
#                                                            )
#            )
#
#    def story_to_text(self): 
#        """Join list of story strings into a single story string."""
#        return ''.join(self.story)

class Household(object):
    """Define a Household() class to represent a group of persons that reside 
    together as a single analysis unit with attributes and methods.
    """
    def __init__(self, simulation, housing_stock, household_df, write_story = False):
        """Define household inputs and outputs attributes.
        Initiate household's story list string. 
        
        simulation -- Pointer to SimPy simulation environment.
        household_df -- Dataframe row w/ household input attributes.
        housing_stock -- a SimPy FilterStore that acts as an occupied housing stock
        write_story -- Boolean indicating whether to track a households story.
        """
        
        # Household attributes
        self.household = household_df  # Dataframe w/ household input attributes
        self.name = household_df['Name']   # Name associated with occupant of the home %***%
        self.savings = household_df['Savings']  # Amount of household savings in $
        self.tenure_pref = household_df['Tenure Pref'] # Indicator of the household's preference between rent or own %***%
        self.occupancy_pref = household_df['Occupancy Pref'] # Indicator of the household's preference between occupancy types %***%
        
        self.prior_residence = []
        
        # Household simulation outputs
        self.story = []  # The story of events for each household
        self.home_search_start = 0.0  # Time started searching for a new home
        self.home_search_stop = 0.0  # Time found a new home
        self.money_search_start = 0.0  # Time that household started search for money
        self.money_search_stop = 0.0  # Time that household found rebuild money
        self.gave_up_money_search = False  # Whether household gave up search for money
        self.gave_up_home_search = False  # Whether household gave up search for home 
        
        # Initial method calls
        
        self.setResidence(simulation, housing_stock, household_df)
    
    def setResidence(self, simulation, housing_stock, household_df):
        """Initiate the household's residence based on input attributes
        then add their residence to the housing stock FilterStore.
        
        Keyword Arguments:
        simulation -- Pointer to SimPy simulation environment.
        household_df -- Dataframe row w/ household input attributes.
        housing_stock -- a SimPy FilterStore that acts as an occupied housing stock
        """
        self.residence = Residence(simulation, household_df) 
        housing_stock.put(self.residence)
        

    def story_to_text(self): 
        """Join list of story strings into a single story string."""
        return ''.join(self.story)

class Owner(Household):
    """Define a Owner() class to represent a group of persons that reside 
    together as a single analysis unit with attributes and methods.
    """
    def __init__(self, simulation, housing_stock, household_df, write_story = False):
        """Define household inputs and outputs attributes.
        Initiate household's story list string. 
        
        simulation -- Pointer to SimPy simulation environment.
        household_df -- Dataframe row w/ household input attributes.
        housing_stock -- a SimPy FilterStore that acts as an occupied housing stock
        write_story -- Boolean indicating whether to track a households story.
        """
        
        Household.__init__(self, simulation, housing_stock, household_df, 
                           write_story = False)
        
        # Owner attributes
        self.insurance = household_df['Insurance']  # Hazard-specific insurance coverage in $

         
        # Owner simulation outputs
        self.inspection_put = 0.0  # Time put request in for house inspection
        self.inspection_get = 0.0  # Time get  house inspection
        self.claim_put = 0.0  # Time put request in for insurance settlement
        self.claim_get = 0.0  # Time get insurance claim settled
        self.claim_payout = 0.0  # Amount of insurance claim payout
        self.assistance_put = 0.0  # Time put request in for FEMA assistance
        self.assistance_get = 0.0  # Time get FEMA assistance
        self.assistance_request = 0.0  # Amount of money requested from FEMA
        self.assistance_payout = 0.0  # Amount of assistance provided by FEMA
        self.money_to_rebuild = self.savings  # Total funds available to household to rebuild house
        self.home_put = 0.0  # Time put request in for house rebuild
        self.home_get = 0.0  # Time get house rebuild completed
        self.loan_put = 0.0  # Time put request for loan
        self.loan_get = 0.0  # Time get requested loan
        self.loan_amount = 0.0  # Amount of loan received
        self.permit_put = 0.0  # Time put request for building permit
        self.permit_get = 0.0  # Time get requested building permit
        
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
            '{0} owns and lives in a {1} bedroom {2} at {3} worth ${4:,.0f}. '.format(self.name, 
                                                            self.residence.bedrooms, 
                                                            self.residence.occupancy.lower(),
                                                            self.residence.address,
                                                            self.residence.value
                                                            )
            )

    def story_to_text(self): 
        """Join list of story strings into a single story string."""
        return ''.join(self.story)
        
class Renter(Household):
    """Define a Owner() class to represent a group of persons that reside 
    together as a single analysis unit with attributes and methods.
    """
    def __init__(self, simulation, housing_stock, household_df, write_story = False):
        """Define household inputs and outputs attributes.
        Initiate household's story list string. 
        
        simulation -- Pointer to SimPy simulation environment.
        household_df -- Dataframe row w/ household input attributes.
        housing_stock -- a SimPy FilterStore that acts as an occupied housing stock
        write_story -- Boolean indicating whether to track a households story.
        """
        
        Household.__init__(self, simulation, housing_stock, household_df, 
                           write_story = False)
        
        self.landlord = []

         
        # Household simulation outputs
        
        
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
            '{0} rents and lives in a {1} bedroom {2} at {3} worth ${4:,.0f}. '.format(self.name, 
                                                            self.residence.bedrooms, 
                                                            self.residence.occupancy.lower(),
                                                            self.residence.address,
                                                            self.residence.value
                                                            )
            )

    def story_to_text(self): 
        """Join list of story strings into a single story string."""
        return ''.join(self.story)
        


class Landlord(object):
    """Define a Landlord() class to represent ____
    
    """
    def __init__(self, write_story = False):
        """Define landlord's inputs and outputs attributes.
        Initiate landlord's story list string. 
        
        write_story -- Boolean indicating whether to track a households story.
        """
        
        # Landlord simulation inputs
        self.name = names.get_first_name() # Random name associated with household
        self.savings = 0.5  # Amount of landlord savings as percentage of property value (cash ratio)
        self.insurance = 0.85 # Hazard-specific insurance coverage as percentage of replacement cost (includes deductible)
        self.money_to_rebuild = self.savings   # Total funds available to landlord to rebuild building
        
        self.residence = []
        self.tenant = []
         
        # Household simulation outputs
        self.story = []  # The story of events for each household
        self.inspection_put = 0.0  # Time put request in for house inspection
        self.inspection_get = 0.0  # Time get  house inspection
        self.claim_put = 0.0  # Time put request in for insurance settlement
        self.claim_get = 0.0  # Time get insurance claim settled
        self.claim_payout = 0.0  # Amount of insurance claim payout
        self.assistance_put = 0.0  # Time put request in for FEMA assistance
        self.assistance_get = 0.0  # Time get FEMA assistance
        self.assistance_request = 0.0  # Amount of money requested from FEMA
        self.assistance_payout = 0.0  # Amount of assistance provided by FEMA

        self.home_put = 0.0  # Time put request in for house rebuild
        self.home_get = 0.0  # Time get house rebuild completed
        self.loan_put = 0.0  # Time put request for loan
        self.loan_get = 0.0  # Time get requested loan
        self.loan_amount = 0.0  # Amount of loan received
        self.permit_put = 0.0  # Time put request for building permit
        self.permit_get = 0.0  # Time get requested building permit
        self.money_search_start = 0.0  # Time that household started search for money
        self.money_search_stop = 0.0  # Time that household found rebuild money
        self.gave_up_money_search = False  # Whether household gave up search for money
        self.gave_up_home_search = False  # Whether household gave up search for home 
        
        # Initial method calls

#        self.setStory(write_story)  # Start stories with non-disaster attributes
    
        
#    def setStory(self, write_story):
#        """Initiate the landlords's story based on input attributes.
#        
#        Keyword Arguments:
#        write_story -- Boolean indicating whether to track a story.
#        """
#        if write_story == True:
#            # Set story with non-disaster attributes.
#            self.story.append()
#            )
                

    def story_to_text(self): 
        """Join list of story strings into a single story string."""
        return ''.join(self.story)
        

def importHouseholds(simulation, housing_stock, households_df, write_story = False):
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
        households.append(Household(simulation, housing_stock, households_df.iloc[i], write_story))
    
    return households


def importOwners(simulation, housing_stock, households_df, write_story = False):
    """Return list of entities.Owner() objects from dataframe containing
    data describing households.
    
    Keyword Arguments:
    simulation -- Pointer to SimPy simulation environment.
    household_df -- Dataframe row w/ household input attributes.
    write_story -- Boolean indicating whether to track a households story.
    """
    
    owners = []

    # Population the simulation with households from the households dataframe
    for i in households_df.index:
        owners.append(Owner(simulation, housing_stock, households_df.iloc[i], write_story))
    
    return owners

def importRenters(simulation, housing_stock, households_df, write_story = False):
    """Return list of entities.Renter() objects from dataframe containing
    data describing households.
    
    Keyword Arguments:
    simulation -- Pointer to SimPy simulation environment.
    household_df -- Dataframe row w/ household input attributes.
    write_story -- Boolean indicating whether to track a households story.
    """
    
    renters = []

    # Population the simulation with households from the households dataframe
    for i in households_df.index:
        renters.append(Renter(simulation, housing_stock, households_df.iloc[i], write_story))
    

    return renters
    
def assignLandlords(renters, landlords, write_story = False):
    """Return list of entities.Owner() objects from dataframe containing
    data describing households.
    
    Keyword Arguments:
    simulation -- Pointer to SimPy simulation environment.
    renters -- List of entities.Renters()
    landlords -- List of entities.Landlords()
    write_story -- Boolean indicating whether to track a households story.
    """
        
    for i, renter in enumerate(renters):
        renter.landlord = landlords[i]
        renter.landlord.residence = renter.residence
        renter.landlord.tenant = renter
    
        if write_story == True:
            # Indicate renter's landlord in their story.
            renter.story.append(
                              '{0}\'s residence is owned by {1}. '.format(renter.name, 
                              renter.landlord.name
                              )
                )