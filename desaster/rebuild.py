# -*- coding: utf-8 -*-
"""
Created on July 2016

@author: Scott

processes related to rebuilding
"""
from desaster.config import building_repair_times
from desaster import request
from simpy import Interrupt
import random

def home(simulation, human_capital, entity, write_story = True, callbacks = None): 
    try: # in case a process interrupt is thrown in a master process
        

        # With enough money, can rebuild
        if entity.money_to_rebuild >= entity.residence.damage_value:
            # Put in request for contractors to repair house
            entity.house_put = simulation.now

            contractors_request = human_capital.contractors.request()
            yield contractors_request
            
            # Get the rebuild time for the entity from config.py 
            # which imports the HAZUS repair time look up table.
            # Rebuild time is based on occupancy type and damage state.
            rebuild_time = building_repair_times.ix[entity.residence.occupancy][entity.residence.damage_state]
            
            yield simulation.timeout(rebuild_time)
        
            human_capital.contractors.release(contractors_request)
            
            entity.residence.damage_state = 'None'
            entity.residence.damage_value = 0.0

            # Record time when household gets house
            entity.house_get = simulation.now
            
            if write_story == True:
                # Write the household's story
                entity.story.append(
                    '{0}\'s home was repaired {1:,.0f} days after the event, taking {2:.0f} days to repair. '.format(
                    entity.name, entity.house_get, entity.house_get - entity.house_put))
        
        elif entity.money_to_rebuild < entity.residence.damage_value:
            if story == True:
                entity.story.append(
                    '{0} was unable to get enough money to rebuild. '.format(
                    entity.name))
        else: 
            if write_story == True:
                entity.story.append(
                    '{0} was unable to get a permit to rebuild. '.format(
                    entity.name))

    except Interrupt as i: # Handle any interrupt thrown by a master process
        if write_story == True:
            #If true, write their story
            entity.story.append(
                    '{0} gave up {1:.0f} days into the home rebuilding process. '.format(
                    entity.name, i.cause))
    
    if callbacks is not None:
        yield simulation.process(callbacks)

    else:
        pass
        
def stock(simulation, structure_stock, fix_probability, human_capital):
    random.seed(15)

    
    structures_list = []
    
    # Remove all structures from the FilterStore and put them in a list to do processing on them
    while len(structure_stock.items) > 0:
        
        get_structure = yield structure_stock.get(lambda getStructure: 
                                                        getStructure.value >= 0.0
                                                )                                  
        
        structures_list.append(get_structure)                                  
    
    num_fixed = 0
    
    # Iterate through list of structures, do processing, put them back into the FilterStore
    for put_structure in structures_list:
        
        if put_structure.inspected == True and \
        (put_structure.damage_state == 'Moderate' or put_structure.damage_state == 'Complete'):
            
            if random.uniform(0, 1.0) <= fix_probability:
                
                put_structure.damage_state = 'None'
                put_structure.damage_value = 0.0

                structure_stock.put(put_structure)
                
                num_fixed += 1
            
            else:
                structure_stock.put(put_structure)
                
        else:
            structure_stock.put(put_structure)
        
    print('{0} homes in the vacant building stock were fixed on day {1:,.0f}.'.format(num_fixed, simulation.now))