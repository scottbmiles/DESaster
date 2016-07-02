# -*- coding: utf-8 -*-
"""
Created on Mon Jan 25 16:09:02 2016

@author: Derek

processes related to rebuilding
"""
from desaster.config import sfr_rebuild_time
from simpy import Interrupt

def rebuild_house(simulation, human_capital, entity, story = True): 
        
        if entity.permit_get > 0.0 and entity.money_to_rebuild >= entity.residence.damage_value:
            # Put in request for contractors to repair house
            entity.house_put = simulation.now

            request = human_capital.contractors.request()
            yield request
            
            # Time required to rebuild house
            if entity.residence.occupancy == 'Single Family':
                yield simulation.timeout(sfr_rebuild_time)
            if entity.residence.occupancy == 'Multi Family':
                yield simulation.timeout(mfr_rebuild_time)
            if entity.residence.occupancy == 'Mobile':
                yield simulation.timeout(mobile_rebuild_time)

            human_capital.contractors.release(request)


            # Record time when household gets house
            entity.house_get = simulation.now
            
            if story == True:
                # Write the household's story
                entity.story.append(
                    'The house was rebuilt {0} days after the event, taking {1} days to rebuild. '.format(
                    entity.house_get, sfr_rebuild_time))
        
        elif entity.money_to_rebuild < entity.residence.damage_value:
            if story == True:
                entity.story.append(
                    '{0} was unable to get enough money to rebuild. '.format(
                    entity.name))
        else: 
            if story == True:
                entity.story.append(
                    '{0} was unable to get a permit to rebuild. '.format(
                    entity.name))
