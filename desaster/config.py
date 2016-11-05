# -*- coding: utf-8 -*-
"""
Module for defining variables for a suite of DESaster paramaters. 

@author: Derek Huling, Scott Miles
"""

#configs

import random
import pandas as pd

# Excel workbook with lookup tables from HAZUS-MH earthquake model technical
# manual. (http://www.fema.gov/media-library/assets/documents/24609)
hazus_parameters_file = "../inputs/hazus_parameters.xlsx"

random.seed(69)

# Parameters for defining a normal distribution for representing the duration
# required to inspect structures from the time of a hazard event.
inspection_mean = 1.0
inspection_std = 0
inspection_time = abs(random.gauss(inspection_mean, inspection_std))

# Parameters for defining a normal distribution for representing the duration
# required to process an insurance claim from time claim is submitted.
adjuster_mean = 15.0
adjuster_std = 0.0
adjuster_time = abs(random.gauss(adjuster_mean, adjuster_std))

# Parameters for defining a normal distribution for representing the duration
# required to process an FEMA aid request from time request is submitted.
fema_process_mean = 20.0
fema_process_std = 0.0
fema_process_time = abs(random.gauss(fema_process_mean, fema_process_std))

# Parameters for defining a normal distribution for representing the duration
# required to conduct engineering assessment from time assessment is requested.
engineering_mean = 25.0
engineering_std = 0.0
engineering_assessment_time = abs(random.gauss(engineering_mean, engineering_std))

# Parameters for defining a normal distribution for representing the duration
# required to process a loan application from time application is submitted.
loan_process_mean = 30.0
loan_process_std = 0.0
loan_process_time = abs(random.gauss(loan_process_mean, loan_process_std))

# Parameters for defining a normal distribution for representing the duration
# required to process building permit request from time permit is requested.
permit_process_mean = 35.0
permit_process_std = 0.0
permit_process_time = abs(random.gauss(permit_process_mean, permit_process_std))

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
                     