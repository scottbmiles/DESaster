# -*- coding: utf-8 -*-
"""
Created on Sun Dec 20 09:43:51 2015

@authors: geomando, dhuling

Dependencies: pandas 17+, SimPy 3+, numpy
"""

import simpy
import numpy
from numpy.random import normal, random_integers
import pandas as pd

class Household:

    def __init__(self, household):
        # Time paramaters
        self.response_time = 14           # Initial wait time before inspection is requested
        self.inspection_time = 1           # Time it takes to inspect a house
        self.claim_time = 90       # Time it takes to process insurance claim
        self.assistance_time = 120             # Time required for FEMA to process assistance request
        self.rebuild_time = 60         # Time required to rebuild house

        # Inputs
        self.name = household['name']                     # Name assigned to household
        self.damaged = household['damaged']               # House damaged [True|False]
        self.damage_value = household['damage_value']     # Amount needed to rebuild home/repair damage
        self.savings = household['savings']               # Pre-event household savings
        self.insurance_coverage = household['insurance_coverage']  # Amount of earthquake insurance coverage

        #Outputs
        self.story = []                  # The story of events for each household
        self.inspection_put = 0           # Time that house inspection occurred
        self.inspection_get = 0           # Time that house inspection occurred
        self.claim_put = 0                 # Start time for insurance claim processing
        self.claim_get = 0                  # Stop time for insurance claim processing
        self.claim_payout = 0            # Amount of insurance claim payout
        self.assistance_put = 0                 # Time FEMA assistance request is put in
        self.assistance_get = 0                  # Time FEMA assistance is received
        self.assistance_request = 0                    # Amount of money requested from FEMA
        self.assistance_payout = 0             # Amount of assistance provided by FEMA
        self.house_put = 0             # Start time for house rebuild
        self.house_get = 0              # Stope time for house rebuild
        self.money_to_rebuild = 0            # Total funds available to household to rebuild house

    # This is the first household process called -- the hazard has occurred,
    # damage may have occurred requiring inspection
    def simulate(self, simulation, resources):

        # Write the household's story
        self.story.append(
            '{0} started with ${1} in savings. '.format(self.name, self.savings))

        # Lag before inspection is requested
        yield simulation.timeout(self.response_time)

        # Request inspection process
        yield simulation.process(self.request_inspection(simulation, resources))

    # House inspection process
    # Called by simulate()) process
    def request_inspection(self, simulation, resources):

        with resources['durable'].category['inspectors'].request() as request:

            # Put in request for an inspector (shared resource)
            self.inspection_put = simulation.now
            yield request

            # Duration of inspection
            yield simulation.timeout(self.inspection_time)

            # The time that the inspection has been completed
            self.inspection_get = simulation.now

        # Write their story
        self.story.append(
            'The house was inspected {0} days after the earthquake. '.format(
            self.response_time))

        # If house is not damaged, household exits simulation
        # Otherwise household starts process(es) to find money to rebuild house
        if self.damaged == 1:

            # Write the household's story
            self.story.append(
            'It suffered ${1} of damage. '.format(
            self.name, self.damage_value))

            #When inspection is done check to see if household can rebuild with their savings
            #Otherwise check to see if they have insurance.
            self.money_to_rebuild = self.savings
            if self.money_to_rebuild >= self.damage_value:

                # Write the household's story
                self.story.append(
                    '{0} had enough savings to rebuild the house. '.format(
                    self.name))

                yield simulation.process(self.rebuild_house(simulation, resources))

            else:
                # If has insurance coverage then file a claim
                if self.insurance_coverage > 0:
                    # Write the household's story
                    self.story.append(
                        '{0} had a ${1} insurance policy and filed a claim. '.format(
                        self.name, self.insurance_coverage))

                    yield simulation.process(self.file_insurance_claim(simulation, resources))

                # If does not have insurance coverage request FEMA indivdidual assistance
                else:
                    # Write the household's story
                    self.story.append(
                        '{0} had no insurance and so did not file a claim. '.format(
                        self.name))

                    yield simulation.process(self.request_fema_assistance(simulation, resources))

        else:
            # Write the household's story
            self.story.append(
                '{0}\'s house did not suffer any damage. '.format(
                self.name))

            yield simulation.exit()

    # Process for filing insurance claim (currently assume that all households have insurance)
    # Called by request_inspection() process
    def file_insurance_claim(self, simulation, resources):
        with resources['durable'].category['claim adjusters'].request() as request:
            # Record time that claim is put in
            self.claim_put = simulation.now
            yield request

            # Duration of claim processing
            yield simulation.timeout(self.claim_time)

            # Amount of insurance claim payout
            self.claim_payout = self.insurance_coverage  ### <-- Has thrown "None not a generator" exception

            # Record when the time when household gets claim payout
            self.claim_get = simulation.now

        # If insurance payout exceed damage repair value, there is enough money to rebuild house
        # Otherwise request FEMA assistance
        self.money_to_rebuild = self.savings + self.claim_payout

        if self.money_to_rebuild >= self.damage_value:

            # Write the household's story
            self.story.append(
                '{0} received a ${1} insurance payout after a {2} day wait and had enough to rebuild. '.format(
                self.name, self.claim_payout, self.claim_time))

            yield simulation.process(self.rebuild_house(simulation, resources))

        else:

            # Write the household's story
            self.story.append(
                '{0} received a ${1} insurance payout but still needed FEMA assistance. '.format(
                self.name, self.claim_payout))
            self.story.append(
                'It took {0} days to process the claim. '.format(
                self.claim_time)
            )

            yield simulation.process(self.request_fema_assistance(simulation, resources))

    # Submit request for FEMA individual assistance
    def request_fema_assistance(self, simulation, resources):

        # To process assistance request must request and wait for a FEMA application processor
        with resources['durable'].category['fema processors'].request() as request:
            # Put in request for FEMA individual assistance; record time requested
            self.assistance_put = simulation.now
            yield request

            # Time required for FEMA to process assistance request
            yield simulation.timeout(self.assistance_time)

            # Record time household gets FEMA assistance
            self.assistance_get = simulation.now

        # Compute amount of assistance requested from FEMA; if insurance payout covers repair cost it is zero
        self.assistance_request = self.damage_value - self.claim_payout

        # If requesting assistance, determine if FEMA has money left to provide assistance
        if self.assistance_request > 0:
            if self.assistance_request <= resources['nondurable'].category['fema assistance'].level:

                self.assistance_payout = self.assistance_request

                # Write the household's story
                self.story.append(
                    '{0} received ${1} from FEMA after a {2} day wait. '.format(
                    self.name, self.assistance_payout, self.assistance_time))

                yield resources['nondurable'].category['fema assistance'].get(self.assistance_request)

            else:
                if resources['nondurable'].category['fema assistance'].level > 0:

                    self.assistance_payout = resources['nondurable'].category['fema assistance'].level

                    # Write the household's story
                    self.story.append(
                        '{0} requested ${1} from FEMA but only received ${2}. '.format(
                        self.name, self.assistance_request, self.assistance_payout))
                    self.story.append(
                        'It took {0} days for FEMA to provide the assistance. '.format(
                        self.assistance_time))

                    yield resources['nondurable'].category['fema assistance'].get(resources['nondurable'].category['fema assistance'].level)

                else:
                    self.assistance_payout = 0

                    # Write the household's story
                    self.story.append(
                        '{0} received no money from FEMA because of inadequate funding. '.format(
                        self.name))

        else:
            self.assistance_payout = 0

            # Write the household's story
            self.story.append(
                '{0} did not need FEMA assistance. '.format(
                self.name))

        # After receiving what FEMA assistance is available, calculate how much money is available to rebuild house
        # If damage repair value is less than money available to rebuild, the household rebuilds their house
        self.money_to_rebuild = self.savings + self.claim_payout + self.assistance_payout

        if self.damage_value <= self.money_to_rebuild:

            # Write the household's story
            self.story.append(
                'With the addition of FEMA assistance {0} had enough to rebuild. '.format(
                self.name))

            yield simulation.process(self.rebuild_house(simulation, resources))

        else:
            self.house_put = -9
            self.house_get = -9

            # Write the household's story
            self.story.append(
                '{0} did not have enough money to rebuild. '.format(
                self.name))

    def rebuild_house(self, simulation, resources):
            with resources['durable'].category['contractors'].request() as request:
                # Put in request for contractors to repair house
                self.house_put = simulation.now
                yield request

                # Time required to rebuild house
                yield simulation.timeout(self.rebuild_time)

                # Record time when household gets house
                self.house_get = simulation.now

            # Write the household's story
            self.story.append(
                'The house was rebuilt {0} days after the quake, taking {1} days to rebuild. '.format(
                self.house_get, self.rebuild_time))