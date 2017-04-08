# -*- coding: utf-8 -*-
"""
Module of various recovery processes that make complex requests to 
resources.

Functions:
inspection(simulation, program, structure, entity = None, 
            write_story = False, callbacks = None)
insurance_claim(simulation, program, entity, write_story = False, 
                callbacks = None)
fema_assistance(simulation, program, financial_capital, entity, 
                write_story = False, callbacks = None)
engineering_assessment(simulation, program, entity, write_story = False, 
                        callbacks = None)
loan(simulation, program, entity, write_story = False, callbacks = None)
permit(simulation, program, entity, write_story = False, 
            callbacks = None)
reoccupy(simulation, entity, write_story = False, callbacks = None):

@author: Derek Huling, Scott Miles
"""
from simpy import Interrupt

def inspection(simulation, program, structure, entity = None, 
                write_story = False, callbacks = None):
    """Define process for inspecting an entity's structure.

    Keyword Arguments:
    entity -- An entity object from the entity.py module, for example
                entities.Household(). Defaults to none so that can inspect
                structures that aren't associated with an entity.
                *** Currently, this function expects that the entity *is*
                an entities.Household() object because makes an assignment to
                Household().residence.inspected***
    simulation -- A simpy.Environment() object.
    callbacks -- a generator function containing processes to start after the 
                    completion of this process.
    program -- A capitals.HumanCapital() object.
    structure -- A capitals.BuiltCapital() object or an object of a BuiltCapital()
                sub-class, such as capitals.Residence()
    write_story -- Boolean indicating whether to track a households story.

    Returns or Attribute Changes:
    entity.inspection_put -- Record time of inspection request
    entity.inspection_get -- Record time of inspection completion
    entity.residence.inspected -- Whether inspection was successful.
    entity.story -- Summary of process outcome as string.
    """
    
    # Only record inspection request time if structure associated with an entity.
    if entity != None:
        # Put in request for an inspector (shared resource)
        entity.inspection_put = simulation.now
    
    # Request inspectors
    inspectors_request = program.staff.request()
    yield inspectors_request

    # Yield timeout equivalent to time from hazard event to end of inspection.
    yield simulation.timeout(program.duration())
    
    # Set attribute of structure to indicate its been inspected.
    structure.inspected = True
    
    # Release inspectors now that inspection is complete.
    program.staff.release(inspectors_request) 
    
    # Only record inspection time and write story if structure associated with 
    # an entity.
    if entity != None:
        entity.inspection_get = simulation.now
        
        #If true, write process outcome to story
        if write_story == True:
            
            entity.story.append(
                            "{0}'s {1} was inspected {2:.0f} days after the event and suffered ${3:,.0f} of damage.".format(
                            entity.name.title(), entity.residence.occupancy.lower(),
                            entity.inspection_get, entity.residence.damage_value))

    if callbacks is not None:
        yield simulation.process(callbacks)
    else:
        pass

def insurance_claim(simulation, program, entity, write_story = False, 
                    callbacks = None):
    """Define process for entity to submit an insurance claim.

    Keyword arguments:
    entity -- An entity object from the entity.py module, for example
                entities.Household().
    simulation -- A simpy.Environment() object.
    program -- A capitals.HumanCapital() object.
    write_story -- Boolean indicating whether to track a households story.
    callbacks -- a generator function containing processes to start after the 
                    completion of this process.

    Returns or attribute changes:
    entity.claim_put -- Record current simulation time at the time the entity
                        enters the adjuster queue
    entity.claim_payout -- Set claim payout equal to damage value amount.
    entity.claim_get -- Record simulation time when entity recieves payout
    entity.story -- Append natural language sentences to entities story.
    """
    # Exception handling in case interrupted by another process.
    try: 
        # Ensure entity has insurance.
        if entity.insurance <= 0.0:
            if write_story == True:
                entity.story.append(
                    '{0} has no hazard insurance. '.format(
                        entity.name.title()
                        )
                    )
            return
        
        # Has insurance so submits a claim.
        else:  
            # Record time that claim request is put.
            entity.claim_put = simulation.now   

            #If true, write claim submission time to story.
            if write_story == True:
                entity.story.append(
                    '{0} submitted an insurance claim {1:.0f} days after the event. '.format(
                        entity.name.title(), entity.claim_put)
                    )
            
            # The insurance deductible amount is the home value multiplied by the 
            # coverage ratio multipled by the deductible percentage.
            deductible_amount = entity.residence.value * entity.insurance * program.deductible
            
            # Determine payout amount and add to entity's rebuild money.
            # Only payout amount equal to the damage, not the full coverage.
            if entity.residence.damage_value < deductible_amount:
                if write_story == True:
                    entity.story.append(
                        '{0}\'s insurance deductible is greater than the value of damage. '.format(
                        entity.name.title())
                        )   
                entity.claim_get = simulation.now
                return
            
            # If damage > deductible, submit request for insurance adjusters.
            request = program.staff.request()
            yield request

            # Timeout process to simulate claims processing duration.
            yield simulation.timeout(program.duration())  
          
            entity.claim_payout = entity.residence.damage_value - deductible_amount

            entity.money_to_rebuild += entity.claim_payout

            # Record when the time when household gets claim payout
            entity.claim_get = simulation.now     

            # Release insurance adjusters so they can process other claims.
            program.staff.release(request)
            
            #If true, write process outcome to story.
            if write_story == True:
                entity.story.append(
                    '{0} received a ${1:,.0f} insurance payout {2:.0f} days after the event. '.format(
                        entity.name.title(), 
                        entity.claim_payout,
                        entity.claim_get
                        )
                    )
    # Handle any interrupt thrown by another process.
    except Interrupt as i: 
        #If true, write that the process was interrupted to their story.
        if write_story == True:
            entity.story.append(
                    '{0} gave up during the insurance claim process after a {1} day search for money. '.format(
                    entity.name.title(), i.cause))
    
    if callbacks is not None:
        yield simulation.process(callbacks)
    else:
        pass

