# -*- coding: utf-8 -*-
"""
Module of classes for implementing DESaster technical recovery programs.

Classes:
TechnicalRecoveryProgram
InspectionProgram
PermitProgram
EngineeringAssessment
RepairProgram
DemolitionProgram

@author: Scott Miles (milessb@uw.edu), Derek Huling
"""
from desaster.hazus import building_repair_times
import random
from simpy import Interrupt
from simpy import Resource, Container

class TechnicalRecoveryProgram(object):
    """The base class for operationalizing technical recovery programs.
    All such programs staff implemented as simpy resources .

    All other classes of technical recovery programs should inherit from this class,
    either directly or indirectly. The process for TechnicalRecoveryProgram is
    useless and should only be used as an example of how to implement a process in a
    subclass of TechnicalRecoveryProgram.

    Methods:
    __init__(self, env, duration, staff=float('inf'))
    process(self, entity = None)
    writeCompleted(self):
    """
    def __init__(self, env, duration, staff=float('inf')):
        """Initiate a TechnicalRecoveryProgram object.

        Keyword Arguments:
        env -- simpy.Envionment() object
        duration -- distributions.ProbabilityDistribution() object
        staff -- Integer, indicating number of staff assigned to the programs

        Attribute Changes:
        self.staff -- A simpy.Resource() object with a capacity == staff arg
        self.duration -- A function that is used to calculate random durations
                            for the program process
        """
        self.env = env
        self.staff = Resource(self.env, capacity=staff)
        self.duration = duration
        # self.duration = duration.duration()

    def process(self, structure):
        """The process for TechnicalRecoveryProgram for requesting staff and issuing
        SimPy timeouts to represent duration of associated technical process.

        entity -- A structures.py object (e.g., structures.Building) that is the focus of the recovery program.
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
        
        # Get the entity's building/structure so that the building stock's 
        # FilterStore is informed of attribute changes to the building/structure
        # Also means that only one process at a time can access the building.
        get_structure = yield structure.stock.get(lambda getStructure:
                                                    getStructure.__dict__ == structure.__dict__
                                            )

        # Yield timeout equivalent to program's process duration
        yield self.env.timeout(self.duration())

        # Release release staff after process duation is complete.
        self.staff.release(staff_request)
        

        material_cost = 1 # Cost of materials needed (e.g., for RepairProgram)

        # Get out amount equal to cost.
        yield self.materials.get(material_cost) # *** Materials not used in all TechnicalRecoveryProgram subclasses

        # Put back amount equal to cost.
        yield self.materials.put(material_cost)
        
        # Put the property back in the building stock to register attribute change.
        yield structure.stock.put(get_structure)

        self.writeCompleted()
        
    def writeCompleted(self):
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
    __init__(self, env, duration, staff=float('inf'))
    process(self, structure, entity, callbacks = None)
    writeInspected(self, entity, structure):
    """
    def __init__(self, env, duration, staff=float('inf')):
        """Initiate an InspectionProgram object.

        Keyword Arguments:
        env -- simpy.Envionment() object
        duration -- io.ProbabilityDistribution() object
        staff -- Integer, indicating number of staff assigned to the program

        Inheritance:
        technical.TechnicalRecoveryProgram()
        """
        TechnicalRecoveryProgram.__init__(self, env, duration, staff)

    def process(self, structure, entity, callbacks = None):
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
        
        # Put in request for an inspector (shared resource)
        entity.inspection_put = self.env.now

        # Request inspectors
        staff_request = self.staff.request()
        yield staff_request
        
        # Get the entity's building/structure so that the building stock's 
        # FilterStore is informed of attribute changes to the building/structure
        # Also means that only one process at a time can access the building
        get_structure = yield structure.stock.get(lambda getStructure:
                                                    getStructure.__dict__ == structure.__dict__
                                            )
        
        # Yield timeout equivalent to time from hazard event to end of inspection.
        yield self.env.timeout(self.duration.rvs())

        # Set attribute of structure to indicate its been inspected.
        structure.inspected = True

        # Release inspectors now that inspection is complete.
        self.staff.release(staff_request)
        
        # Put the property back in the building stock to register attribute change.
        yield structure.stock.put(get_structure)

        # Only record inspection time and write story if structure associated with
        # an entity.
        if entity != None:
            entity.inspection_get = self.env.now

        self.writeInspected(entity, structure)
        
    def writeInspected(self, entity, structure):
        if entity.write_story:
            entity.story.append(
                            "{0}'s {1} was inspected {2:.0f} days after the event. ".format(
                            entity.name.title(), structure.occupancy.lower(),
                            entity.inspection_get)
                            )
                            
            entity.story.append(
                            "It was found to have a damage level of {0} and was {1}. ".format(
                            structure.damage_state.lower(), 
                            structure.recovery_limit_state.lower())
                            )
            
            entity.story.append(
                            "The value of the damage was ${0:,.0f}. ".format(
                            structure.damage_value))

