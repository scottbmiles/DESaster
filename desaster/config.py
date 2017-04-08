# -*- coding: utf-8 -*-
"""
Module for defining variables for a suite of DESaster paramaters. 

@author: Scott Miles
"""

#configs

import pandas as pd

# Excel workbook with lookup tables from HAZUS-MH earthquake model technical
# manual. (http://www.fema.gov/media-library/assets/documents/24609)
hazus_parameters_file = "../inputs/hazus_parameters.xlsx"


# % of damage value related to building materials (vs. labor and profit)
materials_cost_pct = 1.0 

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

                     