def fema_assistance(simulation, program, entity, 
                    write_story = False, callbacks = None):
    """Define process for entity to submit request for FEMA individual assistance.

    entity -- An entity object from the entity.py module, for example
                entities.Household().
    simulation -- A simpy.Environment() object.
    program -- A capitals.HumanCapital() object.
    financial_capital -- A capitals.FinancialCapital() object.
    write_story -- Boolean indicating whether to track a households story.
    callbacks -- a generator function containing processes to start after the 
                    completion of this process.

    Returns or Attribute Changes:
    entity.assistance_put -- Records sim time of fema processor request
    entity.assistance_get -- Records sim time of fema assistance reciept
    entity.assistance_request -- The amount of assistance requested.
    entity.assistance_payout -- Amount of FEMA aid given to the entity.
    """
    # Exception handling in case interrupted by another process.
    try:
        #Ensure that entity does not have enough money to rebuild already.
        if entity.money_to_rebuild >= entity.residence.damage_value:
            return
        # If does not have enough money to rebuild, submit request to FEMA.
        else: 
            # Record time requests FEMA assistance.
            entity.assistance_put = simulation.now  
            #If true, write FEMA request time to story.
            if write_story == True:    
                entity.story.append(
                    '{0} submitted a request to FEMA {1:.0f} days after the event. '.format(
                        entity.name.title(), entity.assistance_put
                        )
                    )
            # Request a FEMA processor to review aid application.
            request = program.staff.request()
            yield request
            
            # Yield timeout for duration necessary to process FEMA aid request.
            yield simulation.timeout(program.duration())

            # Release FEMA processors. 
            program.staff.release(request)
            
            # Record time received FEMA assistance.
            entity.assistance_get = simulation.now

            # Must subtract any insurance payout from FEMA payout and choose the lesser of 
            #max assistance and deducted total
            entity.assistance_request = min(program.max_outlay, (entity.residence.damage_value 
                                        - entity.claim_payout))

            # If requesting assistance, determine if FEMA has money left to 
            # provide assistance.
            if entity.assistance_request <= program.budget.level and entity.assistance_request != 0:
                # FEMA has enough money to fully pay requested amount.
                entity.assistance_payout = entity.assistance_request
                entity.money_to_rebuild += entity.assistance_payout

                # Subtract payout amount from the overall amount of assistance
                # FEMA has available to payout to all requests.
                yield program.budget.get(entity.assistance_request)
                
                #If true, write process outcome to story.
                if write_story == True:
                    entity.story.append(
                        '{0} received ${1:,.0f} from FEMA {2:.0f} days after the event. '.format(
                            entity.name.title(),
                            entity.assistance_payout,
                            entity.assistance_get
                            )
                        )
            elif program.budget.level > 0:
                # FEMA has money left but less than requested.
                # Set payout equal to remaining funds.
                entity.assistance_payout = program.budget.level
                entity.money_to_rebuild += entity.assistance_payout
                
                # Subtract payout amount from the overall amount of assistance
                # FEMA has available to payout to all requests.
                yield program.budget.get(program.budget.level)
                
                #If true, write process outcome to story.
                if write_story == True:
                    entity.story.append(
                     '{0} requested ${1:,.0f} from FEMA but only received ${2:,.0f}, {3} days after the event.. '
                     .format(
                                entity.name.title(),
                                entity.assistance_request,
                                entity.assistance_payout,
                                entity.assistance_get
                            )
                        )    
            else:
                # FEMA has no money left to make payout.
                entity.assistance_payout = 0.0
                
                #If true, write process outcome to story.
                if write_story == True:
                    entity.story.append(
                    '{0} received no money from FEMA because of inadequate funding. '
                    .format(entity.name.title())
                    )
            
    # Catch any interrupt from another process.      
    except Interrupt as i:
        #If true, write process outcome to story.
        if write_story == True:
            entity.story.append(
                    '{0} gave up during the FEMA assistance process after a {1} day search for money. '.format(
                        entity.name.title(), i.cause)
                    )

    if callbacks is not None:
        yield simulation.process(callbacks)
    else:
        pass

