# -*- coding: utf-8 -*-
"""


@author: Derek Huling, Scott Miles
"""
from desaster.programs import RecoveryProgram
from desaster.config import building_repair_times, materials_cost_pct
import random

class InspectionProgram(RecoveryProgram):
    def __init__(self, simulation, duration, staff=float('inf')):
        RecoveryProgram.__init__(self, simulation, duration, staff)      

    def process(self, structure, entity = None, write_story = False, callbacks = None):
        
        # Only record inspection request time if structure associated with an entity.
        if entity != None:
            # Put in request for an inspector (shared resource)
            entity.inspection_put = self.simulation.now
        
        # Request inspectors
        staff_request = self.staff.request()
        yield staff_request

        # Yield timeout equivalent to time from hazard event to end of inspection.
        yield self.simulation.timeout(self.duration())
        
        # Set attribute of structure to indicate its been inspected.
        structure.inspected = True
        
        # Release inspectors now that inspection is complete.
        self.staff.release(staff_request) 
        
        # Only record inspection time and write story if structure associated with 
        # an entity.
        if entity != None:
            entity.inspection_get = self.simulation.now
            
            #If true, write process outcome to story
            if write_story == True:
                
                entity.story.append(
                                "{0}'s {1} was inspected {2:.0f} days after the event and suffered ${3:,.0f} of damage.".format(
                                entity.name.title(), structure.occupancy.lower(),
                                entity.inspection_get, structure.damage_value))

class EngineeringAssessment(RecoveryProgram):
    def __init__(self, simulation, duration, staff=float('inf')):
        RecoveryProgram.__init__(self, simulation, duration, staff)      

    def process(self, structure, entity, write_story = False, callbacks = None):
        """Define process for entity to request an engineering assessment of their
        structure.
        
        Keyword Arguments:
        entity -- An entity object from the entity.py module, for example
                    entities.Household().
        simulation -- A simpy.Environment() object.
        program -- A capitals.HumanCapital() object.
        write_story -- Boolean indicating whether to track a entitys story.
        callbacks -- a generator function containing processes to start after the 
                        completion of this process.

        Returns or Attribute Changes:
        entity.assessment_put -- Records sim time of assessment request
        entity.assistance_get -- Records sim time of assessment reciept
        """
        
        # Record time that assessment request put in.
        entity.assessment_put = self.simulation.now
        
        # Request an engineer.
        staff_request = self.staff.request()
        yield staff_request

        # Yield process timeout for duration necessary to assess entity's structure.
        yield self.simulation.timeout(self.duration())
        
        # Release engineer so it can assess other structures.
        self.staff.release(staff_request)
        
        structure.assessment = True
        
        # Record time when assessment complete.
        entity.assessment_get = self.simulation.now
        
        # If true, write the outcome of the process to story.
        if write_story == True:
            entity.story.append(
            '{0} received an engineering assessment {1:.0f} days after the event. '
            .format(entity.name.title(), entity.assessment_get)
            )

        if callbacks is not None:
            yield simulation.process(callbacks)
        else:
            pass

class PermitProgram(RecoveryProgram):
    def __init__(self, simulation, duration, staff=float('inf')):
        RecoveryProgram.__init__(self, simulation, duration, staff)      

    def process(self, structure, entity, write_story = False, callbacks = None):
        """Define process for entity to request an engineering assessment of their
        structure.

        Keyword Arguments:
        entity -- An entity object from the entity.py module, for example
                    entities.Household().
        simulation -- A simpy.Environment() object.
        program -- A capitals.HumanCapital() object.
        write_story -- Boolean indicating whether to track a entitys story.
        callbacks -- a generator function containing processes to start after the 
                        completion of this process.

        Returns or Attribute Changes:
        entity.permit_put -- Records sim time of permit request
        entity.permit_get -- Records sim time of permit reciept
        """
        
        # Record time permit application submitted.
        entity.permit_put = self.simulation.now

        # Request permit processor / building official.
        staff_request = self.staff.request()
        yield staff_request
        
        # Yield process timeout equal to duration required to review permit request.
        yield self.simulation.timeout(self.duration())

        # Release permit process to allow them to review other requests.
        self.staff.release(staff_request)

        structure.permit = True
    
        # Record time that permit is granted.
        entity.permit_get = self.simulation.now
            
        #If true, write outcome of process to story.
        if write_story == True:
            entity.story.append(
            "{0} received permit approval {1:.0f} days after the event. "
            .format(entity.name.title(), entity.permit_get)
            )

        if callbacks is not None:
            yield self.simulation.process(callbacks)
        else:
            pass

