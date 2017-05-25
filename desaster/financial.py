# -*- coding: utf-8 -*-
"""


@author: Scott Miles (milessb@uw.edu), Derek Huling
"""
from simpy import Interrupt
from simpy import Resource, Container
from desaster.distributions import DurationDistributionHomeLoanSBA


class FinancialRecoveryProgram(object):
    """The base class for operationalizing financial recovery programs.
    All such programs staff and budget implemented as simpy resources or containers.

    All other classes of financial recovery programs should inherit from this class,
    either directly or indirectly. The process for FinancialRecoveryProgram is
    useless and should only be used as an example of how to implement a process in a
    subclass of  FinancialRecoveryProgram.
    """
    def __init__(self, env, duration_distribution, staff=float('inf'), budget=float('inf')):
        """Initiate financial recovery program attributes.

        Keyword Arguments:
        env -- simpy.Envionment() object
        duration_distribution -- io.ProbabilityDistribution() object
        staff -- Integer, indicating number of staff assigned to the programs
        budget -- Integer or float, indicating the initial budget available from
                    the recovery program.

        Attribute Changes:
        self.staff -- A simpy.Resource() object with a capacity == staff arg
        self.budget -- A simpy.Container() object with a initial value == budget arg
        self.duration -- A function that is used to calculate random durations
                            for the program process
        """
        self.env = env
        self.staff = Resource(self.env, capacity=staff)
        self.budget = Container(self.env, init=budget)
        self.duration_distribution = duration_distribution

    def process(self, entity = None, callbacks = None):
        """Define generic financial recovery program process for entity.

        entity -- An entity object from the entities.py module, for example
                    entities.Household().
        callbacks -- a generator function containing processes to start after the
                        completion of this process.

        Returns or Attribute Changes:
        entity.story -- Entity's story list.
        """
        ###
        ### The contents of this function are an example of what can be done
        ### in a subclass of this class. It demonstrates the use of SimPy
        ### Resources and Containiners. The results of the function itself are
        ### useless. It is meant to help create your own function after creating
        ### a subclass that inherits from this class.
        ###

        # Request staff
        staff_request = self.staff.request()
        yield staff_request

        # Yield timeout equivalent to program's process duration
        yield self.env.timeout(self.duration_distribution.value())

        # Release release staff after process duation is complete.
        self.staff.release(staff_request)

        cost = 1

        # Get out amount equal to cost.
        yield self.budget.get(cost)

        # Put back amount equal to cost.
        yield self.budget.put(cost)

        self.writeCompleted(entity)

        if callbacks is not None:
            yield self.env.process(callbacks)
        else:
            pass
            
    def writeCompleted(self, entity):
        if entity.write_story:
            entity.story.append("{0} process completed for {1} after {2} days, leaving a program budget of ${3:,.0f}. ".format(
                                self.__class__, entity.name.title(), self.env.now, self.budget.level
                                                                                        )
                                )
    
    def writeGaveUp(self, entity, recovery_program):
        if entity.write_story:
            entity.story.append("{0} gave up waiting for recovery funds from {1} {2} days after the event. ".format(
                                entity.name.title(), recovery_program, self.env.now
                                                                                        )
                                )
                                
    def writeWithdraw(self, entity, recovery_program):
        #If true, write interrupt outcome to story.
        if entity.write_story:
            entity.story.append(
                    '{0} withdrew their application to {1} {2} days after the event because enough recovery funds were found from other sources. '.format(
                    entity.name.title(), recovery_program, self.env.now))
                    

