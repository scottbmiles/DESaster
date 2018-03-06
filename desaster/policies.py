# -*- coding: utf-8 -*-
"""
Copyright (C) 2018  Scott B. Miles, milessb@uw.edu, scott.miles@resilscience.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
    
Module of classes that implement compound policies for custom arrangements of
DESaster recovery programs.

Classes:
FinancialRecoveryPolicy
Insurance_IA_SBA_Sequential
Insurance_IA_SBA_Parallel
Insurance_SBA_Sequential
Insurance_SBA_Parallel
RepairVacantBuilding

@author: Scott Miles (milessb@uw.edu)
"""
import random
random.seed(15)
from desaster.entities import Owner


class FinancialRecoveryPolicy(object):
    """Base class for creating financial recovery policies. Serves to make
    pretty UML diagrams using pyreverse. And contains some story writing methods.
    
    Methods:
    __init__(self, env):
    policy(self):
    writeHadEnough(self, entity):
    writeCompletedWithoutEnough(self, entity, search_duration):
    writeCompletedWithEnough(self, entity, search_duration):
    
    """
    def __init__(self, env):
        """ Initiate FinancialRecoveryPolicy object.
        
        Keyword Arguments:
        self.env -- The associated simpy.Environment
        """
        self.env = env
    def policy(self):
        pass
        
    def writeHadEnough(self, entity):
        if entity.write_story:
            entity.story.append(
                '{0} already had enough money to repair (${1:,.0f}) and did not seek assistance. '.format(
                                    entity.name.title(), entity.recovery_funds.level)
                                )
        
    def writeCompletedWithoutEnough(self, entity, search_duration):
        if entity.write_story:
            entity.story.append(
                'It took {0} {1:.0f} days to exhaust financial assistance options but still does not have enough money to cover repairs (${2:,.0f}). '.format(
                        entity.name.title(), search_duration, entity.recovery_funds.level)
                )
                
    def writeCompletedWithEnough(self, entity, search_duration):
        if entity.write_story:
            entity.story.append(
                'It took {0} {1:.0f} days to exhaust financial assistance options and now has ${2:,.0f} for repairs. '.format(
                        entity.name.title(), search_duration, entity.recovery_funds.level)
                )