class RebuildProgram(RecoveryProgram):
    def __init__(self, simulation, duration, staff=float('inf'), budget=float('inf')):
        RecoveryProgram.__init__(self, simulation, duration, staff, budget)      

    def process(self, structure, entity, write_story = False, callbacks = None):
        """A process to rebuild a building structure based on available contractors and
        building materials.
        
        Keyword Arguments:
        entity -- A single entities.Household() object.
        human_capital -- A capitals.HumanCapital() object.
        financial_capital -- A capitals.FinancialCapital() object.
        write_story -- Boolean indicating whether to track a entitys story.
        
        Returns or Attribute Changes:
        entity.story -- Process outcomes appended to story.
        entity.rebuild_put -- Record time money search starts
        entity.rebuild_get -- Record time money search stops
        structure.damage_state -- Set to 'None' if successful.
        structure.damage_value = Set to $0.0 if successful.
        """
        # Use exception handling in case process is interrupted by another process.
        try: 
            
            materials_cost = structure.damage_value * materials_cost_pct
            # Deal with case that insufficient construction materials are available.
            if materials_cost > self.budget.level:
                
                # If true, write outcome of the process to their story
                if write_story == True:
                    entity.story.append(
                    'There were insufficient construction materials available in the area for {0} to rebuild. '
                    .format(entity.name.title())
                    )
                
                return
            
            # Deal with case that entity does not have enough money to rebuild.
            if entity.money_to_rebuild < structure.damage_value:
                # If true, write outcome of the process to their story
                if write_story == True:
                    entity.story.append(
                        '{0} was unable to get enough money to rebuild or rebuild. '.format(
                        entity.name.title()))
                
                return
            
            # If entity has enough money & there is enough available construction 
            # materials in the region, then rebuild.
            if (entity.money_to_rebuild >= structure.damage_value and
            materials_cost <= self.budget.level):
                
            
                # Record time put in request for home rebuild.
                entity.rebuild_put = self.simulation.now
                
                # Put in request for contractors to rebuild home.
                staff_request = self.staff.request()
                yield staff_request

                # Get the rebuild time for the entity from config.py
                # which imports the HAZUS rebuild time look up table.
                # Rebuild time is based on occupancy type and damage state.
                rebuild_time = building_repair_times.ix[structure.occupancy][structure.damage_state]

                # Obtain necessary construction materials from regional inventory.
                # materials_cost_pct is % of damage value related to building materials 
                # (vs. labor and profit)
                
                
                
                yield self.budget.get(materials_cost)

                # Yield timeout equivalent to rebuild time.
                yield self.simulation.timeout(rebuild_time)

                # Release contractors.
                self.staff.release(staff_request)

                # After successful rebuild, set damage to None & $0.
                structure.damage_state = 'None'

                # Record time when entity gets home.
                entity.rebuild_get = self.simulation.now

                # If True, write outcome of successful rebuild to story.
                if write_story == True:
                    entity.story.append(
                        '{0}\'s {1} was rebuilded {2:,.0f} days after the event, taking {3:.0f} days to rebuild. '.format(
                            entity.name.title(), structure.occupancy.lower(),
                            entity.rebuild_get,
                            entity.rebuild_get - entity.rebuild_put
                        )
                    )
            
        # Handle any interrupt thrown by another process
        except Interrupt as i: 
            # If true, write outcome of the process to their story
            if write_story == True:
                entity.story.append(
                        '{0} gave up {1:.0f} days into the rebuild process. '.format(
                        entity.name.title(), i.cause))

        if callbacks is not None:
            yield simulation.process(callbacks)

        else:
            pass

class RebuildStockProgram(RecoveryProgram):
    def __init__(self, simulation, duration, staff=float('inf')):
        RecoveryProgram.__init__(self, simulation, duration, staff)      

    def process(structure_stock, fix_probability):
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
        while structure_stock.items:
            get_structure = yield structure_stock.get(lambda getStructure:
                                                            getStructure.value >= 0.0
                                                    )
            structures_list.append(get_structure)

        num_fixed = 0  # Counter
        # Iterate through structures, do processing, put back into the FilterStore
        for put_structure in structures_list:
            # Select inspected structures that have Moderate or Complete damage
            if (put_structure.inspected == True 
            and (put_structure.damage_state == 'Extensive' 
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

        print('{0} homes in the vacant building stock were fixed on day {1:,.0f}.'.format(num_fixed, self.simulation.now))

