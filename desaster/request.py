# -*- coding: utf-8 -*-
"""
Created on Thu Jan 14 09:14:04 2016

@author: Derek
"""
from config import inspection_time, adjuster_time, fema_process_time

def inspection(entity, 
               simulation, 
               resource,
               callbacks = None):
    """Request an inspection, do inspection, update entity attribute times.
    
    Keyword Arguments:
    entity -- An entity object from the Entity() class. Must have a value for 
              attribute 'insurance_coverage', which should be set at __init__()
             
    simulation -- A simpy.Environment() object. This references the simulation
                  environment, and is usually set as the first variable in a
                  simulation, e.g. simulation = simpy.Environment().
                  
    inspector -- A simpy.resource object. can be any type of resource that has a 
                request() method. 
                
                     
    callbacks -- a generator function containing any processes you want to start
                 after the completion of the insurance claim. If this does not 
                 contain a yield (therefore isn't a generator), simpy will throw
                 an error. Defaults to None.
                 
    Returns or Attribute Changes:
    
    entity.inspection_put -- Record time of inspection request
    entity.inspection_get -- Record time of inspection completion
    entity.story -- append natural language summary of process
    """

    with resource.inspectors.request() as request:

        # Put in request for an inspector (shared resource)
        entity.inspection_put = simulation.now
        #the inspection_put attribute can be added after init, 
        yield request

        # Duration of inspection
        yield simulation.timeout(inspection_time)

        # The time that the inspection has been completed
        entity.inspection_get = simulation.now
        response_time = simulation.now
        #write their story
        entity.story.append(
        "{1}'s house was inspected {0} days after the event. ".format(
        response_time, entity.name))
        
        
        if callbacks is not None:
            yield simulation.process(callbacks)
        else:
            pass

def file_insurance_claim(entity, #Entity object (the household usually)
                         simulation, #a simpy.Environment() object
                         resource,
                         callbacks = None):
    """File an insurance claim, assign claim amounts to entity objects.
    
    Keyword arguments:
    entity -- An entity object from the Entity() class. Must have a value for 
              attribute 'insurance_coverage', which should be set at __init__()
             
    simulation -- A simpy.Environment() object. This references the simulation
                  environment, and is usually set as the first variable in a
                  simulation, e.g. simulation = simpy.Environment().
                  
    adjuster -- A simpy.resource object. can be any type of resource that has a 
                request() method. 
                
                     
    callbacks -- a generator function containing any processes you want to start
                 after the completion of the insurance claim. If this does not 
                 contain a yield (therefore isn't a generator), simpy will throw
                 an error. Defaults to None.
                 
    Returns or attribute changes:
    
    entity.claim_put -- Record current simulation time at the time the entity
                        enters the adjuster queue
                        
    entity.claim_payout -- Set claim payout equal to coverage amount
    
    entity.claim_get -- Record simulation time when entity recieves payout
    
    entity.story -- Append natural language sentences to entities story.
    """
                         
    with resource.insurance_adjusters.request() as request:
        # Record time that claim is put in
        entity.claim_put = simulation.now
        yield request

        # Duration of claim processing
        yield simulation.timeout(adjuster_time)

        # Amount of insurance claim payout
        # This is where we'd add actual claims payout logic 
            #(you don't get your whole payout, etc)
        entity.claim_payout = entity.insurance_coverage

        # Record when the time when household gets claim payout
        entity.claim_get = simulation.now

    # Write the household's story
    entity.story.append(
        '{0} received a ${1} insurance payout after a {2} day wait.'.format(
        entity.name, entity.claim_payout, entity.claim_get))
    if callbacks is not None:   
        yield simulation.process(callbacks)

    else:
        pass
    
def fema_assistance(entity, 
                    simulation,
                    resource,
                    callbacks = None):
    """Request and receive assistance from fema.
    
    entity -- An entity object from the Entity() class. Must have a value for 
              attributes: 'damage_value', 'claim_payout', 
              which should be set at __init__()
             
    simulation -- A simpy.Environment() object. This references the simulation
                  environment, and is usually set as the first variable in a
                  simulation, e.g. simulation = simpy.Environment().
                  
    fema_processors -- A simpy.resource object. can be any type of resource 
                       that has a request() method. 
                       
    resource.fema_aid -- money provided by fema for the purposes of general aid. This
                  has to be a simpy container, as it needs to have a get()
                  method and a put() method. 
                     
    callbacks -- a generator function containing any processes you want to start
                 after the completion of the insurance claim. If this does not 
                 contain a yield (therefore isn't a generator), simpy will throw
                 an error. Defaults to None.
                 
    function version date: Jan 25 2015
    
    Returns or Attribute Changes:
    
    entity.assistance_put -- Records sim time of fema processor request
    
    entity.assistance_get -- Records sim time of fema assistance reciept 
    
    entity.assistance_request -- The amount of money being requested by the 
                                 entity, equal to the damage_value minus the 
                                 claim_payout provided by the insurance process
    
    entity.assistance_payout -- amount of money given to the entity, equal to 
                                the request amount, or whatever is left in the
                                resource.fema_aid container, whichever is higher.
    
    """             

    # To process assistance request must request and wait 
    #for a FEMA application processor
    with resource.fema_processors.request() as request:
        # Put in request for FEMA individual assistance; record time requested
        entity.assistance_put = simulation.now
        yield request

        # Time required for FEMA to process assistance request
        yield simulation.timeout(fema_process_time)

        # Record time household gets FEMA assistance
        entity.assistance_get = simulation.now

    # Compute amount of assistance requested from FEMA; if insurance payout covers repair cost it is zero
    entity.assistance_request = entity.damage_value - entity.claim_payout

    # If requesting assistance, determine if FEMA has money left to provide assistance
    ## I think this should actually just be a request to the resource and if 
    ## there isn't money left, it just sits in the queue.
    
    if entity.assistance_request > 0: #determine need of assistance, if none, move to else
        if entity.assistance_request <= resource.fema_aid.level:

            entity.assistance_payout = entity.assistance_request

            # Write the household's story
            entity.story.append(
                '{0} received ${1} from FEMA after a {2} day wait. '.format(
                entity.name, entity.assistance_payout, entity.assistance_time))

            yield resource.fema_aid.get(entity.assistance_request)

        elif resource.fema_aid.level > 0: 

            entity.assistance_payout = resource.fema_aid.level

            # Write the household's story
            entity.story.append(
                '{0} requested ${1} from FEMA but only received ${2}. '.format(
                entity.name, entity.assistance_request, entity.assistance_payout))
            entity.story.append(
                'It took {0} days for FEMA to provide the assistance. '.format(
                entity.assistance_time))

            yield resource.fema_aid.get(resource.fema_aid.level)

        else:
            entity.assistance_payout = 0

            # Write the household's story
            entity.story.append(
                '{0} received no money from FEMA because of inadequate funding. '.format(
                entity.name))

    else:
        entity.assistance_payout = 0

        # Write the household's story
        entity.story.append(
            '{0} did not need FEMA assistance. '.format(
            entity.name))
            
    if callbacks is not None:   
        yield simulation.process(callbacks)

    else:
        pass
