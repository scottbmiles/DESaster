# -*- coding: utf-8 -*-
"""
Module of classes and functions for input/output related to DESaster.

Classes:
DurationProbabilityDistribution
random_duration_function
importSingleFamilyResidenceStock

@author: Scott Miles (milessb@uw.edu), Derek Huling
"""
from scipy.stats import uniform, beta, weibull_min

class ProbabilityDistribution(object):
    """A general class to hold parameters for defining different probability
    distibutions for use with io.random_duration_function() to dynamically randomly
    sample a duration for a given process.
    
    Parameter terminology follows the generalized terms from numpy.stats module:
    https://docs.scipy.org/doc/scipy/reference/stats.html#module-scipy.stats
    """
    def __init__(self, dist='scalar', loc=0.0, scale=None, shape_a=None, shape_b=None, shape_c=None):
        """Initiate a robabilityDistribution object.
        
        Parameter terminology follows the generalized terms from numpy.stats module:
        https://docs.scipy.org/doc/scipy/reference/stats.html#module-scipy.stats
        """
        self.dist = dist # String. Name of a probability distribution 
                            # (must be supported by io.random_duration_function())
        self.loc = loc # Float. The location of the distribution (e.g., mean, for Gaussian)
        self.scale = scale # Float. Scale of the distribution. (e.g., distribution range for Uniform)
        self.shape_a = shape_a # Float. Numpy.stats shape parameter "a". (e.g., for Beta)
        self.shape_b = shape_b # Float. Numpy.stats shape parameter "b". (e.g., for Beta)
        self.shape_c = shape_c # Float. Numpy.stats shape parameter "c". (e.g., for Weibull)
        
    def value(self):
        """A function that returns a sampled duration for a given process 
        based on distribution type and parameters specified by inputted i
        o.DurationProbabilityDistribution. Random number generators for different 
        distributions from scipy.stats. 
        
        Supported scipy.stats Distributions:
        scalar (determistic scalar location)
        uniform.rvs
        beta.rvs
        weibull_min.rvs
        
        Returns
        value()
        """
        try:
            if self.dist == "scalar":
                return self.loc
            elif self.dist == "uniform":
                return uniform.rvs(loc = self.loc, scale = self.scale)
            elif self.dist == "beta":
                return beta.rvs(a = self.shape_a, b = self.shape_b,loc = self.loc,scale = self.scale)
            elif self.dist == "weibull":
                return weibull_min.rvs(c = self.shape_c,loc = self.loc,scale = self.scale)
            else:
                raise ValueError("Probability distibution type not specified or supported.")
                return
        except TypeError as te:
            print("Duration probability distribution not specified: ", te)
            return
            

class DurationDistributionHomeLoanSBA(ProbabilityDistribution):
    """
    
    Parameter terminology follows the generalized terms from numpy.stats module:
    https://docs.scipy.org/doc/scipy/reference/stats.html#module-scipy.stats
    """
    def __init__(self, dist='beta', loc=15.0, scale=30.0, shape_a=2.0, shape_b=2.0, loc_delta_credit=15.0):
        
        ProbabilityDistribution.__init__(self, dist, loc, scale, shape_a, shape_b)
        
        self.loc_delta_credit = loc_delta_credit
        
    def value(self, credit, min_credit):
        
        try:
            if credit >= min_credit:
                if self.dist == "scalar":
                    return self.loc
                elif self.dist == "uniform":
                    return uniform.rvs(loc = self.loc, scale = self.scale)
                elif self.dist == "beta":
                    return beta.rvs(a = self.shape_a, b = self.shape_b,
                                    loc = self.loc, scale = self.scale)
                elif self.dist == "weibull":
                    return weibull_min.rvs(c = self.shape_c,loc = self.loc,scale = self.scale)
                else:
                    raise ValueError("Probability distibution type not specified or supported.")
                    return
            else:
                if self.dist == "scalar":
                    return self.loc + self.loc_credit_delta
                elif self.dist == "uniform":
                    return uniform.rvs(loc = self.loc + self.loc_credit_delta,
                                        scale = self.scale)
                elif self.dist == "beta":
                    return beta.rvs(a = self.shape_a, b = self.shape_b,
                                    loc = self.loc + self.loc_delta_credit,
                                    scale = self.scale)
                elif self.dist == "weibull":
                    return weibull_min.rvs(c = self.shape_c,
                                            loc = self.loc + self.loc_credit_delta,
                                            scale = self.scale)
                else:
                    raise ValueError("Probability distibution type not specified or supported.")
                    return
        
        except TypeError as te:
            print("Duration probability distribution not specified: ", te)
            return
            