class IndividualAssistance(FinancialRecoveryProgram):
    """A class for operationalizing FEMA's individual assistance grant program.
    The class process enforces a maximum budget for the program (after which
    no further grants can be made, as well as a maximum outlay that any
    applicant is allowed to receive.


    """
    def __init__(self, env, duration_distribution, staff=float('inf'), budget=float('inf'),
                max_outlay=float('inf'), declaration_duration=0, deadline=540):
        """Initiate FEMA individual assistance recovery program attributes.

        Keyword Arguments:
        env -- simpy.Envionment() object
        duration_distribution -- io.ProbabilityDistribution() object
        staff -- Integer, indicating number of staff assigned to the program
        budget -- Integer or float, indicating the initial budget available from
                    the recovery program.
        max_outlay -- The maximum amount ($) of assistance that any one entity can receive

        Inheritance:
        Subclass of financial.FinancialRecoveryProgram()
        """
        FinancialRecoveryProgram.__init__(self, env, duration_distribution, staff, budget)

        # Set attributes
        self.max_outlay = max_outlay
        self.deadline = deadline
        self.declaration_duration = declaration_duration

    def process(self, entity, callbacks = None):
        """Define process for entity to submit request for FEMA individual assistance.

        entity -- An entity object from the entities.py module, for example
                    entities.OwnerHousehold().
        callbacks -- a generator function containing processes to start after the
                        completion of this process.

        Returns or Attribute Changes:
        entity.fema_put -- Records sim time of fema processor request
        entity.fema_get -- Records sim time of fema assistance reciept
        entity.fema_amount -- Amount of FEMA aid given to the entity.
        """
        # Exception handling in case interrupted by another process.
        try:
            #Ensure that entity does not have enough money to rebuild already.
            if entity.recovery_funds.level >= entity.property.damage_value:
                return

            # If does not have enough money to rebuild, submit request to FEMA.
            
            # Must wait for a disaster declaration 
            yield self.env.timeout(self.declaration_duration)

            # Calculate assistance request.
            # Must subtract any insurance payout from FEMA payout and choose the lesser of
            # max assistance and deducted total
            entity.fema_amount = min(self.max_outlay, (entity.property.damage_value
                                        - entity.claim_amount))

            # Record time requests FEMA assistance.
            entity.fema_put = self.env.now

            # Check to see if missed application deadline
            if self.env.now > self.deadline:
                self.writeDeadline(entity)    
                return # Application rejected, end process
            
            self.writeRequest(entity)

            # Request a FEMA processor to review aid application.
            request = self.staff.request()
            yield request

            # Yield timeout for duration necessary to process FEMA aid request.
            yield self.env.timeout(self.duration_distribution.value())

            # Release FEMA processors.
            self.staff.release(request)

            # Update assistance request in case of funding from parallel insurance process
            entity.fema_amount = min(self.max_outlay, (entity.property.damage_value
                                        - entity.claim_amount))

            if entity.fema_amount <= 0:
                self.writeWithdraw(entity, 'FEMA')
                return

            # Request payout amount from FEMA budget
            # Must wait for request to be fulfilled
            yield self.budget.get(entity.fema_amount)

            yield entity.recovery_funds.put(entity.fema_amount)

            # Record time received FEMA assistance.
            entity.fema_get = self.env.now

            self.writeReceived(entity)

        # Catch any interrupt from another process.
        except Interrupt as i:
            #If true, write process outcome to story.
            if entity.write_story:
                self.writeGaveUp(entity, 'FEMA')

        if callbacks is not None:
            yield self.env.process(callbacks)
        else:
            pass

    def writeDeadline(self, entity):
        if entity.write_story:
            entity.story.append(
                '{0} requested ${1:,.0f} from FEMA {2} days after the event. Their application was rejected because it was submitted after the {3}-day deadline after the disaster declaration that was made on day {4}'.format(
                    entity.name.title(), entity.fema_amount, entity.fema_put, self.deadline, self.declaration_duration)
                )
    
    def writeRequest(self, entity):
        #If true, write FEMA request time to story.
        if entity.write_story:
            entity.story.append(
                '{0} requested ${1:,.0f} from FEMA {2:.0f} days after the event and {3:.0f} days after the disaster declaration. '.format(
                    entity.name.title(), entity.fema_amount, entity.fema_put, (entity.fema_put - self.declaration_duration))
                                )
    def writeReceived(self, entity):
        #If true, write process outcome to story.
        if entity.write_story:
            entity.story.append(
                '{0} received ${1:,.0f} from FEMA {2:.0f} days after the event. '.format(
                    entity.name.title(),
                    entity.fema_amount,
                    entity.fema_get
                    )
                )

