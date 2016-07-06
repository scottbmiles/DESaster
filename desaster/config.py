# -*- coding: utf-8 -*-
"""
Created on Wed Feb 10 12:45:29 2016

@author: Derek, Scott
"""

#configs

import random
import pandas as pd

hazus_parameters_file = "../inputs/hazus_parameters.xlsx"

random.seed(69)

inspection_mean = 10.0
inspection_std = 0
inspection_time = abs(random.gauss(inspection_mean, inspection_std))

adjuster_mean = 15.0
adjuster_std = 0.0
adjuster_time = abs(random.gauss(adjuster_mean, adjuster_std))

fema_process_mean = 20.0
fema_process_std = 0.0
fema_process_time = abs(random.gauss(fema_process_mean, fema_process_std))

engineering_mean = 25.0
engineering_std = 0.0
engineering_assessment_time = abs(random.gauss(engineering_mean, engineering_std))

loan_process_mean = 30.0
loan_process_std = 0.0
loan_process_time = abs(random.gauss(loan_process_mean, loan_process_std))

permit_process_mean = 35.0
permit_process_std = 0.0
permit_process_time = abs(random.gauss(permit_process_mean, permit_process_std))

mobile_rebuild_mean = 40.0
mobile_rebuild_std = 0.0
mobile_rebuild_time = abs(random.gauss(mobile_rebuild_mean, mobile_rebuild_std))

sfr_rebuild_mean = 45.0
sfr_rebuild_std = 0.0
sfr_rebuild_time = abs(random.gauss(sfr_rebuild_mean, sfr_rebuild_std))

mfr_rebuild_mean = 50.0
mfr_rebuild_std = 0.0
mfr_rebuild_time = abs(random.gauss(mfr_rebuild_mean, mfr_rebuild_std))

building_repair_times = pd.read_excel(hazus_parameters_file, 
                            sheetname='Repair times', 
                            index_col='Occupancy')

structural_damage_ratios = pd.read_excel(hazus_parameters_file, 
                                sheetname='Struct. Repair Cost % of value', 
                                index_col='Occupancy')
                                          
acceleration_damage_ratios = pd.read_excel(hazus_parameters_file, 
                            sheetname='Accel non-struc repair cost', 
                            index_col='Occupancy')
                                          
drift_damage_ratios = pd.read_excel(hazus_parameters_file, 
                        sheetname='Deflect non-struc repair cost', 
                        index_col='Occupancy')
                     