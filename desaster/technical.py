# -*- coding: utf-8 -*-
"""
Module of classes for implementing DESaster technical recovery programs.

Classes:
InspectionProgram
PermitProgram
EngineeringAssessment
RepairProgram
RepairStockProgram

@author: Scott Miles (milessb@uw.edu), Derek Huling
"""
from desaster.config import building_repair_times, materials_cost_pct
import random
from numpy.random import choice
from simpy import Interrupt
from simpy import Resource, Container
from desaster.io import random_duration_function

class TechnicalRecoveryProgram(object):
    """The base class for operationalizing technical recovery programs. 
    All such programs staff implemented as simpy resources . 
    
    All other classes of technical recovery programs should inherit from this class, 
    either directly or indirectly. The process for TechnicalRecoveryProgram is 
    useless and should only be used as an example of how to implement a process in a
    subclass of TechnicalRecoveryProgram.
    
    Methods:
    __init__(self, env, duration_prob_dist, staff=float('inf'))
    process(self, entity = None)
    """
    def __init__(self, env, duration_prob_dist, staff=float('inf')):
        """Initiate a TechnicalRecoveryProgram object.
        
        Keyword Arguments:
        env -- simpy.Envionment() object
        duration_prob_dist -- io.DurationProbabilityDistribution() object
        staff -- Integer, indicating number of staff assigned to the programs
                    
        Attribute Changes:
        self.staff -- A simpy.Resource() object with a capacity == staff arg
        self.duration -- A function that is used to calculate random durations 
                            for the program process
        """
        self.env = env
        self.staff = Resource(self.env, capacity=staff)
        self.duration = random_duration_function(duration_prob_dist)
        
    def process(self, entity = None):
        """The process for TechnicalRecoveryProgram for requesting staff and issuing
        SimPy timeouts to represent duration of associated technical process.
        
        entity -- Some entities.py object that initiates and benefits from the recovery program.
        """
        ###
        ### The contents of this function are an example of what can be done
        ### in a subclass of this class. It demonstrates the use of SimPy 
        ### Resources and Containiners. The function itself is useless.
        ### It is meant to help create your own function after creating
        ### a subclass that inherits from this class.
        ### 
        
        # Request staff
        staff_request = self.staff.request()
        yield staff_request

        # Yield timeout equivalent to program's process duration
        yield self.env.timeout(self.duration())

        # Release release staff after process duation is complete.
        self.staff.release(staff_request)

        material_cost = 1 # Cost of materials needed (e.g., for RepairProgram)

        # Get out amount equal to cost.
        yield self.materials.get(material_cost) # *** Materials not used in all TechnicalRecoveryProgram subclasses

        # Put back amount equal to cost.
        yield self.materials.put(material_cost)

        #If true, write process outcome to story
        if entity.write_story and entity != None:
            entity.story.append("{0} process completed for {1} after {2} days, leaving ${3:,.0f} of materials. ".format(
                                self.__class__, entity.name.title(), self.env.now, self.materials.level
                                                                                        )
                                )

class InspectionProgram(TechnicalRecoveryProgram):
    """ A class for representing staff allocation and process duration associated 
    with post-event building inspections or tagging. No actual damage
    assessment (valuation) is done by the class process. It is done in the 
    instantiation of the building object (e.g., entities.SingleFamilyResidential.damage_value)
    based on inputted damage_state and HAZUS lookup tables.
    
    Methods:
    __init__(self, env, duration_prob_dist, staff=float('inf'))
    process(self, structure, entity = None, callbacks = None)
    """
    def __init__(self, env, duration_prob_dist, staff=float('inf')):
        """Initiate an InspectionProgram object.
        
        Keyword Arguments:
        env -- simpy.Envionment() object
        duration_prob_dist -- io.DurationProbabilityDistribution() object
        staff -- Integer, indicating number of staff assigned to the program
        
        Inheritance:
        Subclass of technical.TechnicalRecoveryProgram()
        """
        TechnicalRecoveryProgram.__init__(self, env, duration_prob_dist, staff)

    def process(self, structure, entity = None, callbacks = None):
        """Process to allocate staff and simulate duration associated 
        with post-event building inspections. 
        
        Keyword Arguments:
        structure -- Some structures.py object, such as structures.SingleFamilyResidential()
        entity -- An entity (e.g., entities.OwnerHousehold()) that initiates 
                    and benefits from the process.
        callbacks -- a generator function containing processes to start after the
                    completion of this process.
                    
        Changed Attributes:
        entity.story -- Append story strings to entity's story
        entity.inspection_put -- Time request for inspection was put in
        entity.inspection_get -- Time structure was inspected
        structure.inspected = True, if successfully inspected
        """
        # Only record inspection request time if structure associated with an entity.
        if entity != None:
            # Put in request for an inspector (shared resource)
            entity.inspection_put = self.env.now

        # Request inspectors
        staff_request = self.staff.request()
        yield staff_request

        # Yield timeout equivalent to time from hazard event to end of inspection.
        yield self.env.timeout(self.duration())

        # Set attribute of structure to indicate its been inspected.
        structure.inspected = True

        # Release inspectors now that inspection is complete.
        self.staff.release(staff_request)

        # Only record inspection time and write story if structure associated with
        # an entity.
        if entity != None:
            entity.inspection_get = self.env.now

            #If true, write process outcome to story
            if entity.write_story:

                entity.story.append(
                                "{0}'s {1} was inspected {2:.0f} days after the event and suffered ${3:,.0f} of damage.".format(
                                entity.name.title(), structure.occupancy.lower(),
                                entity.inspection_get, structure.damage_value))