class OwnersInsurance(FinancialRecoveryProgram):
    """A class to represent an insurance company's hazard insurance program.
    The class process enforces a deductible to determine how much, if any, the
    insurance claim payout will be.

    """
    def __init__(self, env, duration_distribution, staff=float('inf'), budget=float('inf'),
                deductible=0.0):
        """Initiate owners insurance recovery program attributes.

        Keyword Arguments:
        env -- simpy.Envionment() object
        duration_distribution -- io.ProbabilityDistribution() object
        staff -- Integer, indicating number of staff assigned to the programs
        budget -- Integer or float, indicating the initial budget available from
                    the recovery program. *** Not currently used, but could be used
                    to represent the capitalization of the insurance company (above
                    which it will be bankrupt).
        deductible -- Float[0,1]. Ratio of building value that must be paid by entity
                        as a deductible before receiving a claim payout.

        Inheritance:
        Subclass of financial.FinancialRecoveryProgram()
        """
        FinancialRecoveryProgram.__init__(self, env, duration_distribution, staff, budget)

        self.deductible = deductible

    def process(self, entity, callbacks = None):
        """Define process for entity to submit an owner's insurance claim.

        Keyword arguments:
        entity -- An entity object from the entities.py module, for example
                    entities.OwnerHousehold().
        callbacks -- a generator function containing processes to start after the
                        completion of this process.

        Returns or attribute changes:
        entity.claim_put -- Record current env time at the time the entity
                            enters the adjuster queue
        entity.claim_amount -- Set claim payout equal to damage value amount.
        entity.claim_get -- Record env time when entity recieves payout
        entity.story -- Append natural language sentences to entities story.
        """
        # Exception handling in case interrupted by another process.
        try:
            # Ensure entity has insurance.
            if entity.insurance <= 0.0:
                self.writeNoInsurance(entity)
                return

            # Has insurance so submits a claim.
            else:
                # Record time that claim request is put.
                entity.claim_put = self.env.now

                #If true, write claim submission time to story.
                self.writeRequest(entity)

                # The insurance deductible amount is the home value multiplied by the
                # coverage ratio multipled by the deductible percentage.
                deductible_amount = entity.property.value * entity.insurance * self.deductible

                # Determine payout amount and add to entity's rebuild money.
                # Only payout amount equal to the damage, not the full coverage.
                if entity.property.damage_value < deductible_amount:
                    self.writeDeductible(entity)
                    return

                # If damage > deductible, submit request for insurance adjusters.
                request = self.staff.request()
                yield request

                # Timeout process to simulate claims processing duration.
                yield self.env.timeout(self.duration_distribution.value())

                # Release insurance adjusters so they can process other claims.
                self.staff.release(request)

                entity.claim_amount = entity.property.damage_value - deductible_amount

                # Make request for the claim amount from the insurance budget
                # If get request, add to entity money to rebuild
                yield self.budget.get(entity.claim_amount)

                yield entity.recovery_funds.put(entity.claim_amount)

                # Record when the time when entity gets claim payout
                entity.claim_get = self.env.now

                self.writeReceived(entity)

        # Handle any interrupt thrown by another process.
        except Interrupt as i:
            #If true, write that the process was interrupted to the story.
            if entity.write_story:
                self.writeGaveUp(entity, 'their insurance company')

        if callbacks is not None:
            yield self.env.process(callbacks)
        else:
            pass

    def writeNoInsurance(self, entity):
        if entity.write_story:
            entity.story.append(
                '{0} has no hazard insurance. '.format(
                    entity.name.title()
                    )
                )
    def writeRequest(self, entity):
        if entity.write_story:
            entity.story.append(
                '{0} submitted an insurance claim {1:.0f} days after the event. '.format(
                    entity.name.title(), entity.claim_put)
                )

    def writeDeductible(self, entity):
        if entity.write_story:
            entity.story.append(
                '{0}\'s insurance deductible is greater than the value of damage. '.format(
                entity.name.title())
                )

    def writeReceived(self, entity):
        #If true, write process outcome to story.
        if entity.write_story:
            entity.story.append(
                '{0} received a ${1:,.0f} insurance payout {2:.0f} days after the event. '.format(
                    entity.name.title(),
                    entity.claim_amount,
                    entity.claim_get
                    )
                )

