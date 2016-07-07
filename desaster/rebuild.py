# -*- coding: utf-8 -*-
"""
Created on July 2016

@author: Scott

processes related to rebuilding
"""
from desaster.config import building_repair_times
from desaster import request
from simpy import Interrupt

def home(simulation, human_capital, entity, write_story = True, callbacks = None): 
    try: # in case a process interrupt is thrown in a master process
        
        # Need to get an engineering assessment before filing for a building permit
        yield simulation.process(request.engineering_assessment(simulation, human_capital, entity, write_story))
        
        # With an engineering assessment can request a permit
        yield simulation.process(request.permit(simulation, human_capital, entity, write_story))
        
        # With a permit and enough money, can rebuild
        if entity.permit_get > 0.0 and entity.money_to_rebuild >= entity.residence.damage_value:
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

            # Record time when household gets house
            entity.house_get = simulation.now
            
            if write_story == True:
                # Write the household's story
                entity.story.append(
                    'The house was rebuilt {0} days after the event, taking {1} days to rebuild. '.format(
                    entity.house_get, entity.house_get - entity.house_put))
        
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
                    '{0} gave up {1} days into the home rebuilding process. '.format(
                    entity.name, i.cause))
    
    if callbacks is not None:
        yield simulation.process(callbacks)

    else:
        pass