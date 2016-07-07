# -*- coding: utf-8 -*-
"""
Created on Wed Jan 20 14:14:36 2016

@author: Scott
"""
from simpy import Interrupt
from desaster import request

def permanent_housing(simulation, entity, housing_stock, write_story = True):
    
    entity.home_search_start = simulation.now
    
    if write_story == True:
        entity.story.append(
                                '{0} started searching for a {1} with a value under ${2} on day {3}. '.format(
                                entity.name, entity.residence.occupancy, 
                                entity.residence.value, entity.home_search_start)
                                )
    # Find a new home from the vacant housing stock with similar attributes as current home
    new_residence = yield housing_stock.get(lambda getResidence:
                                        (getResidence.damage_state == 'None' or 
                                        getResidence.damage_state == 'Slight')  and
                                        getResidence.occupancy == entity.residence.occupancy and 
                                        getResidence.value <= entity.residence.value
                                       )
    # Place current residence in vacant housing stock -- household left the house                            
    yield housing_stock.put(entity.residence)
    
    # Set the newly found residence as the household's residence
    entity.residence = new_residence
    
    entity.home_search_stop = simulation.now
    
    if write_story == True:
        entity.story.append(
                                'On day {0}, {1} found a {2} at {3} with a value of ${4}. '.format(
                                entity.home_search_stop, entity.name, entity.residence.occupancy, 
                                entity.residence.address, entity.residence.value)
                                )

def rebuild_money(simulation, human_capital, financial_capital, entity, money_patience, write_story):
    # try:

        entity.money_search_start = simulation.now
        patience_end = entity.money_search_start + money_patience
        
        if entity.insurance > 0.0:
            
            find_money_patience = simulation.timeout(patience_end - simulation.now, value='Gave up')
            try_insurance = simulation.process(request.insurance_claim(simulation, human_capital, entity, write_story))
            
            money_search_outcome = yield find_money_patience | try_insurance
            
            if money_search_outcome == {find_money_patience: 'Gave up'}:
                
                try_insurance.interrupt(simulation.now - entity.money_search_start)


                return
        
        if entity.money_to_rebuild < entity.residence.damage_value:
            
            find_money_patience = simulation.timeout(patience_end - simulation.now, value='Gave up')
            try_fema = simulation.process(request.fema_assistance(simulation, human_capital, 
                                                                  financial_capital, entity, write_story))
            
            money_search_outcome = yield find_money_patience | try_fema
            
            if money_search_outcome == {find_money_patience: 'Gave up'}:
                try_fema.interrupt(simulation.now - entity.money_search_start)

                return
            
        if entity.money_to_rebuild < entity.residence.damage_value:
            
            find_money_patience = simulation.timeout(patience_end - simulation.now, value='Gave up')
            try_loan = simulation.process(request.loan(simulation, human_capital, entity, write_story))
            
            money_search_outcome = yield find_money_patience | try_loan
            
            if money_search_outcome == {find_money_patience: 'Gave up'}:
                try_loan.interrupt(simulation.now - entity.money_search_start)

                return
        
        entity.money_search_stop = simulation.now
        
        if write_story == True:    
            entity.story.append(
                                    'It took {0} {1} days to exhaust the search for money. '.format(
                                    entity.name, entity.money_search_stop - entity.money_search_start))
    
    # except:
    #     
    #     if write_story == True:
    #         entity.story.append(
    #                             '{0} gave up searching for money after {1} days. '.format(
    #                                 entity.name, simulation.now - start_money_search))
    # 
    #     return