def engineering_assessment(simulation, program, entity, write_story = False, 
                            callbacks = None):
    """Define process for entity to request an engineering assessment of their
    structure.
    
    Keyword Arguments:
    entity -- An entity object from the entity.py module, for example
                entities.Household().
    simulation -- A simpy.Environment() object.
    program -- A capitals.HumanCapital() object.
    write_story -- Boolean indicating whether to track a households story.
    callbacks -- a generator function containing processes to start after the 
                    completion of this process.

    Returns or Attribute Changes:
    entity.assessment_put -- Records sim time of assessment request
    entity.assistance_get -- Records sim time of assessment reciept
    """
    
    # Record time that assessment request put in.
    entity.assessment_put = simulation.now
    
    # Request an engineer.
    request = program.staff.request()
    yield request

    # Yield process timeout for duration necessary to assess entity's structure.
    yield simulation.timeout(program.duration())
    
    # Release engineer so it can assess other structures.
    program.staff.release(request)
    
    # Record time when assessment complete.
    entity.assessment_get = simulation.now
    
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

def loan(simulation, program, entity, write_story = False, callbacks = None):
    """Define process for entity to submit request for loan (e.g., from SBA).

    entity -- An entity object from the entity.py module, for example
                entities.Household().
    simulation -- A simpy.Environment() object.
    program -- A capitals.HumanCapital() object.
    write_story -- Boolean indicating whether to track a households story.
    callbacks -- a generator function containing processes to start after the 
                    completion of this process.

    Returns or Attribute Changes:
    entity.loan_put -- Records sim time of loan request
    entity.loan_get -- Records sim time of loan reciept
    entity.loan_amount -- The amount of loan requested.
    """
    # Exception handling in case interrupted by another process.
    try:
        # Ensure entity does not have enough money to rebuild.
        if entity.money_to_rebuild >= entity.residence.damage_value:
            return
        else:
            # Does not have enough money to rebuild.
            # Record time application submitted.
            entity.loan_put = simulation.now 
            
            # If true, write loan request time to story.
            if write_story == True:
                   
                entity.story.append(
                    '{0} submitted a loan application {1:.0f} days after the event. '.format(
                        entity.name.title(), entity.loan_put)
                    )
            
            # Request a loan processor.
            request = program.staff.request()
            yield request

            # Yield process timeout for duration needed to process loan request.
            yield simulation.timeout(program.duration())
            
            # Release loan processor so that they can process other loans.
            program.staff.release(request)

            # Record time loan is given.
            entity.loan_get = simulation.now
            
            # Subtract any insurance or FEMA payouts from damage value to 
            # arrive at loan amount.
            entity.loan_amount = (
                                    entity.residence.damage_value 
                                    - entity.claim_payout
                                    - entity.assistance_payout
                                )
            
            # Add loan amount to entity's money to rebuild.
            if entity.loan_amount > 0.0:
                entity.money_to_rebuild += entity.loan_amount
                
                #If true, write process outcome to story.
                if write_story == True:
                
                    entity.story.append(
                    "{0} received a loan for ${1:,.0f} {2:.0f} days after the event. "
                    .format(entity.name.title(), entity.loan_amount, entity.loan_get))

    # Handle any interrupt from another process.
    except Interrupt as i:
        #If true, write interrupt outcome to story.
        if write_story == True:
            entity.story.append(
                    '{0} gave up during the loan approval process after a {1} day search for money. '.format(
                    entity.name.title(), i.cause))
    
    if callbacks is not None:
        yield simulation.process(callbacks)
    else:
        pass

def permit(simulation, program, entity, write_story = False, callbacks = None):
    """Define process for entity to request an engineering assessment of their
    structure.

    Keyword Arguments:
    entity -- An entity object from the entity.py module, for example
                entities.Household().
    simulation -- A simpy.Environment() object.
    program -- A capitals.HumanCapital() object.
    write_story -- Boolean indicating whether to track a households story.
    callbacks -- a generator function containing processes to start after the 
                    completion of this process.

    Returns or Attribute Changes:
    entity.permit_put -- Records sim time of permit request
    entity.permit_get -- Records sim time of permit reciept
    """
    # Record time permit application submitted.
    entity.permit_put = simulation.now

    # Request permit processor / building official.
    request = program.staff.request()
    yield request
    
    # Yield process timeout equal to duration required to review permit request.
    yield simulation.timeout(program.duration())

    # Release permit process to allow them to review other requests.
    program.staff.release(request)

    # Record time that permit is granted.
    entity.permit_get = simulation.now
    
    #If true, write outcome of process to story.
    if write_story == True:
        entity.story.append(
        "{0} received permit approval {1:.0f} days after the event. "
        .format(entity.name.title(), entity.permit_get)
        )

    if callbacks is not None:
        yield simulation.process(callbacks)
    else:
        pass

