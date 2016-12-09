# -*- coding: utf-8 -*-
"""
Created on Wed Jan 20 14:19:52 2016

@author: Derek
Main Simulation
"""
#standard libs
import sys

#3rd Party Libs
import simpy
import pandas as pd

#Aftermath modules
import _requests #all requests processes are held in this py file
from entities import Household
import resources




#---------Main Code Here --------------
#Main sim env
simulation = simpy.Environment()

#Setting up Resources
"""Unless we make these constants actually stocastic we should just put them
directly in the dictionary when instantiating the resource objects, otherwise
its pretty redundant and annoying. Alternatively we could put all the resources
into the resource file and just import the ones we are using, i.e. all the 
set up code would be hard coded for now until we change it later with user
input."""
NUM_INSPECTORS = 1  #Number of Inspectors 
NUM_FEMA_PROCESSORS = 4 #Number of FEMA assistance application processors
NUM_INSURANCE_ADJUSTERS = 2 #Number of insurance claim adjusters
NUM_CONTRACTORS = 4 #Number of Contractors
FEMA_ASSISTANCE_BUDGET = 100000



durables = resources.DurableResource(simulation,
                                     {"inspectors": NUM_INSPECTORS,   
                                     "fema processors": NUM_FEMA_PROCESSORS,
                                     "claim adjusters": NUM_INSURANCE_ADJUSTERS,
                                     "contractors": NUM_CONTRACTORS,
                                     })
             


nondurables = resources.NondurableResource(simulation, 
                                           {"fema assistance": FEMA_ASSISTANCE_BUDGET})

buildings = None #placeholder for a buildings filterstore resource object

#setting up entities

households_inputs_dict = {'name' : ['Bill', 'Boyd', 'Bobby', 'Biff'],
                     'savings' : [100.0, 1000.0, 10000.0, 100000.0],
                    'damaged' : [1, 1, 1, 1],
                    'damage_value' : [10000.0, 10000.0, 20000.0, 20000.0],
                    'insurance_coverage' : [0.0, 0.0, 5000.0, 10000.0]
                    }
# Create dataframe from dictionary
households_df = pd.DataFrame(households_inputs_dict)

# Re-order dataframe columns
households_df = households_df[['name','savings','insurance_coverage','damaged','damage_value']]

households = {}
for i in households_df.index:
    households[i] = Household(households_df.loc[i])

#Set up all our processes we want to use. We import these from other modules
insurance_claim = _requests.file_insurance_claim(households[i],
                                                 simulation,
                                                 durables.category["claim adjusters"],
                                                 adjuster_time = 5,
                                                 callbacks = None)


def callback():
    yield simulation.process(insurance_claim) 

#This returns a function
my_callback = bundle_callbacks(insurance_claim, request_inspect)

for i in households:
    simulation.process(_requests.request_inspection(households[i], 
                                 simulation, 
                                 durables.category["inspectors"], 
                                 inspection_time = 2,
                                 callbacks = None))
    
    simpy.events.AllOf(simulation, [insurance_claim, request_fema_aid])                                
my_call = simpy.AnyOf(simulation, ())



simulation.run()


for i in households:
    print (households[i].story)


if __name__ == '__main__': 
    #If running as a script vs. importing as module
    #Check version of python
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 2):
        sys.exit("Must have python 3 installed, running version: {0}.{1}"
                 .format(version.major, version.minor))