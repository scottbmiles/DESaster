# -*- coding: utf-8 -*-
"""
Created on Wed Jan 20 15:08:52 2016

@author: Derek
"""
import simpy
import csv

class Capitals():
    """This is the main resource data structure.
    
        Provide a data dictionary. The dictionary MUST include all the
        resources listed below. 
    """
    def __init__(self, simulation, data):
                
        self.data = data
        ## HUMAN CAPITALS ##
        
        try:
            self.inspectors = simpy.Resource(simulation, data['inspectors'])
            self.insurance_adjusters = simpy.Resource(simulation, data['insurance adjusters'])
            self.fema_processors = simpy.Resource(simulation, data['fema processors'])
            self.permit_processors = simpy.Resource(simulation, data['permit processors'])
            self.contractors = simpy.Resource(simulation, data['contractors'])
            self.loan_processors = simpy.Resource(simulation, data['loan processors'])
            self.engineers = simpy.Resource(simulation, data['engineers'])
        except ValueError as e:
            
            print ("You are missing a config value, or your value is zero. All" 
                    "values must have a positive number, see error: {0}".format(e))
        except KeyError as f:
            print ("You are missing {0} as a capital. Please re-add in your"
                    " config file".format(f))
                    
        except Exception as g:
            print ("Something went really wrong, capitals failed to load."
                    " See error {0}".format(g))

        ## FINANCIAL CAPITALS ##
        self.fema_aid = simpy.Container(simulation, data['fema aid'])
        
        ## Households ##
        self.housing_stock = self.load_households(simulation) #FILTERSTORE
            
    def get_capitals_list(self):
        c_list = []
        for i in dir(self):
            if "__" not in i:
                c_list.append(i)
        return c_list
        
    def get_capitals_values(self):
        return self.data
        
    def load_households(self, simulation): #this is only used internally
        #TODO load all input files from the IO file
        input_file = "C:/Users/Derek/Dropbox/Simulation/SeaGrantSimulation/Inputs/housing_stock.csv"
        stock = []
        with open(input_file) as file:
            reader = csv.reader(file)
            for i in reader:
                stock.append(House(i)) #House is a class defined below
        stock.pop(0)
        housing_stock = simpy.Store(simulation)
        for i in stock:
            housing_stock.put(i)
        
        return housing_stock
            
class House:
    def __init__(self, inp):
        self.number = inp[0]
        self.lat = inp[2]
        self.long = inp[1]
        
