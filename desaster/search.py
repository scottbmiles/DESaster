# -*- coding: utf-8 -*-
"""
Module of functions that implement complex searches for resources by simulated
entities.

Functions: 
permanent_housing(simulation, entity, search_patience, housing_stock, 
                    human_capital, write_story = False)

rebuild_money(simulation, human_capital, financial_capital, entity, 
                    search_patience, write_story = False):

@author: Scott Miles
"""
from desaster import request

def permanent_housing(simulation, household, search_patience, housing_stock, 
                        human_capital, write_story = False):
    """A process (generator) representing household search for permanent housing
    based on housing preferences, available housing stock, and patience finding 
    a new home.
    
    Keyword Arguments:
    simulation -- Pointer to SimPy simulation environment.
    household -- A single entities.Household() object.
    search_patience -- The search duration in which the household is willing to wait
                        to find a new home. Does not include the process of
                        securing money.
    housing_stock -- A SimPy FilterStore that contains one or more
                    capitals.Residence() objects that represent vacant homes for
                    purchase.
    human_capital -- A capitals.HumanCapital() object.
    write_story -- Boolean indicating whether to track a households story.
    
    Returns or Attribute Changes:
    household.story -- Process outcomes appended to story.
    household.home_search_start -- Record time home search starts
    household.home_search_stop -- Record time home search stops
    household.residence -- Potentially assigned a new capitals.Residence() object.
    household.gave_up_home_search -- Set to True if search patience runs out.
    """
    # Record when housing search starts
    # Calculate the time that housing search patience ends
    # If write_story == True, write search start time to household's story
    household.home_search_start = simulation.now
    patience_end = household.home_search_start + search_patience
    if write_story == True:
        household.story.append(
            "{0} started searching for a {1} with a value under ${2:,.0f} {3:,.0f} days after the event. ".format(
            household.name.title(), household.residence.occupancy,
            household.residence.value, household.home_search_start)
            )
    
    # Define timeout process representing household's *remaining* search patience.
    # Return 'Gave up' if timeout process completes.
    find_search_patience = simulation.timeout(patience_end - simulation.now, 
        value='Gave up')

    # Define a FilterStore get process to find a new home from the vacant 
    # housing stock with similar attributes as current home.
    def find_res(simulation):
        
        new_residence = yield housing_stock.get(lambda getResidence:
                        (
                            getResidence.damage_state == 'None'
                            or getResidence.damage_state == 'Slight'
                        )
                        and getResidence.occupancy == household.residence.occupancy
                        and getResidence.value < household.residence.value
                        and getResidence.inspected == True
                       )
        yield housing_stock.put(household.residence)
        household.residence = new_residence
        household.old_house = (household.residence.latitude, household.residence.longitude)
        household.moved = 1
    find_a_res = simulation.process(find_res(simulation))
    # Yield both the patience timeout and the housing stock FilterStore get.
    # Wait until one or the other process is completed.
    # Assign the process that is completed first to the variable.
    home_search_outcome = yield find_search_patience | find_a_res
    # Exit the function if the patience timeout completes before a suitable 
    # home is found in the housing stock.
    if home_search_outcome == {find_search_patience: 'Gave up'}:
        
        household.gave_up_home_search = True
        
        # If write_story == True, note in the story that the household gave up 
        # the search.
        if write_story == True:
            household.story.append(
                "On day {0:,.0f}, after a {1:,.0f} day search, {2} gave up looking for a new home in the local area. ".format(
                    simulation.now,
                    simulation.now - household.home_search_start, 
                    household.name.title()
                    )
                )
        
        
    
    # If a new home is found before patience runs out place household's current 
    # residence in vacant housing stock -- "sell" the house.
    yield housing_stock.put(household.residence)
    
    # Set the newly found residence as the household's residence.
    #household.residence = home_search_outcome
    
    # Record the time that the housing search ends.
    household.home_search_stop = simulation.now
    
    # If write_story is True, then write results of successful home search to
    # household's story.
    if write_story == True:
        household.story.append(
            "On day {0:,.0f}, {1} received a {2} at {3} with a value of ${4:,.0f} and ${5:,.0f} of damage. ".format(
                household.home_search_stop,
                household.name.title(), household.residence.occupancy, 
                household.residence.address, 
                household.residence.value, 
                household.residence.damage_value
                )
            )

