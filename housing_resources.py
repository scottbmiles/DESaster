# -*- coding: utf-8 -*-
"""
Created on Sun Dec 20 09:44:46 2015

@author: geomando, dhuling

Dependencies: pandas 17+, SimPy 3+, numpy
"""

import simpy
import numpy
import pandas as pd


# Durable resources class definition based on SimPy base Resource class
class DurableResource:
    def __init__(self, simulation, durables_dict):
        self.simulation = simulation
        self.durables = durables_dict
        self.fill()
    
    #Fill is an internal method to fill the dictionary of resource objects
    def fill(self):
        self.category = {}
        for resource, quantity in self.durables.iteritems():
            self.category[resource] = simpy.Resource(self.simulation, quantity)
            self.quantity = quantity

# Nondurable resources class definition based on SimPy Container class
class NondurableResource:
    def __init__(self, simulation, nondurables_dict):
        self.simulation = simulation
        self.nondurables = nondurables_dict
        self.fill()

    #Fill is an internal method to fill the dictionary of resource objects
    def fill(self):
        self.category = {}
        for resource, quantity in self.nondurables.iteritems():
            self.category[resource] = simpy.Container(self.simulation, capacity=1000000000000, init=quantity)
            self.quantity = quantity