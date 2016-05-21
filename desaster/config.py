# -*- coding: utf-8 -*-
"""
Created on Wed Feb 10 12:45:29 2016

@author: Derek
"""

#configs

import random

random.seed(69)

inspection_time = abs(random.gauss(.5, 0.5))

adjuster_time = abs(random.gauss(1.0, 1.0))

fema_process_time = abs(random.gauss(1, 1.00))

engineering_assessment_time = abs(random.gauss(1.0, 1.0))

loan_process_time = abs(random.gauss(10.0, 10.0))

permit_process_time = abs(random.gauss(3.0, 3.0))