class EngineeringAssessment(TechnicalRecoveryProgram):
    """A class to represent staff allocation and process duration associated with
    building engineering assessments. Conceptually this intended as a detailed
    damage assessment prior to design, permitting, and repair/construction of
    a building. No actual damage valuation is done by the class process, though
    it would conceputally make sense. It is done in the instantiation of the
    building object (e.g., entities.SingleFamilyResidential.damage_value)
    based on inputted damage_state and HAZUS lookup tables.

    Methods:
    __init__(self, env, duration, staff=float('inf'))
    process(self, structure, entity, callbacks = None)
    writeAssessed(self, entity):
    """
    def __init__(self, env, duration, staff=float('inf'), ):
        """Initiate EngineeringAssessment object.

        Keyword Arguments:
        env -- simpy.Envionment() object
        duration -- io.ProbabilityDistribution() object
        staff -- Integer, indicating number of staff assigned to the program

        Inheritance:
        technical.TechnicalRecoveryProgram()
        """
        TechnicalRecoveryProgram.__init__(self, env, duration, staff)

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
        structure.assessment = True, if successfully assessed
        entity.assessment_put -- Record when assessment request submitted
        entity.assessment_put -- Record when assessment request fulfilled
        """
        # Record time that assessment request put in.
        entity.assessment_put = self.env.now

        # Request an engineer.
        staff_request = self.staff.request()
        yield staff_request
        
        # Get the entity's building/structure to register attribute changes w/ FilterStore
        get_structure = yield structure.stock.get(lambda getStructure:
                                                    getStructure.__dict__ == structure.__dict__
                                            )

        # Yield process timeout for duration necessary to assess entity's structure.
        yield self.env.timeout(self.duration.rvs())

        # Release engineer so it can assess other structures.
        self.staff.release(staff_request)

        structure.assessment = True
        
        # Put the property back in the building stock to register attribute change.
        yield structure.stock.put(get_structure)

        # Record time when assessment complete.
        entity.assessment_get = self.env.now

        self.writeAssessed(entity)

        if callbacks is not None:
            yield env.process(callbacks)
        else:
            pass

    def writeAssessed(self, entity):
        if entity.write_story:
            entity.story.append(
            '{0} received an engineering assessment {1:.0f} days after the event. '
            .format(entity.name.title(), entity.assessment_get)
            )
            
class PermitProgram(TechnicalRecoveryProgram):
    """A class to represent staff allocation and process duration associated with
    building permit processing. Conceptually this intended prior to building
    repairs or construction.

    Methods:
    __init__(self, env, duration, staff=float('inf'))
    process(self, structure, entity, callbacks = None)
    writePermitted(self, entity):
    """
    def __init__(self, env, duration, staff=float('inf'), ):
        """Initiate PermitProgram object.

        Keyword Arguments:
        env -- simpy.Envionment() object
        duration -- io.ProbabilityDistribution() object
        staff -- Integer, indicating number of staff assigned to the program

        Inheritance:
        technical.TechnicalRecoveryProgram()
        """
        TechnicalRecoveryProgram.__init__(self, env, duration, staff)

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
        
        # Get the entity's building/structure to register attribute changes w/ FilterStore
        get_structure = yield structure.stock.get(lambda getStructure:
                                                    getStructure.__dict__ == structure.__dict__
                                            )

        # Yield process timeout equal to duration required to review permit request.
        yield self.env.timeout(self.duration.rvs())

        # Release permit process to allow them to review other requests.
        self.staff.release(staff_request)

        structure.permit = True
        
        # Put the property back in the building stock to register attribute change.
        yield structure.stock.put(get_structure)

        # Record time that permit is granted.
        entity.permit_get = self.env.now

        self.writePermitted(entity)

        if callbacks is not None:
            yield self.env.process(callbacks)
        else:
            pass

    def writePermitted(self, entity):
        if entity.write_story:
            entity.story.append(
            "{0} received permit approval {1:.0f} days after the event. "
            .format(entity.name.title(), entity.permit_get)
            )
            
class RepairProgram(TechnicalRecoveryProgram):
    """A class to represent staff allocation and process duration associated with
    building repair. The class also represents building/concstruction materials in
    a simplified way--a single simpy.Container representing the inventory dollar
    value of undifferented materials

    *** Currently building materials are undifferentiad. Potentially eventually can
    represent different material types with separate simpy Containers (e.g.,
    wood, metal, aggregate, etc.)***

    Methods:
    __init__(self, env, duration, staff=float('inf'))
    process(self, structure, entity, callbacks = None)
    writeRepaired(self, entity, structure):
    writeGaveUp(self, entity, now):
    """
    def __init__(self, env, duration, staff=float('inf'), materials=float('inf')):
        """Initiate RepairProgram object.

        Keyword Arguments:
        env -- simpy.Envionment() object
        duration -- io.ProbabilityDistribution() object
        staff -- Integer, indicating number of staff assigned to the program

        Inheritance:
        technical.TechnicalRecoveryProgram()
        """
        TechnicalRecoveryProgram.__init__(self, env, duration, staff)

        # Simpy Container to represent bulding materials as inventory dollar value
        # of undifferented materials.
        self.materials = Container(self.env, init=materials)

    def process(self, structure, entity, callbacks = None):
        """A process to repair a building structure based on available contractors
        and building materials.

        Keyword Arguments:
        structure -- Some structures.py object, such as structures.SingleFamilyResidential()
        entity -- An entity (e.g., entities.OwnerHousehold()) that initiates
                    and benefits from the process.
        callbacks -- a generator function containing processes to start after the
                    completion of this process.

        Returns or Attribute Changes:
        entity.story -- Process outcomes appended to story.
        entity.repair_put -- Record time repairs requested
        entity.repair_get -- Record time repairs completed
        structure.damage_state -- Set to 'None' if successful.
        structure.damage_value = Set to $0.0 if successful.
        """
        # Use exception handling in case process is interrupted by another process.
        try:
            # % of damage value related to building materials (vs. labor and profit)
            # **** PERHAPS PROMOTE TO A FUNCTION ARGUMENT ***
            materials_cost_pct = 1.0

            materials_cost = structure.damage_value * materials_cost_pct

            # Record time put in request for home repair.
            entity.repair_put = self.env.now
            
            # Withdraw recovery funds equal to the repair value (assumed to be
            # same as damage value). If no enough available, process waits until 
            # there is.
            yield entity.recovery_funds.get(structure.damage_value)

            # Put in request for contractors to repair home.
            staff_request = self.staff.request()
            yield staff_request
            
            # Get the entity's building/structure to register attribute changes w/ FilterStore
            get_structure = yield structure.stock.get(lambda getStructure:
                                                        getStructure.__dict__ == structure.__dict__
                                                )

            # Get the repair time for the entity from io.py
            # which imports the HAZUS repair time look up table.
            # Rebuild time is based on occupancy type and damage state.
            # Set the program's distribution.loc (e.g., mean) to repair time
            self.duration.loc = building_repair_times.ix[structure.occupancy][structure.damage_state]

            # Obtain necessary construction materials from regional inventory.
            # materials_cost_pct is % of damage value related to building materials
            # (vs. labor and profit)
            yield self.materials.get(materials_cost)

            # Yield timeout equivalent to repair time.
            yield self.env.timeout(self.duration.rvs())

            # Release contractors.
            self.staff.release(staff_request)

            # After successful repair, set damage to None & $0.
            structure.damage_state = 'None'
            structure.damage_value = 0.0
            
            # Put the property back in the building stock to register attribute change.
            yield structure.stock.put(get_structure)

            # Record time when entity gets home.
            entity.repair_get = self.env.now

            self.writeRepaired(entity, structure)

        # Handle any interrupt thrown by another process
        except Interrupt as i:
            self.writeGaveUp(entity, i.cause)

        if callbacks is not None:
            yield env.process(callbacks)

        else:
            pass
            
    def writeRepaired(self, entity, structure):
        if entity.write_story:
            entity.story.append(
                '{0}\'s {1} was repaired {2:,.0f} days after the event. '.format(
                    entity.name.title(), structure.occupancy.lower(),
                    entity.repair_get
                )
            )       
    
    def writeGaveUp(self, entity, now):
        if entity.write_story:
            entity.story.append(
                    '{0} gave up {1:.0f} days into the repair process. '.format(
                    entity.name.title(), now))

class DemolitionProgram(TechnicalRecoveryProgram):
    """A class to represent staff allocation and process duration associated with
    building demolition.

    Methods:
    __init__(self, env, duration, staff=float('inf'))
    process(self, structure, entity, callbacks = None)
    writeDemolished(self, entity, structure):
    """
    def __init__(self, env, duration, staff=float('inf')):
        """Initiate RepairProgram object.

        Keyword Arguments:
        env -- simpy.Envionment() object
        duration -- io.ProbabilityDistribution() object
        staff -- Integer, indicating number of staff assigned to the program

        Inheritance:
        Subclass of technical.TechnicalRecoveryProgram()
        """
        TechnicalRecoveryProgram.__init__(self, env, duration, staff)

    def process(self, structure, entity, callbacks = None):
        """A process to demolition a building structure based on available contractors.

        Keyword Arguments:
        structure -- Some structures.py object, such as structures.SingleFamilyResidential()
        entity -- An entity (e.g., entities.OwnerHousehold()) that initiates
                    and benefits from the process.
        callbacks -- a generator function containing processes to start after the
                    completion of this process.

        Returns or Attribute Changes:
        entity.story -- Process outcomes appended to story.
        entity.demolition_put -- Record time demolition requested
        entity.demolition_get -- Record time demolition finished
        structure.damage_state -- Set to 'Complete' if successful.
        """
        # Record time put in request for home repair.
        entity.demolition_put = self.env.now

        # Put in request for contractors to repair home.
        staff_request = self.staff.request()
        yield staff_request
        
        # Get the entity's building/structure to register attribute changes w/ FilterStore
        get_structure = yield structure.stock.get(lambda getStructure:
                                                    getStructure.__dict__ == structure.__dict__
                                            )

        # Yield timeout equivalent to repair time.
        yield self.env.timeout(self.duration.rvs())

        # Release contractors.
        self.staff.release(staff_request)

        # After successful repair, set damage to Complete.
        structure.damage_state = 'Complete'
        
        # Put the property back in the building stock to register attribute change.
        yield structure.stock.put(get_structure)

        # Record time when entity gets home.
        entity.demolition_get = self.env.now

        self.writeDemolished(entity, structure)

        if callbacks is not None:
            yield env.process(callbacks)

        else:
            pass
            
    def writeDemolished(self, entity, structure):
        # If True, write outcome of successful repair to story.
        if entity.write_story:
            entity.story.append(
                '{0}\'s {1} was demolished {2:,.0f} days after the event. '.format(
                    entity.name.title(), structure.occupancy.lower(),
                    entity.demolition_get
                )
            )