class EngineeringAssessment(TechnicalRecoveryProgram):
    """A class to represent staff allocation and process duration associated with 
    building engineering assessments. Conceptually this intended as a detailed
    damage assessment prior to design, permitting, and repair/construction of
    a building. No actual damage valuation is done by the class process, though
    it would conceputally make sense. It is done in the instantiation of the 
    building object (e.g., entities.SingleFamilyResidential.damage_value)
    based on inputted damage_state and HAZUS lookup tables.
    
    Methods:
    __init__(self, env, duration_prob_dist, staff=float('inf'))
    process(self, structure, entity = None, callbacks = None)
    """
    def __init__(self, env, duration_prob_dist, staff=float('inf'), ):
        """Initiate EngineeringAssessment object.
        
        Keyword Arguments:
        env -- simpy.Envionment() object
        duration_prob_dist -- io.DurationProbabilityDistribution() object
        staff -- Integer, indicating number of staff assigned to the program
        
        Inheritance:
        Subclass of technical.TechnicalRecoveryProgram()
        """
        TechnicalRecoveryProgram.__init__(self, env, duration_prob_dist, staff)

    def process(self, structure, entity, callbacks = None):
        """Define process for entity to request an engineering assessment of their
        building.

        
        Keyword Arguments:
        structure -- Some structures.py object, such as structures.SingleFamilyResidential()
        entity -- An entity (e.g., entities.OwnerHousehold()) that initiates 
                    and benefits from the process.
        callbacks -- a generator function containing processes to start after the
                    completion of this process.
        
        Returns or Attribute Changes:
        entity.story -- Append story strings to entity's story
        entity.assessment_put -- Records sim time of assessment request
        entity.assistance_get -- Records sim time of assessment reciept
        structure.inspected = True, if successfully assessed
        """
        # Record time that assessment request put in.
        entity.assessment_put = self.env.now

        # Request an engineer.
        staff_request = self.staff.request()
        yield staff_request

        # Yield process timeout for duration necessary to assess entity's structure.
        yield self.env.timeout(self.duration())

        # Release engineer so it can assess other structures.
        self.staff.release(staff_request)

        structure.assessment = True

        # Record time when assessment complete.
        entity.assessment_get = self.env.now

        # If true, write the outcome of the process to story.
        if entity.write_story:
            entity.story.append(
            '{0} received an engineering assessment {1:.0f} days after the event. '
            .format(entity.name.title(), entity.assessment_get)
            )

        if callbacks is not None:
            yield env.process(callbacks)
        else:
            pass

