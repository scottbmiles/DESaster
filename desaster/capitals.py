# -*- coding: utf-8 -*-
"""
Created on Wed Jan 20 15:08:52 2016

@author: Derek, Scott
"""
from simpy import Resource, Container, Interrupt

class HumanCapital(): # --% created a separate class for just human capitals %--
    """
    
    """
    def __init__(self, simulation, human_cap_data): # --% changed argument name %--
                
        self.data = human_cap_data
        
        ## HUMAN CAPITALS ## --% changed to make reference to human_cap_data %--
        
        try:
            self.inspectors = Resource(simulation, human_cap_data['inspectors'])
            self.insurance_adjusters = Resource(simulation, human_cap_data['insurance adjusters'])
            self.fema_processors = Resource(simulation, human_cap_data['fema processors'])
            self.permit_processors = Resource(simulation, human_cap_data['permit processors'])
            self.contractors = Resource(simulation, human_cap_data['contractors'])
            self.loan_processors = Resource(simulation, human_cap_data['loan processors'])
            self.engineers = Resource(simulation, human_cap_data['engineers'])
        except ValueError as e:
            
            print ("You are missing a config value, or your value is zero. All" 
                    "values must have a positive number, see error: {0}".format(e))
        except KeyError as f:
            print ("You are missing {0} as a capital. Please re-add in your"
                    " config file".format(f))
                    
        except Exception as g:
            print ("Something went really wrong, capitals failed to load."
                    " See error {0}".format(g))

class FinancialCapital(): # --% created a separate class for just financial capitals %--
        def __init__(self, simulation, financial_cap_data): # --% changed/added arguments %--
            
            self.fema_aid = Container(simulation, init=financial_cap_data['fema aid'])
        
class BuiltCapital(): # --% created a separate class for just financial capitals %--
        def __init__(self, simulation, asset):
            self.setYearBuilt(asset)
            self.setValue(asset)
            self.setDamageState(asset)  
            self.setDamageValue(asset) 
            self.setInspection(simulation, asset)
        def setYearBuilt(self, asset):
            self.age = asset['Year Built']
        def setValue(self, asset):
            self.value = asset['Value']
        def setDamageState(self, asset):
            self.damage_state = asset['Damage State']
        def setDamageValue(self, asset):
            self.damage_value = asset['Damage Value']
        def setInspection(self, simulation, asset):
            self.inspection = simulation.event()
            self.inspect_start = None
            self.inspect_stop = None

class Building(BuiltCapital):
    def __init__(self, simulation, building):
        self.setAddress(building)
#         self.setResident(building)
        try:
            self.setOccupancy(building)
        except AttributeError:
            print('Invalid occupancy type provided: {0}.'.format(building['occupancy']))
        self.setMonthlyCost(building)
        self.setYearBuilt(asset)
        self.setValue(building)
        self.setDamageState(building)  
        self.setDamageValue(building) 
        self.setInspection(simulation, building)
    def setAddress(self, building):
        self.address = building['Address']
    def setOccupancy(self, building):
        self.occupancy = building['Occupancy']
    def setMonthlyCost(self, building):
        self.cost = building['Cost']
    def setBuildingArea(self, building):
        self.cost = building['Area']

        
class Residence(Building):
    #Can verify that occupancy types only relate to residences
    def __init__(self, simulation, residence):
        self.setAddress(residence)
        self.setBuildingArea(residence)
        self.setMonthlyCost(residence)
        self.setOccupancy(residence)
        self.setBedrooms(residence)
        self.setBathrooms(residence)
        self.setYearBuilt(residence)
        self.setValue(residence)
        self.setDamageState(residence)  
        self.setDamageValue(residence) 
        self.setInspection(simulation, residence)
    def setOccupancy(self, residence):
        if residence['Occupancy'] in ('Single Family', 'Multi Family', 'Mobile', 'Condo'):
            self.occupancy = residence['Occupancy']
        else:
            raise AttributeError(residence['Occupancy'])
    def setBedrooms(self, residence):
        self.bedrooms = residence['Bedrooms']
    def setBathrooms(self, residence):
        self.bathrooms = residence['Bathrooms']



