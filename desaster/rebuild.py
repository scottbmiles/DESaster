# -*- coding: utf-8 -*-
"""
Module of functions for rebuilding/repairing individual homes and entire
building stocks. Eventually functions for non-residential buildings can be added.

Functions:
home(simulation, human_capital, financial_capital, household, write_story = True,
callbacks = None)
stock(simulation, structure_stock, fix_probability, human_capital)

@author: Scott Miles
"""
from desaster.config import building_repair_times, materials_cost_pct
from simpy import Interrupt
import random

def home(simulation, human_capital, financial_capital, household, write_story = True, callbacks = None):
    """A process to rebuild a household's residence based on available contractors and
    building materials.
    
    Keyword Arguments:
    household -- A single entities.Household() object.
    human_capital -- A capitals.HumanCapital() object.
    financial_capital -- A capitals.FinancialCapital() object.
    write_story -- Boolean indicating whether to track a households story.
    
    Returns or Attribute Changes:
    household.story -- Process outcomes appended to story.
    household.home_put -- Record time money search starts
    household.home_get -- Record time money search stops
    household.residence.damage_state -- Set to 'None' if successful.
    household.residence.damage_value = Set to $0.0 if successful.
    """
    # Use exception handling in case process is interrupted by another process.
    try: 

        # If household has enough money & there is enough available construction 
        # materials in the region, then rebuild.
        if (household.money_to_rebuild >= household.residence.damage_value and
        household.residence.damage_value <= financial_capital.building_materials.level):
            # Record time put in request for home rebuild.
            household.home_put = simulation.now
            
            # Put in request for contractors to repair home.
            contractors_request = human_capital.contractors.request()
            yield contractors_request

            # Get the rebuild time for the household from config.py
            # which imports the HAZUS repair time look up table.
            # Rebuild time is based on occupancy type and damage state.
            rebuild_time = building_repair_times.ix[household.residence.occupancy][household.residence.damage_state]

            # Obtain necessary construction materials from regional inventory.
            # materials_cost_pct is % of damage value related to building materials 
            # (vs. labor and profit)
            yield financial_capital.building_materials.get(household.residence.damage_value * materials_cost_pct)

            # Yield timeout equivalent to rebuild time.
            yield simulation.timeout(rebuild_time)

            # Release contractors.
            human_capital.contractors.release(contractors_request)

            # After successful rebuild, set damage to None & $0.
            household.residence.damage_state = 'None'
            household.residence.damage_value = 0.0

            # Record time when household gets home.
            household.home_get = simulation.now

            # If True, write outcome of successful rebuild to story.
            if write_story == True:
                household.story.append(
                    '{0}\'s home was repaired {1:,.0f} days after the event, taking {2:.0f} days to repair. '.format(
                        household.name,
                        household.home_get,
                        household.home_get - household.home_put
                    )
                )
        
        # Deal with case that insufficient construction materials are available.
        if household.residence.damage_value > financial_capital.building_materials.level:
            # If true, write outcome of the process to their story
            if write_story == True:
                household.story.append(
                'There were insufficient construction materials available in the area for {0} to rebuild. '
                .format(household.name)
                )
            
            return
        
        # Deal with case that household does not have enough money to rebuild.
        if household.money_to_rebuild < household.residence.damage_value:
            # If true, write outcome of the process to their story
            if write_story == True:
                household.story.append(
                    '{0} was unable to get enough money to rebuild. '.format(
                    household.name))
            
            return
    
    # Handle any interrupt thrown by another process
    except Interrupt as i: 
        # If true, write outcome of the process to their story
        if write_story == True:
            household.story.append(
                    '{0} gave up {1:.0f} days into the home rebuilding process. '.format(
                    household.name, i.cause))

    if callbacks is not None:
        yield simulation.process(callbacks)

    else:
        pass

def stock(simulation, structure_stock, fix_probability):
    """Process to rebuild a part or an entire building stock (FilterStore) based
    on available contractors and specified proportion/probability.
    
    Keyword Arguments:
    structure_stock -- A SimPy FilterStore that contains one or more
        capitals.BuiltCapital(), capitals.Building(), or capitals.Residence() 
        objects that represent vacant structures for purchase.
    fix_probability -- A value to set approximate percentage of number of structures
        in the stock to rebuild.
        
    Attribute Changes:
    put_structure.damage_state -- Changed to 'None' for selected structures.
    put_structure.damage_value = Changed to $0.0 for selected structures.
    """
    random.seed(15)

    structures_list = []  # Empty list to temporarily place FilterStore objects.

    # Remove all structures from the FilterStore; put in a list for processing.
    while len(structure_stock.items) > 0:
        get_structure = yield structure_stock.get(lambda getStructure:
                                                        getStructure.value >= 0.0
                                                )
        structures_list.append(get_structure)

    num_fixed = 0  # Counter
    # Iterate through structures, do processing, put back into the FilterStore
    for put_structure in structures_list:
        # Select inspected structures that have Moderate or Complete damage
        if (put_structure.inspected == True 
        and (put_structure.damage_state == 'Moderate' 
        or put_structure.damage_state == 'Complete')
        ):
            # Compare uniform random to prob to estimate percentage to fix.
            # Then set damage to None and $0. Put back in FilterStore.
            if random.uniform(0, 1.0) <= fix_probability:
                put_structure.damage_state = 'None'
                put_structure.damage_value = 0.0
                structure_stock.put(put_structure)

                num_fixed += 1
            else:
                # Put back in FilterStore if chosen not to be fixed.
                structure_stock.put(put_structure)

        else:
            # Put all other structures back in FilterStore.
            structure_stock.put(put_structure)

    print('{0} homes in the vacant building stock were fixed on day {1:,.0f}.'.format(num_fixed, simulation.now))
    