class PermitProgram(TechnicalRecoveryProgram):
    """A class to represent staff allocation and process duration associated with 
    building permit processing. Conceptually this intended prior to building
    repairs or construction.
    
    Methods:
    __init__(self, env, duration_prob_dist, staff=float('inf'))
    process(self, structure, entity = None, callbacks = None)
    """
    def __init__(self, env, duration_prob_dist, staff=float('inf'), ):
        """Initiate PermitProgram object.
        
        Keyword Arguments:
        env -- simpy.Envionment() object
        duration_prob_dist -- io.DurationProbabilityDistribution() object
        staff -- Integer, indicating number of staff assigned to the program
        
        Inheritance:
        Subclass of technical.TechnicalRecoveryProgram()
        """    
        TechnicalRecoveryProgram.__init__(self, env, duration_prob_dist, staff)

    def process(self, structure, entity, callbacks = None):
        """Define process for entity to request a building permit for their
        building.

        Keyword Arguments:
        structure -- Some structures.py object, such as structures.SingleFamilyResidential()
        entity -- An entity (e.g., entities.OwnerHousehold()) that initiates 
                    and benefits from the process.
        callbacks -- a generator function containing processes to start after the
                    completion of this process.
        
        Returns or Attribute Changes:
        entity.story -- Append story strings to entity's story
        entity.permit_put -- Records sim time of permit request
        entity.permit_get -- Records sim time of permit reciept
        structure.permit = True, if successfully permitted
        """
        # Record time permit application submitted.
        entity.permit_put = self.env.now

        # Request permit processor / building official.
        staff_request = self.staff.request()
        yield staff_request

        # Yield process timeout equal to duration required to review permit request.
        yield self.env.timeout(self.duration())

        # Release permit process to allow them to review other requests.
        self.staff.release(staff_request)

        structure.permit = True

        # Record time that permit is granted.
        entity.permit_get = self.env.now

        #If true, write outcome of process to story.
        if entity.write_story:
            entity.story.append(
            "{0} received permit approval {1:.0f} days after the event. "
            .format(entity.name.title(), entity.permit_get)
            )

        if callbacks is not None:
            yield self.env.process(callbacks)
        else:
            pass