class Insurance_IA_SBA_Sequential(FinancialRecoveryPolicy):
    """ A class that organizes funding requests to insurance, FEMA, and SBA in 
    sequential order. Also implements patience for waiting for funding.
    
    Methods:
    __init__
    policy

    Inheritance:
    FinancialRecoveryPolicy
    """
    def __init__(self, env):
        """ Initiate Insurance_IA_SBA_Sequential object.
        
        Keyword Arguments:
        self.env -- The associated simpy.Environment
        """
        FinancialRecoveryPolicy.__init__(self, env)
    
    def policy(self, insurance_program, fema_program, sba_program, entity,
                        search_patience):
        """A process (generator) representing entity search for money to repair
        home based on requests for insurance and/or FEMA aid and/or loan.
        
        Keyword Arguments:
        insurance_program -- A OwnersInsurance object.
        fema_program -- A HousingAssistanceFEMA object.
        sba_program -- A RealPropertyLoanSBA object.
        entity -- A single entities object, such as Household().
        search_patience -- The search duration in which the entity is willing to
                            wait to find a new home. Does not include the process of
                            securing money.
        write_story -- Boolean indicating whether to track a entitys story.

        Returns or Attribute Changes:
        entity.story -- Process outcomes appended to story.
        money_search_start -- Record time money search starts
        entity.gave_up_funding_search -- Record time money search stops
        entity.recovery_funds.level -- Increase recovery funds amount in $
        """
        # Calculate the time that money search patience ends
        # patience_end = money_search_start + search_patience

        # Return out of function if entity has enough money to repair and does not
        # have any insurance coverage.
        if (entity.recovery_funds.level >= entity.property.damage_value
            and entity.insurance == 0.0):

            self.writeHadEnough(entity)
            return

        # If entity has insurance then yield an insurance claim request, the duration
        # of which is limited by entity's money search patience.
        if entity.insurance > 0.0:
            # Record when money search starts
            money_search_start = self.env.now
            patience_end = money_search_start + search_patience
            patience_remain = patience_end - self.env.now
            
            # Define a timeout process to represent search patience, with duration
            # equal to the *remaining* patience. Pass the value "Gave up" if the
            # process completes.
            find_search_patience = self.env.timeout(patience_remain, value='Gave up')

            # Define insurance claim request process. Pass data about available
            # insurance claim adjusters.
            try_insurance = self.env.process(insurance_program.process(entity))

            # Yield both the patience timeout and the insurance claim request.
            # Pass result for the process that completes first.
            money_search_outcome = yield find_search_patience | try_insurance
            
            # If patience process completes first, interrupt the insurance claim
            # request and return out of function.
            if money_search_outcome == {find_search_patience: 'Gave up'}:
                if try_insurance.is_alive:
                    try_insurance.interrupt(self.env.now)
                entity.gave_up_funding_search = self.env.now
                return
                
            patience_remain = patience_end - self.env.now

        # If entity (still) does not have enough repair money then yield a FEMA IA
        # request, the duration of which is limited by entity's money search patience.
        if entity.recovery_funds.level < entity.property.damage_value:
            # Define a timeout process to represent search patience, with duration
            # equal to the *remaining* patience. Pass the value "Gave up" if the
            # process completes.
            if entity.insurance > 0.0:
                # If has insurance, account for time it took to get claim
                find_search_patience = self.env.timeout(patience_remain, value='gave up')
            else:
                #If no insurance, money search starts after disaster declaration
                money_search_start = max(fema_program.declaration, self.env.now)
                patience_end = money_search_start + search_patience
                patience_remain = patience_end - self.env.now
                
                find_search_patience = self.env.timeout(patience_remain,
                                                        value='gave up'
                                                        )
            
            # Define FEMA aid request process. Pass data about available
            # FEMA processors, budget, and maximum grant amount.
            try_fema = self.env.process(fema_program.process(entity))
            
            # Yield both the patience timeout and the FEMA aid request.
            # Pass result for the process that completes first.
            money_search_outcome = yield find_search_patience | try_fema
            
            # If patience process completes first, interrupt the FEMA aid
            # request and return out of function.
            if 'gave up' in str(money_search_outcome).lower():
                if try_fema.is_alive:
                    try_fema.interrupt(self.env.now)
                entity.gave_up_funding_search = self.env.now
                return

            patience_remain = patience_end - self.env.now
            
        # If entity (still) does not have enough repair money then yield a loan
        # request, the duration of which is limited by entity's money search patience.
        if entity.recovery_funds.level < entity.property.damage_value:
            # Define a timeout process to represent search patience, with duration
            # equal to the *remaining* patience. Pass the value "gave up" if the
            # process completes.
            find_search_patience = self.env.timeout(patience_remain, value='gave up')

            # Define loan request process. Pass data about available
            # loan processors.
            try_loan = self.env.process(sba_program.process(entity))

            # Yield both the patience timeout and the loan request.
            # Pass result for the process that completes first.
            money_search_outcome = yield find_search_patience | try_loan

            # If patience process completes first, interrupt the loan
            # request and return out of function.
            if 'gave up' in str(money_search_outcome).lower():
                if try_loan.is_alive:
                    try_loan.interrupt(self.env.now)
                entity.gave_up_funding_search = self.env.now
                return

        # Record the time and duration when entity's search for money ends without
        # giving up.
        search_duration = self.env.now - money_search_start

        # If entity (STILL) does not have enough repair money then indicate so and
        # that options have been exhausted.
        if entity.recovery_funds.level < entity.property.damage_value:
            # If write_story is True, then append money search outcome to entity's story.
            self.writeCompletedWithoutEnough(entity, search_duration)
            return

        # If entity completed search and obtained sufficient funding.
        self.writeCompletedWithEnough(entity, search_duration)
                
