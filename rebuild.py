# -*- coding: utf-8 -*-
"""
Created on Mon Jan 25 16:09:02 2016

@author: Derek

processes related to rebuilding
"""

def rebuild_house(entity, simulation, contractors):
        with contractors.request() as request:
            # Put in request for contractors to repair house
            entity.house_put = simulation.now
            yield request

            # Time required to rebuild house
            yield simulation.timeout(entity.rebuild_time)

            # Record time when household gets house
            entity.house_get = simulation.now

        # Write the household's story
        entity.story.append(
            'The house was rebuilt {0} days after the quake, taking {1} days to rebuild. '.format(
            entity.house_get, entity.rebuild_time))
