# -*- coding: utf-8 -*-
"""
Created on Thu Jan 14 09:14:04 2016

@author: Derek, Scott
"""
from simpy import Interrupt
from desaster.config import inspection_time, adjuster_time, fema_process_time
from desaster.config import engineering_assessment_time, loan_process_time
from desaster.config import permit_process_time

def inspection(simulation, human_capital, entity, callbacks = None):
    """Request an inspection, do inspection, update entity attribute times.

    Keyword Arguments:
    entity -- An entity object from the Entity() class. Must have a value for
              attribute 'insurance_coverage', which should be set at __init__()

    simulation -- A Environment() object. This references the simulation
                  environment, and is usually set as the first variable in a
                  simulation, e.g. simulation = Environment().

    callbacks -- a generator function containing any processes you want to start
                 after the completion of the insurance claim. If this does not
                 contain a yield (therefore isn't a generator), simpy will throw
                 an error. Defaults to None.

    Returns or Attribute Changes:

    entity.inspection_put -- Record time of inspection request
    entity.inspection_get -- Record time of inspection completion
    entity.story -- append natural language summary of process
    """

    # Put in request for an inspector (shared resource)
    entity.inspection_put = simulation.now
    
    # ??? the inspection_put attribute can be added after init, ???
    request = human_capital.inspectors.request()
    yield request

    # Duration of inspection
    yield simulation.timeout(inspection_time)
    
    # The time that the inspection has been completed
    entity.inspection_get = simulation.now

    # --% Added release statement
    human_capital.inspectors.release(request)

    #write their story
    entity.story.append(
    "{1}'s house was inspected {0} days after the event. ".format(entity.inspection_get, entity.name))
    
    entity.story.append(
                    'The event caused ${0} of damage to the residence. '.format(entity.residence.damage_value)
                    )

    if callbacks is not None:
        yield simulation.process(callbacks)
    else:
        pass

def insurance_claim(simulation, human_capital, entity, callbacks = None):
    """File an insurance claim, assign claim amounts to entity objects.

    Keyword arguments:
    entity -- An entity object from the Entity() class. Must have a value for
              attribute 'insurance_coverage', which should be set at __init__()

    simulation -- A Environment() object. This references the simulation
                  environment, and is usually set as the first variable in a
                  simulation, e.g. simulation = Environment().

    callbacks -- a generator function containing any processes you want to start
                 after the completion of the insurance claim. If this does not
                 contain a yield (therefore isn't a generator), simpy will throw
                 an error. Defaults to None.

    Returns or attribute changes:

    entity.claim_put -- Record current simulation time at the time the entity
                        enters the adjuster queue

    entity.claim_payout -- Set claim payout equal to damage value amount.

    entity.claim_get -- Record simulation time when entity recieves payout

    entity.story -- Append natural language sentences to entities story.
    """
    try: # in case a process interrupt is thrown in a master process
        
        if entity.money_to_rebuild >= entity.residence.damage_value:  # Doesn't need to make a claim
            
            return
        
        elif entity.insurance == 0.0:  # Has no insurance
            
            return
        
        else: # Has insurance and needs to submit a claim
            
            entity.claim_put = simulation.now   # Record time that claim is put in
            
            entity.story.append(
                '{0} submitted an insurance claim {1} days after the event. '.format(
                entity.name, entity.claim_put))
            
            request = human_capital.insurance_adjusters.request()
            yield request

            yield simulation.timeout(adjuster_time)    # Duration of claim processing

            
            entity.claim_get = simulation.now     # Record when the time when household gets claim payout

            human_capital.insurance_adjusters.release(request)
            
            # Only payout amount equal to the damage, not the full coverage
            if entity.residence.damage_value < entity.insurance:
                entity.claim_payout = entity.residence.damage_value
            else:
                entity.claim_payout = entity.insurance

            entity.money_to_rebuild += entity.claim_payout

            entity.story.append(
                '{0} received a ${1} insurance payout {2} days after the event. '.format(
                entity.name, entity.claim_payout, entity.claim_get))
       
    except Interrupt as i: # Handle any interrupt thrown by a master process
        
        entity.story.append(
                '{0} gave up during the insurance claim process after a {1} day search for money. '.format(
                entity.name, i.cause))
    
    if callbacks is not None:
        yield simulation.process(callbacks)

    else:
        pass