class Insurance_IA_SBA_Parallel(FinancialRecoveryPolicy):
    """ A class that organizes funding requests to insurance, FEMA, and SBA in 
    parallel. Also implements patience for waiting for funding.

    Methods:
    __init__
    policy

    Inheritance:
    FinancialRecoveryPolicy
    """
    def __init__(self, env):
        """ Initiate Insurance_IA_SBA_Sequential object.
        
        Keyword Arguments:
        self.env -- The associated simpy.Environment
        """
        FinancialRecoveryPolicy.__init__(self, env)
    def policy(self, insurance_program, fema_program, sba_program, entity,
                        search_patience):
        """A process (generator) representing entity search for money to repair or
        repair home based on requests for insurance and/or SBA loan.

        Keyword Arguments:
        insurance_program -- A OwnersInsurance object.
        fema_program -- A HousingAssistanceFEMA object.
        sba_program -- A RealPropertyLoanSBA object.
        entity -- A single entities object, such as Household().
        search_patience -- The search duration in which the entity is willing to
                            wait to find a new home. Does not include the process of
                            securing money.
        write_story -- Boolean indicating whether to track a entitys story.

        Returns or Attribute Changes:
        entity.story -- Process outcomes appended to story.
        money_search_start -- Record time money search starts
        entity.gave_up_funding_search -- Record time money search stops
        entity.recovery_funds.level -- Increase recovery funds amount in $
        """

        # Return out of function if entity has enough money to repair and does not
        # have any insurance coverage.
        if (entity.recovery_funds.level >= entity.property.damage_value
            and entity.insurance == 0):

            self.writeHadEnough(entity)
            return
        
        # Define insurance claim request process. Define loan request process.
        try_insurance = self.env.process(insurance_program.process(entity))
        try_loan = self.env.process(sba_program.process(entity))
        try_fema = self.env.process(fema_program.process(entity))

        # If entity has insurance then yield an insurance claim request, the duration
        # of which is limited by entity's money search patience.
        if entity.insurance > 0.0:
            # Define a timeout process to represent search patience. Pass the value
            # "gave up" if the process completes.
            find_search_patience = self.env.timeout(search_patience, value='gave up')
            
            # Record when money search starts, if don't have insurance
            money_search_start = self.env.now
            
            # At any point the entity has enough money to repair, stop looking.
            while entity.recovery_funds.level < entity.property.damage_value:
                
                # Yield the patience timeout, the FEMA request, insurance claim request, and the loan request.
                money_search_outcome = yield find_search_patience | ( try_insurance & try_loan & try_fema )
    
                # End looping if all recovery processes have completed.
                if try_insurance.processed and try_loan.processed and try_fema.processed:
                    break

                # If patience process completes first, interrupt the insurance, FEMA,
                # and SBA processes.
                if 'gave up' in str(money_search_outcome).lower():
                    if try_insurance.is_alive:
                        try_insurance.interrupt(self.env.now)
                    if try_fema.is_alive:
                            try_fema.interrupt(self.env.now)
                    if try_loan.is_alive:
                        try_loan.interrupt(self.env.now)
                    entity.gave_up_funding_search = self.env.now
                    return
        else:
            # If no insurance, money search starts after disaster declaration
            # Need to check current simulation time again when disaster declaration
            # occurs to determine how much patience remains
            money_search_start = max(fema_program.declaration, self.env.now)
            patience_end = money_search_start + search_patience
            patience_remain = patience_end - self.env.now
            
            # Define a timeout process to represent search patience. Pass the value
            # "gave up" if the process completes.
            find_search_patience = self.env.timeout(patience_remain, value='gave up')
            
            # At any point the entity has enough money to repair, stop looking.
            while entity.recovery_funds.level < entity.property.damage_value:
                # Yield the patience timeout and the loan request.
                # No insurance so just yield FEMA & SBA loan request process.
                money_search_outcome = yield find_search_patience | (try_loan & try_fema)
                
                # End looping if both recovery processes have completed
                if try_loan.processed and try_fema.processed:
                    break

                # If patience process completes first, interrupt the insurance claim
                # request and the loan request before ending process.
                if 'gave up' in str(money_search_outcome).lower():
                    if try_loan.is_alive:
                        try_loan.interrupt(self.env.now)
                    if try_fema.is_alive:
                        try_fema.interrupt(self.env.now)
                    entity.gave_up_funding_search = self.env.now
                    return

        # Record the duration when entity's search for money ends without
        # giving up.
        search_duration = self.env.now - money_search_start

        # If entity (STILL) does not have enough repair money then indicate so and
        # that options have been exhausted.
        if entity.recovery_funds.level < entity.property.damage_value:
            self.writeCompletedWithoutEnough(entity, search_duration)
            return

        # If entity completed search and obtained sufficient funding.
        self.writeCompletedWithEnough(entity, search_duration)

