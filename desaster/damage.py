# -*- coding: utf-8 -*-
"""
Created on Sat July 2 2016

@author: Scott

functions related to damage and loss
"""
import pandas as pd

def struct_damage(residence)
    file_path = "../inputs/structural_repair_cost_ratios.csv"
    struct_repair_costs = pd.read_csv(file_path)

    struct_damage_ratio = struct_repair_costs.ix[residence.occupancy][residence.damage_state] / 100.0

    residence.damage_value = struct_damage_ratio * residence.value
    