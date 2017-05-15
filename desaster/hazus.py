# -*- coding: utf-8 -*-
"""
Module for parameterizing DESaster variables based on HAZUS associated lookup
tables.

@author: Scott Miles
"""
import pandas as pd

#### HAZUS LOOKUP TABLE INPUT/OUTPUT #########################################
# Currently input data must use format laid out in 
# "../inputs/hazus_parameters.xlsx". Any changes to lookup values should
# maintain the format. However, currently there is no better alternative for
# quick damage valuation based on building occupancy type. When there is, 
# can be revised to take different files for different lookup tables etc.
# ############################################################################

# Excel workbook with lookup tables from HAZUS-MH earthquake model technical
# manual. (http://www.fema.gov/media-library/assets/documents/24609)
hazus_parameters_file = "../config/hazus_building_lookup_tables.xlsx"

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

def setDamageValueHAZUS(building_value, occupancy, damage_state):
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
    struct_repair_ratio = structural_damage_ratios.ix[occupancy][damage_state] / 100.0
    accel_repair_ratio = acceleration_damage_ratios.ix[occupancy][damage_state] / 100.0
    drift_repair_ratio = drift_damage_ratios.ix[occupancy][damage_state] / 100.0
    
    return building_value * (struct_repair_ratio + accel_repair_ratio + drift_repair_ratio)

##### END HAZUS LOOKUP TABLE INPUT/OUTPUT ############################