class Insurance_SBA_Sequential(FinancialRecoveryPolicy):
    """ A class that organizes funding requests to insurance and SBA in 
    sequential order. Also implements patience for waiting for funding.

    Methods:
    __init__
    policy

    Inheritance:
    FinancialRecoveryPolicy
    """
    def __init__(self, env):
        FinancialRecoveryPolicy.__init__(self, env)
        """ Initiate Insurance_IA_SBA_Sequential object.
        
        Keyword Arguments:
        self.env -- The associated simpy.Environment
        """
    def policy(self, insurance_program, sba_program, entity,
                        search_patience):
        """A process (generator) representing entity search for money to repair or
        repair home based on requests for insurance, FEMA IA, and/or SBA loan.
        Funding requests are done in sequential order.

        env -- Pointer to SimPy env environment.
        entity -- A single entities object, such as Household().
        search_patience -- The search duration in which the entity is willing to
                            wait to find a new home. Does not include the process of
        write_story -- Boolean indicating whether to track a entitys story.

        Keyword Arguments:
        insurance_program -- A OwnersInsurance object.
        fema_program -- A HousingAssistanceFEMA object.
        sba_program -- A RealPropertyLoanSBA object.
        entity -- A single entities object, such as Household().
        search_patience -- The search duration in which the entity is willing to
                            wait to find a new home. Does not include the process of
                            securing money.
        write_story -- Boolean indicating whether to track a entitys story.

        Returns or Attribute Changes:
        entity.story -- Process outcomes appended to story.
        money_search_start -- Record time money search starts
        entity.gave_up_funding_search -- Record time money search stops
        entity.recovery_funds.level -- Increase recovery funds amount in $
        """
        # Return out of function if entity has enough money to repair and does not
        # have any insurance coverage.
        if (entity.recovery_funds.level >= entity.property.damage_value
            and entity.insurance == 0.0):

            self.writeHadEnough(entity)
            return

        # If entity has insurance then yield an insurance claim request, the duration
        # of which is limited by entity's money search patience.
        if entity.insurance > 0.0:

            # Record when money search starts
            money_search_start = self.env.now
            patience_end = money_search_start + search_patience
            patience_remain = patience_end - self.env.now
            
            # Define a timeout process to represent search patience, with duration
            # equal to the *remaining* patience. Pass the value "gave up" if the
            # process completes.
            find_search_patience = self.env.timeout(patience_remain, value='gave up')

            # Define insurance claim request process. Pass data about available
            # insurance claim adjusters.
            try_insurance = self.env.process(insurance_program.process(entity))

            # Yield both the patience timeout and the insurance claim request.
            # Pass result for the process that completes first.
            money_search_outcome = yield find_search_patience | try_insurance

            # Record when money search starts
            money_search_start = entity.claim_put
            
            # If patience process completes first, interrupt the insurance claim
            # request and return out of function.
            if 'gave up' in str(money_search_outcome).lower():
                if try_insurance.is_alive:
                    try_insurance.interrupt(self.env.now)
                entity.gave_up_funding_search = self.env.now
                return

            patience_remain = patience_end - self.env.now
            
        # If entity (still) does not have enough repair money then yield a loan
        # request, the duration of which is limited by entity's money search patience.
        if entity.recovery_funds.level < entity.property.damage_value:

            # Define a timeout process to represent search patience, with duration
            # equal to the *remaining* patience. Pass the value "Gave up" if the
            # process completes.
            if entity.insurance > 0.0:
                # If has insurance, account for time it took to get claim
                find_search_patience = self.env.timeout(patience_remain, value='gave up')
            else:
                # If no insurance, money search starts after disaster declaration
                # Need to check current simulation time again when disaster declaration
                # occurs to determine how much patience remains
                money_search_start = max(sba_program.declaration, self.env.now)
                patience_end = money_search_start + search_patience
                patience_remain = patience_end - self.env.now
                
                find_search_patience = self.env.timeout(patience_remain, value='gave up')
            
            # Define loan request process. Pass data about available
            # loan processors.
            try_loan = self.env.process(sba_program.process(entity))

            # Yield both the patience timeout and the loan request.
            # Pass result for the process that completes first.
            money_search_outcome = yield find_search_patience | try_loan

            # If patience process completes first, interrupt the loan
            # request and return out of function.
            if 'gave up' in str(money_search_outcome).lower():
                if try_loan.is_alive:
                    try_loan.interrupt(self.env.now)
                entity.gave_up_funding_search = self.env.now
                return

        # Record the duration when entity's search for money ends without
        # giving up.
        search_duration = self.env.now - money_search_start

        # If entity (STILL) does not have enough repair money then indicate so and
        # that options have been exhausted.
        if entity.recovery_funds.level < entity.property.damage_value:
            self.writeCompletedWithoutEnough(entity, search_duration)
            return

        # If entity completed search and obtained sufficient funding.
        self.writeCompletedWithEnough(entity, search_duration)

