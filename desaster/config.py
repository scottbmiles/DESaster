# -*- coding: utf-8 -*-
"""
Created on Wed Feb 10 12:45:29 2016

@author: Derek, Scott
"""

#configs

import random

random.seed(69)

inspection_mean = 14.0
inspection_std = 0
inspection_time = abs(random.gauss(inspection_mean, inspection_std))

adjuster_mean = 90.0
adjuster_std = 0.0
adjuster_time = abs(random.gauss(adjuster_mean, adjuster_std))

fema_process_mean = 60.0
fema_process_std = 0.0
fema_process_time = abs(random.gauss(fema_process_mean, fema_process_std))

engineering_mean = 14.0
engineering_std = 0.0
engineering_assessment_time = abs(random.gauss(engineering_mean, engineering_std))

loan_process_mean = 90.0
loan_process_std = 0.0
loan_process_time = abs(random.gauss(loan_process_mean, loan_process_std))

permit_process_mean = 30.0
permit_process_std = 0.0
permit_process_time = abs(random.gauss(permit_process_mean, permit_process_std))

sfr_rebuild_mean = 30.0
sfr_rebuild_std = 0.0
sfr_rebuild_time = abs(random.gauss(sfr_rebuild_mean, sfr_rebuild_std))