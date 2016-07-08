# -*- coding: utf-8 -*-
"""
Created on July 2016

@author: Scott
"""
from simpy import Interrupt
from desaster import request

def permanent_housing(simulation, entity, search_patience, housing_stock, human_capital, write_story = False):
    
    entity.home_search_start = simulation.now
    patience_end = entity.home_search_start + search_patience
    
    if write_story == True:
        entity.story.append(
                                '{0} started searching for a {1} with a value under ${2:,.0f} {3:,.0f} days after the event. '.format(
                                entity.name, entity.residence.occupancy, 
                                entity.residence.value, entity.home_search_start)
                                )
    
    find_search_patience = simulation.timeout(patience_end - simulation.now, value='Gave up')
    
    # Find a new home from the vacant housing stock with similar attributes as current home
    new_residence = housing_stock.get(lambda getResidence:
                                        (getResidence.damage_state == 'None' or 
                                        getResidence.damage_state == 'Slight')  and
                                        getResidence.occupancy == entity.residence.occupancy and 
                                        getResidence.value < entity.residence.value and
                                        getResidence.inspected == True
                                       )
    
    # Yield both the patience timeout and the new residence FilterStore search
    home_search_outcome = yield find_search_patience | new_residence
    
    # If the patience timeout occurs before a suitable home is available
    if home_search_outcome == {find_search_patience: 'Gave up'}:
        
        if write_story == True:
            entity.story.append(
                                    'On day {0:,.0f}, after a {1:,.0f} day search, {2} gave up looking for a new home in the local area. '.format(
                                    simulation.now, simulation.now - entity.home_search_start, entity.name)
                                    )
        return 'Gave up'
    
    # If a new home is found before patience runs out...
    # Place current residence in vacant housing stock -- household left the house                            
    yield housing_stock.put(entity.residence)
    
    # Set the newly found residence as the household's residence
    entity.residence = home_search_outcome[new_residence]
    
    entity.home_search_stop = simulation.now
    
    if write_story == True:
        entity.story.append(
                                'On day {0:,.0f}, {1} received a {2} at {3} with a value of ${4:,.0f} and ${5:,.0f} of damage. '.format(
                                entity.home_search_stop, entity.name, entity.residence.occupancy, 
                                entity.residence.address, entity.residence.value, entity.residence.damage_value)
                                )

def rebuild_money(simulation, human_capital, financial_capital, entity, search_patience, write_story):
    entity.money_search_start = simulation.now
    patience_end = entity.money_search_start + search_patience
    
    if entity.money_to_rebuild >= entity.residence.damage_value and entity.insurance == 0.0:
        
        if write_story == True:    
            entity.story.append(
                                    '{0} already had enough money to rebuild (1:,.0f) and did not seek assistance. '.format(
                                    entity.name, entity.money_to_rebuild))

    if entity.insurance > 0.0:
        
        find_search_patience = simulation.timeout(patience_end - simulation.now, value='Gave up')
        try_insurance = simulation.process(request.insurance_claim(simulation, human_capital, entity, write_story))
        
        money_search_outcome = yield find_search_patience | try_insurance
        
        if money_search_outcome == {find_search_patience: 'Gave up'}:
            
            try_insurance.interrupt(simulation.now - entity.money_search_start)

            return
    
    if entity.money_to_rebuild < entity.residence.damage_value:
        
        find_search_patience = simulation.timeout(patience_end - simulation.now, value='Gave up')
        try_fema = simulation.process(request.fema_assistance(simulation, human_capital, 
                                                              financial_capital, entity, write_story))
        
        money_search_outcome = yield find_search_patience | try_fema
        
        if money_search_outcome == {find_search_patience: 'Gave up'}:
            try_fema.interrupt(simulation.now - entity.money_search_start)

            return
        
    if entity.money_to_rebuild < entity.residence.damage_value:
        
        find_search_patience = simulation.timeout(patience_end - simulation.now, value='Gave up')
        try_loan = simulation.process(request.loan(simulation, human_capital, entity, write_story))
        
        money_search_outcome = yield find_search_patience | try_loan
        
        if money_search_outcome == {find_search_patience: 'Gave up'}:
            try_loan.interrupt(simulation.now - entity.money_search_start)

            return
    
    entity.money_search_stop = simulation.now
    search_duration = entity.money_search_stop - entity.money_search_start
    
    if write_story == True:    
        entity.story.append(
                                'It took {0} {1:.0f} days to receive enough financial assistance and now has ${2:,.0f} to rebuild. '.format(
                                entity.name, search_duration, entity.money_to_rebuild))