class Insurance_FirstThen_IA_SBA_Parallel(FinancialRecoveryPolicy):
    """ A class that organizes funding requests to insurance, FEMA, and SBA. 
    FEMA and SBA programs run in parallel but only *after* insurance claim has 
    been processed (if has insurance). 
    Also implements patience for waiting for funding.

    Methods:
    __init__
    policy

    Inheritance:
    FinancialRecoveryPolicy
    """
    def __init__(self, env):
        """ Initiate Insurance_IA_SBA_Sequential object.
        
        Keyword Arguments:
        self.env -- The associated simpy.Environment
        """
        FinancialRecoveryPolicy.__init__(self, env)
    def policy(self, insurance_program, fema_program, sba_program, entity,
                        search_patience):
        """A process (generator) representing entity search for money to repair or
        repair home based on requests for insurance, FEMA IA, and/or SBA loan.
        Insurance processed first and then the other two programs in parallel.

        Keyword Arguments:
        insurance_program -- A OwnersInsurance object.
        fema_program -- A HousingAssistanceFEMA object.
        sba_program -- A RealPropertyLoanSBA object.
        entity -- A single entities object, such as Household().
        search_patience -- The search duration in which the entity is willing to
                            wait to find a new home. Does not include the process of
                            securing money.
        write_story -- Boolean indicating whether to track a entitys story.

        Returns or Attribute Changes:
        entity.story -- Process outcomes appended to story.
        money_search_start -- Record time money search starts
        entity.gave_up_funding_search -- Record time money search stops
        entity.recovery_funds.level -- Increase recovery funds amount in $
        """

        # Return out of function if entity has enough money to repair and does not
        # have any insurance coverage.
        if (entity.recovery_funds.level >= entity.property.damage_value
            and entity.insurance == 0):

            self.writeHadEnough(entity)
            return
        
        # Define insurance claim request process. Define loan request process.
        try_insurance = self.env.process(insurance_program.process(entity))
        try_loan = self.env.process(sba_program.process(entity))
        try_fema = self.env.process(fema_program.process(entity))

        # If entity has insurance then yield an insurance claim request, the duration
        # of which is limited by entity's money search patience.
        if entity.insurance > 0.0:

            
            # At any point the entity has enough money to repair, stop looking.
            while entity.recovery_funds.level < entity.property.damage_value:
                # Record when money search starts 
                money_search_start = self.env.now
                
                # Set patience parameters
                patience_end = money_search_start + search_patience
                patience_remain = patience_end - self.env.now

                # Define a timeout process to represent search patience, with duration
                # equal to the *remaining* patience. Pass the value "gave up" if the
                # process completes.
                find_search_patience = self.env.timeout(patience_remain, value='gave up')

                # Define insurance claim request process. Pass data about available
                # insurance claim adjusters.
                try_insurance = self.env.process(insurance_program.process(entity))

                # Yield both the patience timeout and the insurance claim request.
                # Pass result for the process that completes first.
                money_search_outcome = yield find_search_patience | try_insurance
                
                # If patience process completes first, interrupt the insurance claim
                # request and return out of function.
                if 'gave up' in str(money_search_outcome).lower():
                    if try_insurance.is_alive:
                        try_insurance.interrupt(self.env.now)
                    entity.gave_up_funding_search = self.env.now
                    return

                # Calculate remaining patience and reset patience timeout to
                # wait for FEMA and SBA processes to complete
                patience_remain = patience_end - self.env.now
                find_search_patience = self.env.timeout(patience_remain, value='gave up')
                
                # After insurance claim process has completed, can start FEMA and SBA process
                # Yield the patience timeout, the FEMA request and the SBA request.
                money_search_outcome = yield find_search_patience | (try_loan & try_fema)
    
                # End looping if FEMA and SBA processes have completed.
                if try_loan.processed and try_fema.processed:
                    break

                # If patience process completes first, interrupt the FEMA
                # and SBA processes.
                if 'gave up' in str(money_search_outcome).lower():
                    if try_fema.is_alive:
                            try_fema.interrupt(self.env.now)
                    if try_loan.is_alive:
                        try_loan.interrupt(self.env.now)
                    entity.gave_up_funding_search = self.env.now
                    return
        else:
            # If no insurance, money search starts after disaster declaration
            # Need to check current simulation time again when disaster declaration
            # occurs to determine how much patience remains
            money_search_start = max(fema_program.declaration, self.env.now)
            patience_end = money_search_start + search_patience
            patience_remain = patience_end - self.env.now
            
            # Define a timeout process to represent search patience. Pass the value
            # "gave up" if the process completes.
            find_search_patience = self.env.timeout(patience_remain, value='gave up')
            
            # At any point the entity has enough money to repair, stop looking.
            while entity.recovery_funds.level < entity.property.damage_value:
                # Yield the patience timeout and the loan request.
                # No insurance so just yield FEMA & SBA loan request process.
                money_search_outcome = yield find_search_patience | (try_loan & try_fema)
                
                # End looping if both recovery processes have completed
                if try_loan.processed and try_fema.processed:
                    break

                # If patience process completes first, interrupt the insurance claim
                # request and the loan request before ending process.
                if 'gave up' in str(money_search_outcome).lower():
                    if try_loan.is_alive:
                        try_loan.interrupt(self.env.now)
                    if try_fema.is_alive:
                        try_fema.interrupt(self.env.now)
                    entity.gave_up_funding_search = self.env.now
                    return

        # Record the duration when entity's search for money ends without
        # giving up.
        search_duration = self.env.now - money_search_start

        # If entity (STILL) does not have enough repair money then indicate so and
        # that options have been exhausted.
        if entity.recovery_funds.level < entity.property.damage_value:
            self.writeCompletedWithoutEnough(entity, search_duration)
            return

        # If entity completed search and obtained sufficient funding.
        self.writeCompletedWithEnough(entity, search_duration)

