# -*- coding: utf-8 -*-
"""


@author: Derek Huling, Scott Miles
"""
from simpy import Resource, Container
from scipy.stats import uniform, beta, weibull_min

class ProcessDuration(object):
    def __init__(self, dist='scalar', loc=0.0, scale=None, shape_a=None, shape_b=None):
        self.dist = dist
        self.loc = loc
        self.scale = scale
        self.shape_a = shape_a
        self.shape_b = shape_b

class RecoveryProgram(object):
    def __init__(self, simulation, duration, staff=float('inf'), budget=float('inf')):
        self.simulation = simulation
        self.staff = Resource(self.simulation, capacity=staff)
        self.budget = Container(self.simulation, init=budget)
        
        try:
            if duration.dist == "scalar":
                self.duration = lambda : duration.loc
            elif duration.dist == "uniform":
                self.duration = lambda : uniform.rvs(loc=duration.loc, 
                                                        scale=duration.scale)
            elif duration.dist == "beta":
                self.duration = lambda : beta.rvs(a=duration.shape_a, 
                                                    b=duration.shape_b, 
                                                    loc=duration.loc, 
                                                    scale=duration.scale) 
            elif duration.dist == "weibull":
                self.duration = lambda : weibull_min.rvs(c=duration.shape_a, 
                                                    loc=duration.loc, 
                                                    scale=duration.scale)
            else:
                raise ValueError("Task distibution type not specified or supported.")
                return 
        except TypeError as te:  
            print("Task distribution object not specified: ", te)
            return    
    
    def process(self, entity = None, write_story = False):
          
        # Request staff
        staff_request = self.staff.request()
        yield staff_request
    
        # Yield timeout equivalent to program's process duration
        yield self.simulation.timeout(self.duration())
    
        # Release release staff after process duation is complete.
        self.staff.release(staff_request) 
        
        cost = 1

        # Get out amount equal to cost.
        yield self.budget.get(cost)

        # Put back amount equal to cost.
        yield self.budget.put(cost)

        #If true, write process outcome to story
        if write_story == True and entity != None:  
            entity.story.append("{0} process completed for {1} after {2} days, leaving a program budget of ${3:,.0f}. ".format(
                                self.__class__, entity.name.title(), self.simulation.now, self.budget.level
                                                                                        )
                                )
                                