def rebuild_money(simulation, human_capital, financial_capital, entity, 
                    search_patience, write_story = False):
    """A process (generator) representing entity search for money to rebuild or 
    repair home based on requests for insurance and/or FEMA aid and/or loan.
    
    simulation -- Pointer to SimPy simulation environment.
    entity -- A single entities object, such as Household().
    search_patience -- The search duration in which the household is willing to 
                        wait to find a new home. Does not include the process of
                        securing money.
    financial_capital -- A capitals.FinancialCapital() object.
    human_capital -- A capitals.HumanCapital() object.
    write_story -- Boolean indicating whether to track a households story.
    
    Returns or Attribute Changes:
    entity.story -- Process outcomes appended to story.
    entity.money_search_start -- Record time money search starts
    entity.money_search_stop -- Record time money search stops
    entity.gave_up_money_search -- Set to True if search patience runs out.
    entity.money_to_rebuild -- Technically changed (increased) by functions 
                                called within.
    """
    
    # Record when money search starts
    # Calculate the time that money search patience ends
    entity.money_search_start = simulation.now
    patience_end = entity.money_search_start + search_patience
    
    # Return out of function if entity has enough money to rebuild and does not
    # have any insurance coverage.
    if (entity.money_to_rebuild >= entity.residence.damage_value 
        and entity.insurance == 0.0):
        
        # If True, append search outcome to story.
        if write_story == True:
            entity.story.append(
                "{0} already had enough money to rebuild (1:,.0f) and did not seek assistance. ".format(
                                    entity.name.title(),
                                    entity.money_to_rebuild
                                    )
                                )
        
    
    # If entity has insurance then yield an insurance claim request, the duration
    # of which is limited by entity's money search patience.
    if entity.insurance > 0.0:
        
        # Define a timeout process to represent search patience, with duration
        # equal to the *remaining* patience. Pass the value "Gave up" if the
        # process completes.
        find_search_patience = simulation.timeout(
                                                    patience_end - simulation.now,
                                                    value='Gave up'
                                                )
        
        # Define insurance claim request process. Pass data about available
        # insurance claim adjusters.
        try_insurance = simulation.process(
                                            request.insurance_claim(
                                                                    simulation, 
                                                                    human_capital,
                                                                    entity, 
                                                                    write_story
                                                                    )
                                            )
        
        # Yield both the patience timeout and the insurance claim request.
        # Pass result for the process that completes first.
        money_search_outcome = yield find_search_patience | try_insurance
        
        # If patience process completes first, interrupt the insurance claim
        # request and return out of function.
        if money_search_outcome == {find_search_patience: 'Gave up'}:
            entity.gave_up_money_search = True
            try_insurance.interrupt(simulation.now - entity.money_search_start)
            
    
    # If entity (still) does not have enough rebuild money then yield an FEMA aid
    # request, the duration of which is limited by entity's money search patience.
    if entity.money_to_rebuild < entity.residence.damage_value:
        
        # Define a timeout process to represent search patience, with duration
        # equal to the *remaining* patience. Pass the value "Gave up" if the
        # process completes.
        find_search_patience = simulation.timeout(
                                                patience_end - simulation.now, 
                                                value='Gave up'
                                                )
        
        # Define FEMA aid request process. Pass data about available
        # FEMA processors.
        try_fema = simulation.process(
                                        request.fema_assistance(
                                                                simulation,
                                                                human_capital,
                                                                financial_capital, 
                                                                entity, write_story
                                                                )
                                    )
        # Yield both the patience timeout and the FEMA aid request.
        # Pass result for the process that completes first.
        money_search_outcome = yield find_search_patience | try_fema
        
        # If patience process completes first, interrupt the FEMA aid
        # request and return out of function.
        if money_search_outcome == {find_search_patience: 'Gave up'}:
            entity.gave_up_money_search = True
            try_fema.interrupt(simulation.now - entity.money_search_start)
             
    
    # If entity (still) does not have enough rebuild money then yield a loan 
    # request, the duration of which is limited by entity's money search patience.
    if entity.money_to_rebuild < entity.residence.damage_value:
        
        # Define a timeout process to represent search patience, with duration
        # equal to the *remaining* patience. Pass the value "Gave up" if the
        # process completes.
        find_search_patience = simulation.timeout(patience_end - simulation.now, 
                                value='Gave up')
        
        # Define loan request process. Pass data about available
        # loan processors.
        try_loan = simulation.process(
                                        request.loan(
                                                    simulation, 
                                                    human_capital, 
                                                    entity, 
                                                    write_story
                                                    )
                                    )
        
        # Yield both the patience timeout and the loan request.
        # Pass result for the process that completes first.
        money_search_outcome = yield find_search_patience | try_loan
        
        # If patience process completes first, interrupt the loan
        # request and return out of function.
        if money_search_outcome == {find_search_patience: 'Gave up'}:
            entity.gave_up_money_search = True
            try_loan.interrupt(simulation.now - entity.money_search_start)
            print("Loan Interrupted.")
            
    
    # Record the time and duration when entity's search for money ends without 
    # giving up.
    entity.money_search_stop = simulation.now
    search_duration = entity.money_search_stop - entity.money_search_start
    
    # If write_story is True, then append money search outcome to entity's story.
    if write_story == True:
        entity.story.append(
            "It took {0} {1:.0f} days to receive enough financial assistance and now has ${2:,.0f} to rebuild. ".format(
                    entity.name.title(),
                    search_duration,
                    entity.money_to_rebuild
                    )
            )