class Insurance_SBA_Parallel(FinancialRecoveryPolicy):
    """ A class that organizes funding requests to insurance and SBA in 
    parallel. Also implements patience for waiting for funding.

    Methods:
    __init__
    policy

    Inheritance:
    FinancialRecoveryPolicy
    """
    def __init__(self, env):
        FinancialRecoveryPolicy.__init__(self, env)
        """ Initiate Insurance_IA_SBA_Sequential object.
        
        Keyword Arguments:
        self.env -- The associated simpy.Environment
        """
    def policy(self, insurance_program, sba_program, entity,
                        search_patience):
        """A process (generator) representing entity search for money to repair or
        repair home based on requests for insurance and/or SBA loan.

        Keyword Arguments:
        insurance_program -- A OwnersInsurance object.
        fema_program -- A HousingAssistanceFEMA object.
        sba_program -- A RealPropertyLoanSBA object.
        entity -- A single entities object, such as Household().
        search_patience -- The search duration in which the entity is willing to
                            wait to find a new home. Does not include the process of
                            securing money.
        write_story -- Boolean indicating whether to track a entitys story.

        Returns or Attribute Changes:
        entity.story -- Process outcomes appended to story.
        money_search_start -- Record time money search starts
        entity.gave_up_funding_search -- Record time money search stops
        entity.recovery_funds.level -- Increase recovery funds amount in $
        """

        # Return out of function if entity has enough money to repair and does not
        # have any insurance coverage.
        if (entity.recovery_funds.level >= entity.property.damage_value
            and entity.insurance == 0.0):

            self.writeHadEnough(entity)
            return

        # Define insurance claim request process. Define loan request process.
        try_insurance = self.env.process(insurance_program.process(entity))
        try_loan = self.env.process(sba_program.process(entity))

        # If entity has insurance then yield an insurance claim request, the duration
        # of which is limited by entity's money search patience.
        if entity.insurance > 0.0:

            # Define a timeout process to represent search patience. Pass the value
            # "gave up" if the process completes.
            find_search_patience = self.env.timeout(search_patience, value='gave up')
            
            # Record when money search starts, if don't have insurance
            money_search_start = self.env.now
            
            # At any point the entity has enough money to repair, stop looking.
            while entity.recovery_funds.level < entity.property.damage_value:

                # Yield the patience timeout, the insurance claim request, and the loan request.
                # Pass result for the process(es) that completes first.
                money_search_outcome = yield find_search_patience | ( try_insurance & try_loan )

                # Record when money search starts
                money_search_start = entity.claim_put
                
                # End looping if both recovery processes have completed.
                if try_insurance.processed and try_loan.processed:
                    break

                # If patience process completes first, interrupt the insurance claim
                # request and the loan request before ending process.
                if 'gave up' in str(money_search_outcome).lower():
                    if try_insurance.is_alive:
                        try_insurance.interrupt(self.env.now)
                    if try_loan.is_alive:
                        try_loan.interrupt(self.env.now)
                    entity.gave_up_funding_search = self.env.now
                    return
        else:
            # If no insurance, money search starts after disaster declaration
            # Need to check current simulation time again when disaster declaration
            # occurs to determine how much patience remains
            money_search_start = max(sba_program.declaration, self.env.now)
            patience_end = money_search_start + search_patience
            patience_remain = patience_end - self.env.now
            
            # Define a timeout process to represent search patience. Pass the value
            # "gave up" if the process completes.
            find_search_patience = self.env.timeout(patience_remain, value='gave up')
            
            # Yield the patience timeout and the loan request.
            # No insurance so just yield loan request process.
            # Pass result for the process that completes first.
            money_search_outcome = yield find_search_patience | try_loan

            # Record when money search starts, if don't have insurance
            if entity.insurance <= 0.0:
                money_search_start = entity.sba_put
            
            # If patience process completes first, interrupt the insurance claim
            # request and the loan request before ending process.
            if 'gave up' in str(money_search_outcome).lower():
                if try_loan.is_alive:
                    try_loan.interrupt(self.env.now)
                entity.gave_up_funding_search = self.env.now
                return

        # Record the time and duration when entity's search for money ends without
        # giving up.
        search_duration = self.env.now - money_search_start

        # If entity (STILL) does not have enough repair money then indicate so and
        # that options have been exhausted.
        if entity.recovery_funds.level < entity.property.damage_value:

            self.writeCompletedWithoutEnough(entity, search_duration)
            
            return

        # If entity completed search and obtained sufficient funding.
        self.writeCompletedWithEnough(entity, search_duration)