class LoanSBA(FinancialRecoveryProgram):
    """A class to represent a home loan program. The class process enforces a maximum
    loan amount. *** For the most part this class is a placeholder. Loan eligibility
    and loan amount criteria need to be added. ***

    """
    def __init__(self, env, duration_distribution, inspectors=float('inf'),
                officers=float('inf'), budget=float('inf'), max_loan=float('inf'),
                min_credit=0, min_debt_income_ratio=0, declaration_duration=0, deadline = 60):

        """Initiate owner's home loan recovery program attributes.

        Keyword Arguments:
        env -- simpy.Envionment() object
        duration_distribution -- io.ProbabilityDistribution() object
        inspectors -- Integer, indicating number of staff assigned to the programs
        officers --
        budget -- Integer or float, indicating the initial budget available from
                    the recovery program.
        max_loan -- The maximum amount ($) of loan that any one entity can receive
        min_debt_income_ratio -- %%%% NOT IMPLEMENTED BUT COULD USE FOR LOW CREDIT SCORE ENTITIES
        min_credit --

        Inheritance:
        Subclass of financial.FinancialRecoveryProgram()
        """
        FinancialRecoveryProgram.__init__(self, env, duration_distribution, budget)

        # Define staff/personnel specific to this class
        self.officers = Resource(self.env, capacity=officers)
        self.inspectors = Resource(self.env, capacity=inspectors)

        # New attributes
        self.min_credit = min_credit
        self.min_debt_income_ratio = min_debt_income_ratio
        self.max_loan = max_loan
        self.deadline = deadline
        self.declaration_duration = declaration_duration

    def process(self, entity, callbacks = None):
        """Define process for entity to submit request for loan (e.g., from SBA).

        entity -- An entity object from the entities.py module, for example
                    entities.Household().
        callbacks -- a generator function containing processes to start after the
                        completion of this process.

        Returns or Attribute Changes:
        entity.sba_put -- Records sim time of loan request
        entity.sba_get -- Records sim time of loan reciept
        entity.sba_amount -- The amount of loan requested.
        entity.story -- Append natural language sentences to entities story.
        """
        # Exception handling in case interrupted by another process.
        try:
            # Ensure entity does not have enough money to rebuild.
            if entity.recovery_funds.level >= entity.property.damage_value:
                return # Don't qualify for or need SBA loan, end process

            else:
                # Does not have enough money to rebuild.
                 
                # Take a timeout with duration equal to length of time until a 
                # presidential or SBA disaster is declared, making loans available.
                yield self.env.timeout(self.declaration_duration)
                
                # Record time application submitted.
                entity.sba_put = self.env.now

                # Subtract any insurance or FEMA payouts from damage value to
                # arrive at loan amount.
                entity.sba_amount = min(self.max_loan, (
                                        entity.property.damage_value
                                        - entity.claim_amount
                                        - entity.fema_amount
                                    ) )
                
                # Check to see if missed application deadline
                if self.env.now > self.deadline:
                    self.writeDeadline(entity)    
                    return # Application rejected, end process

                self.writeApplied(entity)

                # Request a loan processor.
                officer_request = self.officers.request()
                yield officer_request

                # # Yield process timeout for duration needed for officer to process application.
                if type(self.duration_distribution) == DurationDistributionHomeLoanSBA:
                    yield self.env.timeout(self.duration_distribution.value(credit = entity.credit,
                                                                            min_credit = self.min_credit)
                                                )
                else: # if not, it's ProbabilityDistribution
                    yield self.env.timeout(self.duration_distribution.value())

                if entity.credit < self.min_credit:
                    
                    self.writeDeniedCredit(entity)
                    
                    return

                # Release loan officer so that they can process other loans.
                self.officers.release(officer_request)

                # If approved (enough credit), request an inspector. Then release it.
                # %%% This increases duration by amount of time it takes
                # to get an inspector. Duration of 1 day assumed, currently. %%%%
                inspector_request = self.inspectors.request()
                yield inspector_request
                yield self.env.timeout(1) # Assumed 1 day inspection duration.
                self.inspectors.release(inspector_request)

                self.writeInspected(entity)
                self.writeApproved(entity)

                # Update loan amount (in case other processes in parallel)
                entity.sba_amount = min(self.max_loan, (
                                        entity.property.damage_value
                                        - entity.claim_amount
                                        - entity.fema_amount
                                    ) )

                if entity.sba_amount <= 0:
                    self.writeWithdraw(entity, 'SBA')
                    return

                # If loan amount is greater than $25k, it requires collateral and more paperwork
                if entity.sba_amount > 25000:
                    # Receives $25k immediately as initial disbursement
                    yield self.budget.get(25000)
                    
                    yield entity.recovery_funds.put(25000)
                    

                    self.writeFirstDisbursement(entity)
                    
                    #
                    # %%%% EVENTUALLY MAKE WAIT FOR A BUILDING PERMIT TO BE ISSUED %%%
                    # %%% FOR NOW: Yield another timeout equal to initial process application duration %%%
                    #

                    if type(self.duration_distribution) == DurationDistributionHomeLoanSBA:
                        yield self.env.timeout(self.duration_distribution.value(credit = entity.credit,
                                                                                min_credit = self.min_credit)
                                                                                )
                    else: # if not, it's ProbabilityDistribution
                        yield self.env.timeout(self.duration_distribution.value())

                    # Upbdate loan amount (in case other processes in parallel)
                    entity.sba_amount = min(self.max_loan, (
                                            entity.property.damage_value
                                            - entity.claim_amount
                                            - entity.fema_amount
                                        ) )

                    print(entity.sba_amount <= 0)
                    if entity.sba_amount <= 0:
                        self.writeWithdraw(entity, 'SBA')
                        return

                    yield self.budget.get(entity.sba_amount - 25000)
                    
                    yield entity.recovery_funds.put(entity.sba_amount - 25000)

                    self.writeSecondDisbursement(entity)

                else:
                    # Add loan amount to entity's money to rebuild.
                    yield entity.recovery_funds.put(entity.sba_amount)

                    self.writeOnlyDisbursement(entity)

                # Record time full loan is approved.
                entity.sba_get = self.env.now

        # Handle any interrupt from another process.
        except Interrupt as i:
            self.writeGaveUp(entity, 'SBA')

        if callbacks is not None:
            yield self.env.process(callbacks)
        else:
            pass

    def writeDeadline(self, entity):
        if entity.write_story:
            entity.story.append(
                '{0} applied for a ${1:,.0f} SBA loan {2} days after the event. Their application was rejected because it was submitted after the {3}-day deadline after the disaster declaration made on day {4}. '.format(
                    entity.name.title(), entity.sba_amount, entity.sba_put, self.deadline, self.declaration_duration)
                )
                
    def writeApplied(self, entity):
        if entity.write_story:
            entity.story.append(
                '{0} applied for a ${1:,.0f} SBA loan {2} days after the event and {3} days after a disaster was declared'.format(
                    entity.name.title(), entity.sba_amount, entity.sba_put, (entity.sba_put - self.declaration_duration))
                )
    
    def writeDeniedCredit(self, entity):
        if entity.write_story:
            entity.story.append(
                '{0}\'s SBA loan application was denied because {0} had a credit score of {1}. '.format(
                    entity.name.title(), entity.credit)
                                )
    
    def writeInspected(self, entity):
        if entity.write_story:
            entity.story.append(
                "SBA inspected {0}\'s home on day {1} after the event. "
                .format(entity.name.title(), self.env.now))
    
    def writeApproved(self, entity):
        if entity.write_story:
            entity.story.append(
            "SBA provisionally approved {0} for a ${1:,.0f} loan {2:.0f} days after the event. "
            .format(entity.name.title(), entity.sba_amount, self.env.now))
    
    def writeFirstDisbursement(self, entity):
        if entity.write_story:
            entity.story.append(
                "{0} received an initial SBA loan disbursement of $25,000 {1} days after the event. "
                .format(entity.name.title(), self.env.now))
    
    def writeSecondDisbursement(self, entity):
            if entity.write_story:
                entity.story.append(
                    "{0} received a second SBA loan disbursement of {1:,.0f} {2} days after the event. "
                    .format(entity.name.title(), (entity.sba_amount - 25000), self.env.now))
    
    def writeOnlyDisbursement(self, entity):
        if entity.write_story:
            entity.story.append(
                "{0} received a SBA loan disbursement of ${1:,.0f} {2} days after the event. "
                .format(entity.name.title(), entity.sba_amount, self.env.now))
