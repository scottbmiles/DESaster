# -*- coding: utf-8 -*-
"""
Module of classes that represent different types of buildings used by DESaster
entities.

Classes:
Building(object)
SingleFamilyResidential(Building)

@author: Scott Miles (milessb@uw.edu)
"""

from desaster.hazus import setStructuralDamageValueHAZUS, setRecoveryLimitState
import pandas as pd
import warnings, sys, distutils.util

class Building(object):
    """Top-level class for representing attributes and methods of different types
    of buildings. Currently the possible damage states of the building must
    match the same possible damage states of buildings in HAZUS. A lookup table
    from HAZUS is then used to assign the associated damage value for the particular
    occupancy type.

    Functions:
    setDamageValue(self, building)
    """
    def __init__(self, owner = None, occupancy = None, address = None, longitude = None,
                    latitude = None, value = None, cost = None, area = None,
                    listed = False, damage_state = None, building_stock = None):
        """

        Keyword Arguments:
        owner -- entities.Owner or subclass that represents building owner.
        occupancy -- The buildings occupancy. DESaster currently supports SFR and mobile home.
        address -- Building's address
        longitude -- Building's longitude
        latitude -- Building's latitude
        value -- Building's value in $
        cost -- Building's monthly cost in $ (e.g., mortgage or rent)
        area -- Building's area in sf
        listed -- Whether building is for rent or sale.
        damage_state -- Building's damage state (e.g., HAZUS damage states)
        building_stock -- The the building's associated building stock FilterStore
        
        Modified Attributes:
        self.damage_value -- Calculated using setStructuralDamageValueHAZUS()
        """
        # Attributes
        self.owner = owner  # Owner of building as Household() entity
        self.monthly_cost = cost  # Monthly rent/mortgage of building
        self.value = value  # Value of the building in $
        self.damage_state = damage_state  # HAZUS damage state
        self.damage_state_start = damage_state  # Archive starting damage state
        self.occupancy = occupancy  # Occupancy type of building
        self.area = area  # Floor area of building
        try:
            self.listed = distutils.util.strtobool(listed)
        except:
            self.listed = listed
        self.address = address # Address of building
        self.latitude = latitude
        self.longitude = longitude
        self.stock = building_stock # The building stock FilterStor the building belongs to
        
        # Outputs and intermediate variables
        self.inspected = False  # Whether the building has been inspected
        self.permit = False  # Whether the building has a permit
        self.assessment = False  # Whether the building has had engineering assessment
        
        # Use HAZUS lookup tables to assign damage value.
        setStructuralDamageValueHAZUS(self)
        self.damage_value_start = self.damage_value # Archive original damage value
        
        # Set Burton et al. recovery-based limit state
        setRecoveryLimitState(self)
        self.recovery_limit_state_start = self.recovery_limit_state # Archive original damage value

class SingleFamilyResidential(Building):
    """Define class that inherits from Building() for representing the
    attributes and methods associated with a single family residence. Currently
    just adds attribuees of bedrooms and bathroom and verifies a HAZUS-compatible
    residential building type is specified.
    """
    def __init__(self, owner = None, occupancy = None, address = None, longitude = None,
                    latitude = None, value = None, cost = None, area = None,
                    bedrooms = None, bathrooms = None, listed = False, damage_state = None,
                    building_stock = None):
        """
        Keyword Arguments:
        owner -- entities.Owner or subclass that represents building owner.
        occupancy -- The buildings occupancy. DESaster currently supports SFR and mobile home.
        address -- Building's address
        longitude -- Building's longitude
        latitude -- Building's latitude
        value -- Building's value in $
        cost -- Building's monthly cost in $ (e.g., mortgage or rent)
        bedrooms -- Building's number of bedrooms
        bathrooms -- Building's number of bathrooms
        area -- Building's area in sf
        listed -- Whether building is for rent or sale.
        damage_state -- Building's damage state (e.g., HAZUS damage states)
        building_stock -- The the building's associated building stock FilterStore
        
        Modified Attributes:
        self.damage_value -- Calculated using setStructuralDamageValueHAZUS()
        
        Inheritance:
        structures.Building
        """

        Building.__init__(self, owner, occupancy, address, longitude,
                        latitude, value, cost, area,
                        listed, damage_state, building_stock) 

        self.bedrooms = bedrooms  # Number of bedrooms in building
        self.bathrooms = bathrooms # Number of bedrooms in building

        # Verify that building dataframe has expected occupancy types
        # Raise warning, if not (but continue with simulation)
        if not occupancy.lower() in ('single family dwelling', 'mobile home'):
            warnings.showwarning('Warning: SingleFamilyResidential not compatible with given occupancy type: {0}'.format(
                    occupancy.title()), DeprecationWarning, filename = sys.stderr,
                                    lineno=661)