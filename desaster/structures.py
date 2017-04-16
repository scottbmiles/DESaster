# -*- coding: utf-8 -*-
"""
Module of classes that represent different types of buildings used by DESaster
entities.

Classes:
Building(object)
SingleFamilyResidential(Building)

@author: Scott Miles (milessb@uw.edu)
"""

from desaster.config import structural_damage_ratios
from desaster.config import acceleration_damage_ratios
from desaster.config import drift_damage_ratios
from desaster import config
import pandas as pd

class Building(object):
    """Top-level class for representing attributes and methods of different types 
    of buildings. Currently the possible damage states of the building must 
    match the same possible damage states of buildings in HAZUS. A lookup table
    from HAZUS is then used to assign the associated damage value for the particular
    occupancy type.
    
    Functions:
    setDamageValue(self, building)
    """
    def __init__(self, building):
        """Run initial methods for defining building attributes.
        
        Keyword Arguments:
        building -- A dataframe row with required building attributes.
        """
        
        self.owner = None  # Owner of building as Household() entity %***%
        self.cost = building['Cost']  # Monthly rent/mortgage of building
        self.age = building['Year Built']  # Year building was built
        self.value = building['Value']  # Value of the building in $
        self.damage_state = building['Damage State']  # HAZUS damage state
        self.inspected = False  # Whether the building has been inspected
        self.permit = False  # Whether the building has a permit
        self.assessment = False  # Whether the building has had engineering assessment    
        self.occupancy = building['Occupancy']  # Occupancy type of building
        self.area = building['Area']  # Floor area of building
        try: #if address isn't in dataframe, we'll just set it to none
            self.address = building['Address']  # Address of building
        except:  
            self.address = 'unknown address'
        try: #if lat/long aren't in data, we'll set to none
            self.latitude = building['Latitude']
            self.longitude = building['Longitude']
        except:
            self.latitude = None
            self.longitude = None

        self.setDamageValue(building)  # Use HAZUS lookup tables to assign damage value.  
    
    def setDamageValue(self, building):
        """Calculate damage value for building based on occupancy type and
        HAZUS damage state.

        Function uses three lookup tables (Table 15.2, 15.3, 15.4) from the HAZUS-MH earthquake model
        technical manual for structural damage, acceleration related damage,
        and for drift related damage, respectively. Estimated damage value for
        each type of damage is summed for total damage value.
        http://www.fema.gov/media-library/buildings/documents/24609
        
        Keyword Arguments:
        structural_damage_ratios -- dataframe set in config.py
        acceleration_damage_ratios -- dataframe set in config.py
        drift_damage_ratios -- dataframe set in config.py
        """
        struct_repair_ratio = structural_damage_ratios.ix[building['Occupancy']][building['Damage State']] / 100.0
        accel_repair_ratio = acceleration_damage_ratios.ix[building['Occupancy']][building['Damage State']] / 100.0
        drift_repair_ratio = drift_damage_ratios.ix[building['Occupancy']][building['Damage State']] / 100.0
        self.damage_value = building['Value']*(struct_repair_ratio +
                                                accel_repair_ratio +
                                                drift_repair_ratio)

class SingleFamilyResidential(Building):
    """Define class that inherits from Building() for representing the
    attributes and methods associated with a single family residence. Currently
    just adds attribues of bedrooms and bathroom and verifies a HAZUS-compatible
    residential building type is specified.
    """
    def __init__(self, building):
        """Run initial methods for defining building attributes.

        Keyword Arguments:
        env -- Pointer to SimPy env environment.
        building -- A dataframe row with required building attributes.
        """
    
        Building.__init__(self, building) # %***%s
        
        try:
            self.bedrooms = building['Bedrooms']  # Number of bedrooms in building
        except:  
            self.bedrooms = 0
        try:
            self.bathrooms = building['Bathrooms']  # Number of bedrooms in building
        except:  
            self.bathrooms = 0
        
        # Verify that building dataframe has expected occupancy types
        if not building['Occupancy'].lower() in ('single family dwelling', 'mobile home'):
            print('Warning: SingleFamilyResidential not compatible with given occupancy type: {0}'.format(
                    building['Occupancy'].title())) 