class RepairProgram(TechnicalRecoveryProgram):
    """A class to represent staff allocation and process duration associated with 
    building repair. The class also represents building/concstruction materials in 
    a simplified way--a single simpy.Container representing the inventory dollar
    value of undifferented materials
    
    *** Currently no conceptual or algorithmic difference is made
    between repairs and reconstruction. Potentially eventually this should be done,
    likely as a separate program together with another program for demolition.
    Currently building materials are undifferentiad. Potentially eventually can 
    represent different material types with separate simpy Containers (e.g., 
    wood, metal, aggregate, etc.)***
    
    Methods:
    __init__(self, env, duration_prob_dist, staff=float('inf'))
    process(self, structure, entity = None, callbacks = None)
    """
    def __init__(self, env, duration_prob_dist, staff=float('inf'), materials=float('inf'), ):
        """Initiate RepairProgram object.
        
        Keyword Arguments:
        env -- simpy.Envionment() object
        duration_prob_dist -- io.DurationProbabilityDistribution() object
        staff -- Integer, indicating number of staff assigned to the program
        
        Inheritance:
        Subclass of technical.TechnicalRecoveryProgram()
        """    
        TechnicalRecoveryProgram.__init__(self, env, duration_prob_dist, staff)
        
        # Simpy Container to represent bulding materials as inventory dollar value
        # of undifferented materials.
        self.materials = Container(self.env, init=materials) 
        
    def process(self, structure, entity, callbacks = None):
        """A process to rebuild a building structure based on available contractors 
        and building materials.

        Keyword Arguments:
        structure -- Some structures.py object, such as structures.SingleFamilyResidential()
        entity -- An entity (e.g., entities.OwnerHousehold()) that initiates 
                    and benefits from the process.
        callbacks -- a generator function containing processes to start after the
                    completion of this process.
        
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
            if materials_cost > self.materials.level:

                # If true, write outcome of the process to the story
                if entity.write_story:
                    entity.story.append(
                    'There were insufficient construction materials available in the area for {0} to rebuild. '
                    .format(entity.name.title())
                    )

                return

            # Deal with case that entity does not have enough money to rebuild.
            if entity.money_to_rebuild < structure.damage_value:
                # If true, write outcome of the process to the story
                if entity.write_story:
                    entity.story.append(
                        '{0} was unable to get enough money to repair the {1}. '.format(
                        entity.name.title(), entity.property.occupancy.lower())
                                        )
                return

            # If entity has enough money & there is enough available construction
            # materials in the region, then rebuild.
            if (entity.money_to_rebuild >= structure.damage_value and
            materials_cost <= self.materials.level):


                # Record time put in request for home rebuild.
                entity.rebuild_put = self.env.now

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
                yield self.materials.get(materials_cost)

                # Yield timeout equivalent to rebuild time.
                yield self.env.timeout(rebuild_time)

                # Release contractors.
                self.staff.release(staff_request)

                # After successful rebuild, set damage to None & $0.
                structure.damage_state = 'None'

                # Record time when entity gets home.
                entity.rebuild_get = self.env.now

                # If True, write outcome of successful rebuild to story.
                if entity.write_story:
                    entity.story.append(
                        '{0}\'s {1} was repaired {2:,.0f} days after the event, taking {3:.0f} days to rebuild. '.format(
                            entity.name.title(), structure.occupancy.lower(),
                            entity.rebuild_get,
                            entity.rebuild_get - entity.rebuild_put
                        )
                    )

        # Handle any interrupt thrown by another process
        except Interrupt as i:
            # If true, write outcome of the process to the story
            if entity.write_story:
                entity.story.append(
                        '{0} gave up {1:.0f} days into the rebuild process. '.format(
                        entity.name.title(), i.cause))

        if callbacks is not None:
            yield env.process(callbacks)

        else:
            pass

class RepairStockProgram(TechnicalRecoveryProgram):
    """ A class to represent a large-scale/bulk program for expedited repairing
    of a building stock. Conceptually this is intended to rebuild vacant building
    stocks that do not have entities associated with them to rebuild them. This bulk
    rebuilding potentially provides additional homes for entities to purchase or rent.
    
    *** CURRENTLY BROKEN ***
    
    Methods:
    __init__(self, env, duration_prob_dist, staff=float('inf'))
    process(self, building_stock, rebuild_fraction, rebuild_start)
    """
    
    def __init__(self, env, duration_prob_dist, staff=float('inf')):
        """Initiate RepairStockProgram object.
        
        Keyword Arguments:
        env -- simpy.Envionment() object
        duration_prob_dist -- io.DurationProbabilityDistribution() object
        staff -- Integer, indicating number of staff assigned to the program
        
        Inheritance:
        Subclass of technical.TechnicalRecoveryProgram()
        """    
        TechnicalRecoveryProgram.__init__(self, env, duration_prob_dist, staff)

    def process(self, building_stock, rebuild_fraction, rebuild_start):
        """Process to repair a part or an entire building stock (FilterStore) based
        on available contractors and specified proportion/probability.

        Keyword Arguments:
        building_stock -- A SimPy FilterStore that contains one or more
            structures.BuiltCapital(), structures.Building(), or structures.Residence()
            objects that represent vacant structures for purchase.
        rebuild_fraction -- A value to set approximate percentage of number of structures
            in the stock to rebuild.
        rebuild_start -- Duration to timeout prior to rebuilding commences.

        Attribute Changes:
        put_structure.damage_state -- Changed to 'None' for selected structures.
        put_structure.damage_value = Changed to $0.0 for selected structures.
        """
        yield self.env.timeout(rebuild_start)
        
        potential_buildings = []  # Empty list to temporarily place FilterStore objects.
        num_fixed = 0  # Counter
        
        for building in building_stock.items:
            # if (building.damage_state == 'Complete'
            #     or building.damage_state == 'Extensive'
            #     or building.damage_state == 'Moderate'):
            #     potential_buildings.append(building)
            building.inspected = True
            building.assessment = True
            building.permit = True
            building.damage_state = 'None'
            building.damage_value = 0.0
            num_fixed += 1
        
        choice_size = int(rebuild_fraction*len(potential_buildings))
        chosen_buildings = choice(potential_buildings, choice_size, replace=False)
        

        
        # # Iterate through structures, do processing, put back into the FilterStore
        # for building in potential_buildings:
        #     building.inspected = True
        #     building.assessment = True
        #     building.permit = True
        #     building.damage_state = 'None'
        #     building.damage_value = 0.0
        #     num_fixed += 1
                    
        print('{0} homes in the vacant building stock were fixed on day {1:,.0f}.'.format(num_fixed, self.env.now))

# def repair_stock(building_stock, rebuild_fraction)):
# 
#         potential_buildings = []  # Empty list to temporarily place FilterStore objects.
# 
#         for building in building_stock.items:
#             if (building.damage_state == 'Complete'
#                 or building.damage_state == 'Extensive'
#                 or building.damage_state == 'Moderate'):
#                 potential_buildings.append(building)
#         
#         choice_size = int(rebuild_fraction*len(potential_buildings))
#         chosen_buildings = choice(potential_buildings, choice_size, replace=False)
#         
#         num_fixed = 0  # Counter
#         
#         # Iterate through structures, do processing, put back into the FilterStore
#         for building in chosen_buildings:
#             building.inspected = True
#             building.assessment = True
#             building.permit = True
#             building.damage_state = 'None'
#             building.damage_value = 0.0
#             num_fixed += 1
#                     
#         print('{0} homes in the vacant building stock were fixed on day {1:,.0f}.'.format(num_fixed, self.env.now))