def fema_assistance(simulation, human_capital, financial_capital, entity, callbacks = None):
    """Request and receive assistance from fema.

    entity -- An entity object from the Entity() class. Must have a value for
              attributes: 'residence.damage_value', 'claim_payout',
              which should be set at __init__()

    simulation -- A Environment() object. This references the simulation
                  environment, and is usually set as the first variable in a
                  simulation, e.g. simulation = Environment().

    callbacks -- a generator function containing any processes you want to start
                 after the completion of the insurance claim. If this does not
                 contain a yield (therefore isn't a generator), simpy will throw
                 an error. Defaults to None.


    Returns or Attribute Changes:

    entity.assistance_put -- Records sim time of fema processor request

    entity.assistance_get -- Records sim time of fema assistance reciept

    entity.assistance_request -- The amount of money being requested by the
                                 entity, equal to the residence.damage_value minus the
                                 claim_payout provided by the insurance process

    entity.assistance_payout -- amount of money given to the entity, equal to
                                the request amount or whatever is left in the
                                financial_capital.fema_aid container, whichever is higher.

    """

    try:

        if entity.money_to_rebuild >= entity.residence.damage_value: # Doesn't need FEMA assistance
            return

        else: # Requires FEMA assistance
            
            entity.assistance_put = simulation.now  # Record time household requests FEMA assistance

            entity.story.append(
                '{0} submitted a request to FEMA {1} days after the event. '.format(
                entity.name, entity.assistance_put))

            request = human_capital.fema_processors.request()
            yield request
            
            yield simulation.timeout(fema_process_time)  # Duration required for FEMA to process assistance request

            human_capital.fema_processors.release(request)

            entity.assistance_get = simulation.now   # Record time household gets FEMA assistance

            # Compute amount of assistance requested from FEMA; if insurance payout covers repair cost it is zero
            entity.assistance_request = entity.residence.damage_value - entity.claim_payout

            # If requesting assistance, determine if FEMA has money left to provide assistance
            if entity.assistance_request <= financial_capital.fema_aid.level: # FEMA has enough money
                entity.assistance_payout = entity.assistance_request
                entity.money_to_rebuild += entity.assistance_payout

                yield financial_capital.fema_aid.get(entity.assistance_request)
                
                # Write the household's story
                entity.story.append(
                    '{0} received ${1} from FEMA {2} days after the event. '.format(
                    entity.name, entity.assistance_payout, entity.assistance_get))

            elif financial_capital.fema_aid.level > 0:  # FEMA has money left but less than requested
                entity.assistance_payout = financial_capital.fema_aid.level
                entity.money_to_rebuild += entity.assistance_payout
                
                yield financial_capital.fema_aid.get(financial_capital.fema_aid.level)
                
                # Write the household's story
                entity.story.append(
                 '{0} requested ${1} from FEMA but only received ${2}. '
                 .format(entity.name, entity.assistance_request, entity.assistance_payout))

                entity.story.append(
                    'They received the assistance {0} days after the event. '.format(
                    entity.assistance_get))
    
            else:  # FEMA has no money left
                
                entity.assistance_payout = 0.0

                # Write the household's story
                entity.story.append(
                '{0} received no money from FEMA because of inadequate funding. '
                .format(entity.name))
                
                yield financial_capital.fema_aid.get(financial_capital.fema_aid.level)
            
    # Catch any interrupt from a master process         
    except Interrupt as i:
        
        entity.story.append(
                '{0} gave up during the FEMA assistance process after a {1} day search for money. '.format(
                entity.name, i.cause))
        
    if callbacks is not None:
        yield simulation.process(callbacks)

    else:
        pass

def engineering_assessment(simulation, human_capital, entity, callbacks = None):
    """Request an engineering assessment"""

    entity.assessment_put = simulation.now #time of request
    
    request = human_capital.engineers.request()
    yield request

    yield simulation.timeout(engineering_assessment_time)
    
    human_capital.engineers.release(request)
    
    entity.assessment_get = simulation.now #when assessment is received

    entity.story.append(
    '{0} received an engineering assessment {1} days after the event. '
    .format(entity.name, entity.assessment_get))

    if callbacks is not None:
        yield simulation.process(callbacks)
    else:
        pass

def loan(simulation, human_capital, entity, callbacks = None):
    
    try:

        if entity.money_to_rebuild >= entity.residence.damage_value:  # Don't need a loan
            return
        
        else:
            entity.loan_put = simulation.now # Record time application submitted
                 
            entity.story.append(
                '{0} submitted a loan application {1} days after the event. '.format(
                entity.name, entity.loan_put))

            request = human_capital.loan_processors.request()
            yield request

            yield simulation.timeout(loan_process_time)  # Duration of loan processing

            human_capital.loan_processors.release(request)

            entity.loan_get = simulation.now


            # --% Added initial code to produce loan payout %--
            # TODO Need code here to determine how much money the entity requests for their
            #loan and whether the are approved
            # TODO make sure to add to entity.money_to_rebuild

            entity.loan_amount = entity.residence.damage_value - entity.claim_payout - entity.assistance_payout

            if entity.loan_amount > 0.0:
                entity.money_to_rebuild += entity.loan_amount

                entity.story.append(
                "{0} received a loan for ${1} {2} days after the event. "
                .format(entity.name, entity.loan_amount, entity.loan_get))

    # Handle any interrupt from a master process
    except Interrupt as i:
        
        entity.story.append(
                '{0} gave up during the loan approval process after a {1} day search for money. '.format(
                entity.name, i.cause))
    
    if callbacks is not None:
        yield simulation.process(callbacks)
    else:
        pass

def permit(simulation, human_capital, entity, callbacks = None):

    """Request a permit for building."""
    entity.permit_put = simulation.now

    request = human_capital.permit_processors.request()
    yield request

    yield simulation.timeout(permit_process_time)

    # --% Added release statement
    human_capital.permit_processors.release(request)

    entity.permit_get = simulation.now

    entity.story.append(
    "{0} received permit approval {1} days after the event. "
    .format(entity.name, entity.permit_get))

    if callbacks is not None:
        yield simulation.process(callbacks)
    else:
        pass