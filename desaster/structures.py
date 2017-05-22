# -*- coding: utf-8 -*-
"""
Module of classes that represent different types of buildings used by DESaster
entities.

Classes:
Building(object)
SingleFamilyResidential(Building)

@author: Scott Miles (milessb@uw.edu)
"""

from desaster.hazus import setDamageValueHAZUS
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
        building -- A dataframe row with required building attributes.
        """
        # Attributes
        self.owner = owner  # Owner of building as Household() entity
        self.cost = cost  # Monthly rent/mortgage of building
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
        self.damage_value = setDamageValueHAZUS(value, occupancy, damage_state) # Use HAZUS lookup tables to assign damage value.
        self.damage_value_start = self.damage_value # Archive original damage value
        
        # Outputs and intermediate variables
        self.inspected = False  # Whether the building has been inspected
        self.permit = False  # Whether the building has a permit
        self.assessment = False  # Whether the building has had engineering assessment

class SingleFamilyResidential(Building):
    """Define class that inherits from Building() for representing the
    attributes and methods associated with a single family residence. Currently
    just adds attribues of bedrooms and bathroom and verifies a HAZUS-compatible
    residential building type is specified.
    """
    def __init__(self, owner = None, occupancy = None, address = None, longitude = None,
                    latitude = None, value = None, cost = None, area = None,
                    bedrooms = None, bathrooms = None, listed = False, damage_state = None,
                    building_stock = None):
        """Run initial methods for defining building attributes.

        Keyword Arguments:
        env -- Pointer to SimPy env environment.
        building -- A dataframe row with required building attributes.
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