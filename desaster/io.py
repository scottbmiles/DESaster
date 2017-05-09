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
from simpy import FilterStore
from desaster.structures import SingleFamilyResidential

class DurationProbabilityDistribution(object):
    """A general class to hold parameters for defining different probability
    distibutions for use with io.random_duration_function() to dynamically randomly
    sample a duration for a given process.
    
    Parameter terminology follows the generalized terms from numpy.stats module:
    https://docs.scipy.org/doc/scipy/reference/stats.html#module-scipy.stats
    """
    def __init__(self, dist='scalar', loc=0.0, scale=None, shape_a=None, shape_b=None, shape_c=None):
        """Initiate a DurationProbabilityDistribution object.
        
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
        
def random_duration_function(duration_prob_dist):
    """A function that returns a pointer to a lambda function that will 
    dynamically randomly sample a duration for a given process based on distribution 
    type and parameters specified by inputted io.DurationProbabilityDistribution. 
    Random number generators for different distributions from numpy.stats. 
    
    Supported numpy.stats Distributions:
    scalar (determistic scalar location)
    uniform.rvs
    beta.rvs
    weibull_min.rvs
    
    Returns
    lambda numpy.stats.[DurationProbabilityDistribution].rvs()
    """
    try:
        if duration_prob_dist.dist == "scalar":
            return lambda : duration_prob_dist.loc
        elif duration_prob_dist.dist == "uniform":
            return lambda : uniform.rvs(loc=duration_prob_dist.loc,
                                                    scale=duration_prob_dist.scale)
        elif duration_prob_dist.dist == "beta":
            return lambda : beta.rvs(a=duration_prob_dist.shape_a,
                                                b=duration_prob_dist.shape_b,
                                                loc=duration_prob_dist.loc,
                                                scale=duration_prob_dist.scale)
        elif duration_prob_dist.dist == "weibull":
            return lambda : weibull_min.rvs(c=duration_prob_dist.shape_c,
                                                loc=duration_prob_dist.loc,
                                                scale=duration_prob_dist.scale)
        else:
            raise ValueError("Probability distibution type not specified or supported.")
            return
    except TypeError as te:
        print("Duration probability distribution not specified: ", te)
        return

def importSingleFamilyResidenceStock(env, stock_df):
    """Define, populate and return a SimPy FilterStore with SingleFamilyResidential() 
    objects to represent a vacant housing stock.
    
    Keyword Arguments:
    env -- Pointer to SimPy env environment.
    stock_df -- Dataframe with required attributes for each vacant home in
                the stock.
    """
    stock_fs = FilterStore(env)

    for i in stock_df.index:
        stock_fs.put(SingleFamilyResidential(stock_df.loc[i]))

    return stock_fs
    
    def importOwners(env, building_stock, entities_df, write_story = False):
        """Return list of entities.Household() objects from dataframe containing
        data describing entities' attributes.

        Keyword Arguments:
        env -- Pointer to SimPy env environment.
        building_stock -- a SimPy FilterStore that acts as an occupied building stock.
        entities_df -- Dataframe row w/ entity input attributes.
        write_story -- Boolean indicating whether to track a entitys story.
        """

        entities = []

        # Population the env with entitys from the entitys dataframe
        for i in entities_df.index:
            entities.append(Owner(env, building_stock, entities_df.iloc[i], write_story))
        return entities

def importEntities(env, building_stock, entities_df, entity_type, write_story = False):
        """Return list of entities.OwnerHouseholds() objects from dataframe containing
        data describing entities' attributes.

        Keyword Arguments:
        env -- Pointer to SimPy env environment.
        building_stock -- a SimPy FilterStore that acts as an occupied building stock.
        entities_df -- Dataframe row w/ entities' input attributes.
        entity_type -- Indicate class of entity: Household, Owner, OwnerHousehold etc.
        write_story -- Boolean indicating whether to track a entitys story.
        """
        entities = []

        if entity_type.lower() == 'household':
            # Populate the env with entitys from the entitys dataframe
            for i in entities_df.index:
                entities.append(Household(env, entities_df.iloc[i]['Name'], entities_df.iloc[i], building_stock, write_story))
            return entities
        elif entity_type.lower() == 'owner':
            # Populate the env with entitys from the entitys dataframe
            for i in entities_df.index:
                entities.append(Owner(env, entities_df.iloc[i]['Name'], entities_df.iloc[i], building_stock, write_story))
            return entities
        elif entity_type.lower() == 'ownerhousehold':
            # Populate the env with entitys from the entitys dataframe
            for i in entities_df.index:
                entities.append(OwnerHousehold(env, entities_df.iloc[i]['Name'], entities_df.iloc[i], building_stock, write_story))
            return entities
        elif entity_type.lower() == 'renterhousehold':
            # Populate the env with entitys from the entitys dataframe
            for i in entities_df.index:
                entities.append(RenterHousehold(env, entities_df.iloc[i]['Name'], entities_df.iloc[i], building_stock, write_story))
            return entities
        elif entity_type.lower() == 'landlord':
            # Populate the env with entitys from the entitys dataframe
            for i in entities_df.index:
                entities.append(Landlord(env, entities_df.iloc[i]['Name'], entities_df.iloc[i], building_stock, write_story))
            return entities
        else:
            raise AttributeError("Entity class type not specified or recognized. Can't complete import.")

def importOwnerHouseholds(env, building_stock, entities_df, write_story = False):
    """Return list of entities.OwnerHouseholds() objects from dataframe containing
    data describing entities' attributes.

    Keyword Arguments:
    env -- Pointer to SimPy env environment.
    building_stock -- a SimPy FilterStore that acts as an occupied building stock.
    entities_df -- Dataframe row w/ entity input attributes.
    write_story -- Boolean indicating whether to track a entitys story.
    """

    warnings.showwarning('importOwnerHouseholds depricated. Use importEntities.',
                            DeprecationWarning, filename = sys.stderr,
                            lineno=643)

    entities = importEntities(env, building_stock, entities_df, 'ownerhousehold', write_story)

    return entities 

def importRenterHouseholds(env, building_stock, entities_df, write_story = False):
    """Return list of entities.RenterHousehold() objects from dataframe containing
    dataframe describing entities' attributes.

    Keyword Arguments:
    env -- Pointer to SimPy env environment.
    building_stock -- a SimPy FilterStore that acts as an occupied building stock.
    entities_df -- Dataframe row w/ entity input attributes.
    write_story -- Boolean indicating whether to track a entitys story.
    """

    warnings.showwarning('importRenterHouseholds depricated. Use importEntities.',
                            DeprecationWarning, filename = sys.stderr,
                            lineno=661)

    entities = importEntities(env, building_stock, entities_df, 'renterhousehold', write_story)

    return entities
