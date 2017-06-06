# -*- coding: utf-8 -*-
"""
Module of classes for specifying generic and custom probability distributions 
for input parameters and process durations.

Classes:
DurationDistributionHomeLoanSBA
ProbabilityDistribution

@author: Scott Miles (milessb@uw.edu)
"""
from scipy.stats import uniform, beta, weibull_min
import numpy as np
from statsmodels.nonparametric.kde import KDEUnivariate

class ProbabilityDistribution(object):
    """A general class to hold parameters for defining different probability
    distibutions to dynamically randomly sample a duration for a given process.
    
    Parameter terminology follows the generalized terms from numpy.stats module:
    https://docs.scipy.org/doc/scipy/reference/stats.html#module-scipy.stats
    """
    def __init__(self, dist='scalar', loc=0.0, scale=None, shape_a=None, shape_b=None, 
                    shape_c = None, loc_delta = 0.0):
        """Initiate a ProbabilityDistribution object.
        
        Keyword Arguments:
        dist -- String. Name of a probability distribution from scipy.stats
        loc -- Float. The location of the distribution (e.g., mean, for Gaussian)
        scale -- Float. Scale of the distribution. (e.g., distribution range for Uniform)
        shape_a -- Float. Numpy.stats shape parameter "a". (e.g., for Beta)
        shape_b -- Float. Numpy.stats shape parameter "b". (e.g., for Beta)
        shape_c -- Float. Numpy.stats shape parameter "c". (e.g., for Weibull)
        loc_delta -- Float. Used to shift loc (central measure) positively or negatively
        
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
        self.loc_delta = loc_delta # Float. Used to shift loc (central measure) positively or negatively
        
    def value(self):
        """A function that returns a sampled value for a given process 
        based on distribution type and parameters specified by inputted
        ProbabilityDistribution. Random number generators for different 
        distributions from scipy.stats. 
        
        Supported Distributions:
        scalar (determistic scalar location)
        scipy.stats.uniform.rvs
        scipy.stats.beta.rvs
        scipy.stats.weibull_min.rvs
        
        Returns:
        value()
        """
        try:
            if self.dist == "scalar":
                return (self.loc + self.loc_delta)
            elif self.dist == "uniform":
                return uniform.rvs(loc = (self.loc + self.loc_delta), scale = self.scale)
            elif self.dist == "beta":
                return beta.rvs(a = self.shape_a, b = self.shape_b,loc = (self.loc + self.loc_delta),
                                scale = self.scale)
            elif self.dist == "weibull":
                return weibull_min.rvs(c = self.shape_c,loc = (self.loc + self.loc_delta),
                                        scale = self.scale)
            else:
                raise ValueError("Probability distibution type not specified or supported.")
                return
        except TypeError:
            print("Probability distribution argument(s) missing.")
            return
            
class KDE_Distribution(object):
    """A general class to do a Kernel Density Estimate to allow random sampling
    from the associated CDF. 
    
    Useful for when data does not match a standard distribution.
    """
    def __init__(self, data):
        """Initiate a KDE_Distribution object.
        
        # Keyword Arguments
        data -- One-dimensional array of float values to fit KDE and CDF
        
        Returns:
        value()
        """
        self.kde = KDEUnivariate(data)
        self.kde.fit()
    
    def value(self):
        """A function that returns a sampled value from the CDF for a given process.
        
        Returns:
        value()
        """
        num = len(self.kde.cdf)
        x_grid = np.linspace(min(data), max(data), num)
        values = np.random.uniform()
        value_bins = np.searchsorted(self.kde.cdf, values)
        return x_grid[value_bins]
    
class DurationDistributionHomeLoanSBA(ProbabilityDistribution):
    """
    A custom distribuion for use with financial.RealPropertyLoanSBA that applies
    a delta to the distribution loc (e.g., mean) based on a some credit threshold
    and entity credit attribute.
    
    Keyword Arguments:
    dist -- String. Name of a probability distribution from scipy.stats
    loc -- Float. The location of the distribution (e.g., mean, for Gaussian)
    scale -- Float. Scale of the distribution. (e.g., distribution range for Uniform)
    shape_a -- Float. Numpy.stats shape parameter "a". (e.g., for Beta)
    shape_b -- Float. Numpy.stats shape parameter "b". (e.g., for Beta)
    shape_c -- Float. Numpy.stats shape parameter "c". (e.g., for Weibull)
    loc_delta_credit -- Float. Used to shift loc (central measure) positively or negatively
    
    Parameter terminology follows the generalized terms from numpy.stats module:
    https://docs.scipy.org/doc/scipy/reference/stats.html#module-scipy.stats
    """
    def __init__(self, dist='beta', loc=15.0, scale=30.0, shape_a=2.0, shape_b=2.0, loc_delta_credit=15.0):
        
        ProbabilityDistribution.__init__(self, dist, loc, scale, shape_a, shape_b)
        
        self.loc_delta_credit = loc_delta_credit # Float. Used to shift loc (central measure) positively or negatively
        
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
            