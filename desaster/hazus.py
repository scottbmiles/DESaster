# -*- coding: utf-8 -*-
"""
Copyright (C) 2018  Scott B. Miles, milessb@uw.edu, scott.miles@resilscience.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
    
Module for parameterizing DESaster variables based on HAZUS associated lookup
tables.

Currently input data must use format laid out in 
"../inputs/hazus_parameters.xlsx". Any changes to lookup values should
maintain the format. However, currently there is no better alternative for
quick damage valuation based on building occupancy type. When there is, 
can be revised to take different files for different lookup tables etc.

@author: Scott Miles
"""
import pandas as pd
import os as os
from scipy.stats import rv_discrete

# Excel workbook with lookup tables from HAZUS-MH earthquake model technical
# manual. (http://www.fema.gov/media-library/assets/documents/24609)
module_path = os.path.dirname(os.path.abspath(__file__))
hazus_parameters_file = module_path + "/config/hazus_building_lookup_tables.xlsx"

# Building repair time lookup table from HAZUS-MH earthquake model technical
# manual Table 15.9 (http://www.fema.gov/media-library/assets/documents/24609)
building_repair_times = pd.read_excel(hazus_parameters_file, 
                            sheetname='Repair times', 
                            index_col='Occupancy')

# Structural damage value ratio lookup table from HAZUS-MH earthquake model technical
# manual Table 15.2 (http://www.fema.gov/media-library/assets/documents/24609)
structural_damage_ratios = pd.read_excel(hazus_parameters_file, 
                                sheetname='Struct. Repair Cost % of value', 
                                index_col='Occupancy')
        
# Acceleration damage value ratio lookup table from HAZUS-MH earthquake model technical
# manual Table 15.3 (http://www.fema.gov/media-library/assets/documents/24609)                                  
acceleration_damage_ratios = pd.read_excel(hazus_parameters_file, 
                            sheetname='Accel non-struc repair cost', 
                            index_col='Occupancy')
    
# Drift damage value ratio lookup table from HAZUS-MH earthquake model technical
# manual Table 15.4 (http://www.fema.gov/media-library/assets/documents/24609)                                       
drift_damage_ratios = pd.read_excel(hazus_parameters_file, 
                        sheetname='Deflect non-struc repair cost', 
                        index_col='Occupancy')
    
# A conditional probability table to map HAZUS damage states to Burton et al.
# recovery-based limit states.
recovery_limit_states = pd.read_excel(hazus_parameters_file, 
                        sheetname='Recovery limit states', 
                        index_col='Damage State')

def setStructuralDamageValueHAZUS(building):
    """Calculate damage value for building based on occupancy type and
    HAZUS damage state.

    Function uses three lookup tables (Table 15.2, 15.3, 15.4) from the HAZUS-MH earthquake model
    technical manual for structural damage, acceleration related damage,
    and for drift related damage, respectively. Estimated damage value for
    each type of damage is summed for total damage value.
    http://www.fema.gov/media-library/buildings/documents/24609

    Keyword Arguments:
    structural_damage_ratios -- HAZUS damage lookup table (see above)
    acceleration_damage_ratios -- HAZUS damage lookup table (see above)
    drift_damage_ratios -- HAZUS damage lookup table (see above)
    """
    struct_repair_ratio = structural_damage_ratios.ix[building.occupancy][building.damage_state] / 100.0
    accel_repair_ratio = acceleration_damage_ratios.ix[building.occupancy][building.damage_state] / 100.0
    drift_repair_ratio = drift_damage_ratios.ix[building.occupancy][building.damage_state] / 100.0
    
    building.damage_value = building.value * (struct_repair_ratio + accel_repair_ratio + drift_repair_ratio)
    

def setContentsDamageValueHAZUS(building):
    """Calculate value of building content loss value for building based on
    HAZUS damage state.

    Function uses a lookup table (Table 15.5) from the HAZUS-MH earthquake model
    technical manual for contents damage ratios. Estimated damage value for
    each type of damage is summed for total damage value.
    http://www.fema.gov/media-library/buildings/documents/24609

    NOTE: Unlike structural damage, HAZUS uses the same contents damage ratio
    for all occupancy type. Hence, no lookup table  is imported below.
    
    *** NOT BEING USED RIGHT NOW. IF DO EVENTUALLY START USING REVISE SO THAT 
    building.content_damage_value (OR WHATEVER CALLED) IS SET DIRECTLY RATHER
    THAN VIA A RETURN. ***
    """
    if building.damage_state.lower() == 'none':
        return 0.0*(building.area*30)
    if building.damage_state.lower() == 'slight':
        return 0.01*(building.area*30)
    if building.damage_state.lower() == 'moderate':
        return 0.05*(building.area*30)
    if building.damage_state.lower() == 'extensive':
        return 0.25*(building.area*30)
    if building.damage_state.lower() == 'complete':
        return 0.5*(building.area*30)

def setRecoveryLimitState(building):
    """ A function to set a building's recovery-based limit state.
    
    The function take a building's HAZUS-based damage state and maps it to a 
    Burton et al. recovery-based limit state based on a specified conditional
    probability table (imported above).
    
    Arguments:
    building -- a desaster.structures.Building object
    
    Attribute Changes:
    building.recovery_limit_state
    
    """
    recovery_limit_state_dist = rv_discrete(values=([0, 1, 2, 3, 4],
                                recovery_limit_states.loc[building.damage_state].values))
    recovery_limit_state_code = recovery_limit_state_dist.rvs()
    code_label_lookup = {0: 'Functional', 1: 'Disfunctional', 2: 'Unsafe', 3: 'Irreparable', 4: 'Collapse'}
    building.recovery_limit_state = code_label_lookup[recovery_limit_state_code]
