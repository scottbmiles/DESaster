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
from desaster.entities import Owner, Household, OwnerHousehold, RenterHousehold, Landlord
from desaster.structures import SingleFamilyResidential, Building

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
        
    def duration(self):
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
            if self.dist == "scalar":
                return lambda : self.loc
            elif self.dist == "uniform":
                return lambda : uniform.rvs(loc=self.loc,
                                                        scale=self.scale)
            elif self.dist == "beta":
                return lambda : beta.rvs(a=self.shape_a,
                                                    b=self.shape_b,
                                                    loc=self.loc,
                                                    scale=self.scale)
            elif self.dist == "weibull":
                return lambda : weibull_min.rvs(c=self.shape_c,
                                                    loc=self.loc,
                                                    scale=self.scale)
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

def importEntities(env, entities_df, entity_type, building_stock = None, write_story = False):
    """Return list of entities.OwnerHouseholds() objects from dataframe containing
    data describing entities' attributes.

    Keyword Arguments:
    env -- Pointer to SimPy env environment.
    building_stock -- a SimPy FilterStore that acts as an occupied building stock.
    entities_df -- Dataframe row w/ entities' input attributes.
    entity_type -- Indicate class of entity: Household, Owner, OwnerHousehold etc.
    write_story -- Boolean indicating whether to track a entities story.
    """
    # try:
    entities = []
    if entity_type.lower() == 'household':
        # Populate the env with entities from the entities dataframe
        for i in entities_df.index:
            
            if entities_df.iloc[i]['Occupancy'].lower() in ['single family house', 'single family home', 
                                    'single family dwelling', 'single family residence',
                                    'sfr', 'sfh', 'sfd', 'mobile home']:
                
                residence = SingleFamilyResidential(
                                    occupancy = entities_df.iloc[i]['Occupancy'],
                                    address = entities_df.iloc[i]['Address'],
                                    longitude = entities_df.iloc[i]['Longitude'],
                                    latitude = entities_df.iloc[i]['Latitude'],
                                    value = entities_df.iloc[i]['Value'],
                                    cost = entities_df.iloc[i]['Cost'],
                                    area = entities_df.iloc[i]['Area'],
                                    bedrooms = entities_df.iloc[i]['Bedrooms'],
                                    bathrooms = entities_df.iloc[i]['Bathrooms'],
                                    listed = entities_df.iloc[i]['Listed'],
                                    damage_state = entities_df.iloc[i]['Damage State'],
                                    building_stock = building_stock
                                    )
            else:
                raise AttributeError("Specified occupancy type ({0}) associated with entity \'{1}\' not supported. Can't complete import.".format(entities_df.iloc[i]['Occupancy'], entities_df.iloc[i]['Name']))
                return
            
            entity = Household(env, 
                                name = entities_df.iloc[i]['Name'],
                                write_story = write_story,
                                residence = residence
                                )
            
            entities.append(entity)
        return entities
    elif entity_type.lower() == 'owner':
        # Populate the env with entities from the entities dataframe
        for i in entities_df.index:
            if entities_df.iloc[i]['Occupancy'].lower() in ['single family house', 'single family home', 
                                    'single family dwelling', 'single family residence',
                                    'sfr', 'sfh', 'sfd', 'mobile home']:
                real_property = SingleFamilyResidential(
                                            occupancy = entities_df.iloc[i]['Occupancy'],
                                            address = entities_df.iloc[i]['Address'],
                                            longitude = entities_df.iloc[i]['Longitude'],
                                            latitude = entities_df.iloc[i]['Latitude'],
                                            value = entities_df.iloc[i]['Value'],
                                            cost = entities_df.iloc[i]['Cost'],
                                            area = entities_df.iloc[i]['Area'],
                                            bedrooms = entities_df.iloc[i]['Bedrooms'],
                                            bathrooms = entities_df.iloc[i]['Bathrooms'],
                                            listed = entities_df.iloc[i]['Listed'],
                                            damage_state = entities_df.iloc[i]['Damage State'],
                                            building_stock = building_stock
                                                    )
            else:
                raise AttributeError("Specified occupancy type ({0}) associated with entity \'{1}\' not supported. Can't complete import.".format(entities_df.iloc[i]['Occupancy'], entities_df.iloc[i]['Name']))
                return
                
            entity = Owner(env, 
                            name = entities_df.iloc[i]['Name'],
                            savings = entities_df.iloc[i]['Owner Savings'],
                            insurance = entities_df.iloc[i]['Owner Insurance'],
                            write_story = write_story,
                            real_property = real_property
                            )

            entity.property.owner = entity
            entities.append(entity)    
        return entities
    
    elif entity_type.lower() == 'ownerhousehold' or entity_type.lower() == 'owner household':
        # Populate the env with entities from the entities dataframe
        for i in entities_df.index:
            if entities_df.iloc[i]['Occupancy'].lower() in ['single family house', 'single family home', 
                                    'single family dwelling', 'single family residence',
                                    'sfr', 'sfh', 'sfd', 'mobile home']:                  
                real_property = SingleFamilyResidential(
                                                    occupancy = entities_df.iloc[i]['Occupancy'],
                                                    address = entities_df.iloc[i]['Address'],
                                                    longitude = entities_df.iloc[i]['Longitude'],
                                                    latitude = entities_df.iloc[i]['Latitude'],
                                                    value = entities_df.iloc[i]['Value'],
                                                    cost = entities_df.iloc[i]['Cost'],
                                                    area = entities_df.iloc[i]['Area'],
                                                    bedrooms = entities_df.iloc[i]['Bedrooms'],
                                                    bathrooms = entities_df.iloc[i]['Bathrooms'],
                                                    listed = entities_df.iloc[i]['Listed'],
                                                    damage_state = entities_df.iloc[i]['Damage State'],
                                                    building_stock = building_stock
                                                    )
            else:
                raise AttributeError("Specified occupancy type ({0}) associated with entity \'{1}\' not supported. Can't complete import.".format(entities_df.iloc[i]['Occupancy'], entities_df.iloc[i]['Name']))
                return
            
            entity = OwnerHousehold(env, 
                                    name = entities_df.iloc[i]['Name'],
                                    savings = entities_df.iloc[i]['Owner Savings'],
                                    insurance = entities_df.iloc[i]['Owner Insurance'],
                                    real_property = real_property,
                                    write_story = write_story
                                    )

            entity.property.owner = entity                                
            entities.append(entity)
        return entities
    elif entity_type.lower() == 'renterhousehold' or entity_type.lower() == 'renter household':
        # Populate the env with entities from the entities dataframe
        for i in entities_df.index:
            
            if entities_df.iloc[i]['Occupancy'].lower() in ['single family house', 'single family home', 
                                    'single family dwelling', 'single family residence',
                                    'sfr', 'sfh', 'sfd', 'mobile home']:                           
                real_property = SingleFamilyResidential(
                                            occupancy = entities_df.iloc[i]['Occupancy'],
                                            address = entities_df.iloc[i]['Address'],
                                            longitude = entities_df.iloc[i]['Longitude'],
                                            latitude = entities_df.iloc[i]['Latitude'],
                                            value = entities_df.iloc[i]['Value'],
                                            cost = entities_df.iloc[i]['Cost'],
                                            area = entities_df.iloc[i]['Area'],
                                            bedrooms = entities_df.iloc[i]['Bedrooms'],
                                            bathrooms = entities_df.iloc[i]['Bathrooms'],
                                            listed = entities_df.iloc[i]['Listed'],
                                            damage_state = entities_df.iloc[i]['Damage State'],
                                            building_stock = building_stock
                                                        )
            else:
                raise AttributeError("Specified occupancy type ({0}) associated with entity \'{1}\' not supported. Can't complete import.".format(entities_df.iloc[i]['Occupancy'], entities_df.iloc[i]['Name']))
                return                      

            entity = RenterHousehold(env, 
                                        name = entities_df.iloc[i]['Name'],
                                        write_story = write_story,
                                        residence = real_property
                                        )
            
            entity.landlord = Landlord(env, 
                                        name = entities_df.iloc[i]['Landlord'],
                                        savings = entities_df.iloc[i]['Owner Savings'],
                                        insurance = entities_df.iloc[i]['Owner Insurance'],
                                        real_property = real_property,
                                        write_story = write_story
                                        )
                    
            entity.landlord.tenant = entity
            entity.landlord.property.owner = entity.landlord
            entities.append(entity)
        return entities
    elif entity_type.lower() == 'landlord':
        # Populate the env with entities from the entities dataframe
        for i in entities_df.index:
            if entities_df.iloc[i]['Occupancy'].lower() in ['single family house', 'single family home', 
                                    'single family dwelling', 'single family residence',
                                    'sfr', 'sfh', 'sfd', 'mobile home']: 
                real_property = SingleFamilyResidential(
                                            occupancy = entities_df.iloc[i]['Occupancy'],
                                            address = entities_df.iloc[i]['Address'],
                                            longitude = entities_df.iloc[i]['Longitude'],
                                            latitude = entities_df.iloc[i]['Latitude'],
                                            value = entities_df.iloc[i]['Value'],
                                            cost = entities_df.iloc[i]['Cost'],
                                            area = entities_df.iloc[i]['Area'],
                                            bedrooms = entities_df.iloc[i]['Bedrooms'],
                                            bathrooms = entities_df.iloc[i]['Bathrooms'],
                                            listed = entities_df.iloc[i]['Listed'],
                                            damage_state = entities_df.iloc[i]['Damage State'],
                                            building_stock = building_stock
                                                        )
            else:
                raise AttributeError("Specified occupancy type ({0}) associated with entity \'{1}\' not supported. Can't complete import.".format(entities_df.iloc[i]['Occupancy'], entities_df.iloc[i]['Name']))
                return
                                                        
            entity = Landlord(env, 
                                        name = entities_df.iloc[i]['Landlord'],
                                        savings = entities_df.iloc[i]['Owner Savings'],
                                        insurance = entities_df.iloc[i]['Owner Insurance'],
                                        real_property = real_property,
                                        write_story = write_story
                                        )
            
            entity.property.owner = entity
            entities.append(entity)                                            
        return entities
    else:
        raise AttributeError("Entity type ({0}) not recognized. Can't complete import.".format(entity_type))
        return
    # except:
    #     warnings.showwarning('importEntities: Unexpected missing attribute. Attribute value set to None.',
    #                             DeprecationWarning, filename = sys.stderr,
    #                             lineno=312)

def importOwnerHouseholds(env, building_stock, entities_df, write_story = False):
    """Return list of entities.OwnerHouseholds() objects from dataframe containing
    data describing entities' attributes.

    Keyword Arguments:
    env -- Pointer to SimPy env environment.
    building_stock -- a SimPy FilterStore that acts as an occupied building stock.
    entities_df -- Dataframe row w/ entity input attributes.
    write_story -- Boolean indicating whether to track a entities story.
    """

    warnings.showwarning('importOwnerHouseholds depricated. Use importEntities.',
                            DeprecationWarning, filename = sys.stderr,
                            lineno=296)


def importRenterHouseholds(env, building_stock, entities_df, write_story = False):
    """Return list of entities.RenterHousehold() objects from dataframe containing
    dataframe describing entities' attributes.

    Keyword Arguments:
    env -- Pointer to SimPy env environment.
    building_stock -- a SimPy FilterStore that acts as an occupied building stock.
    entities_df -- Dataframe row w/ entity input attributes.
    write_story -- Boolean indicating whether to track a entities story.
    """

    warnings.showwarning('importRenterHouseholds depricated. Use importEntities.',
                            DeprecationWarning, filename = sys.stderr,
                            lineno=312)