class RepairVacantBuilding(object):
    """ A class to represent a large-scale/bulk policy for expedited repairing
    of a building stock. Conceptually this is intended to repair vacant building
    stocks that do not have entities associated with them to repair them. This bulk
    repairing potentially provides additional homes for entities to purchase or rent.


    Methods:
    __init__(self, env, duration_prob_dist, staff=float('inf'))
    process(self, building_stock, repair_fraction, repair_start)
    """

    def __init__(self, env):
        """Initiate RepairVacantBuilding object.

        Keyword Arguments:
        env -- simpy.Envionment() object

        %%%% Eventually might implement a TechnicalRecoveryPolicy class. %%%
        
        """
    def policy(self, inspection_program, assessment_program, permit_program,
                repair_program, entity, building_stock, repair_probability = 1.0, 
                wait_time = 0.0):
        """Process to do expedited repairs on a vacant/listed buildings based
        on available contractors, specified proportion/probability, and wait time.

        Keyword Arguments:
        inspection_program -- A technical.InspectionProgram object
        assessment_program -- A technical.EngineeringAssessment object
        permit_program -- A technical.PermitProgram object.
        repair_program -- A technical.RepairProgram object.
        entity -- A entities.Owner or subclass that serves as t
        building_stock -- A SimPy FilterStore that contains one or more
           structures.Building() (or subclasses) objects
           objects that represent vacant structures for purchase.
        repair_probability -- A value to set probability of successful repair.
        wait_time -- Duration that simulates time to get recovery assistance.

        Attribute Changes:
        inspection_put 
        inspection_get
        permit_put
        permit_get
        assessment_put
        assessment_get
        repair_put
        repair_get
        damage_value
        damage_state
        """
        
        if entity.property.damage_state != 'None' and entity.property.listed:
            if random.uniform(0, 1.0) > repair_probability:
                return

            get_building = yield building_stock.get(lambda getBuilding:
                                                    getBuilding.__dict__ == entity.property.__dict__
                                                )

            yield self.env.process(inspection_program.process(entity.property, entity))
            yield self.env.timeout(wait_time)
            yield self.env.process(assessment_program.process(entity.property, entity))
            yield self.env.process(permit_program.process(entity.property, entity))
            yield self.env.process(repair_program.process(entity.property, entity))
            yield building_stock.put(get_building)
