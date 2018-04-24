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
    
Module of classes and functions for input/output related to DESaster.

Classes:
importSingleFamilyResidenceStock

@author: Scott Miles (milessb@uw.edu), Derek Huling
"""
from scipy.stats import uniform, beta, weibull_min
from simpy import FilterStore
from desaster.entities import Owner, Household, OwnerHousehold, RenterHousehold, Landlord
from desaster.structures import SingleFamilyResidential, Building
import pandas as pd
import numpy as np

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
            
            if entities_df.iloc[i]['occupancy'].lower() in ['single family house', 'single family home', 
                                    'single family dwelling', 'single family residence',
                                    'sfr', 'sfh', 'sfd', 'mobile home']:
                
                residence = SingleFamilyResidential(
                                    occupancy = entities_df.iloc[i]['occupancy'],
                                    tenure = entities_df.iloc[i]['tenure'],
                                    address = entities_df.iloc[i]['address'],
                                    longitude = entities_df.iloc[i]['longitude'],
                                    latitude = entities_df.iloc[i]['latitude'],
                                    value = entities_df.iloc[i]['value'],
                                    cost = entities_df.iloc[i]['monthly_cost'],
                                    area = entities_df.iloc[i]['area'],
                                    bedrooms = entities_df.iloc[i]['bedrooms'],
                                    bathrooms = entities_df.iloc[i]['bathrooms'],
                                    listed = entities_df.iloc[i]['listed'],
                                    damage_state = entities_df.iloc[i]['damage_state'],
                                    building_stock = building_stock
                                    )
            else:
                raise AttributeError("Specified occupancy type ({0}) associated with entity \'{1}\' not supported. Can't complete import.".format(entities_df.iloc[i]['occupancy'], entities_df.iloc[i]['name']))
                return
            
            entity = Household(env, 
                                name = entities_df.iloc[i]['name'],
                                income = entities_df.iloc[i]['income'],
                                write_story = write_story,
                                residence = residence
                                )
            
            entities.append(entity)
        return entities
    elif entity_type.lower() == 'owner':
        # Populate the env with entities from the entities dataframe
        for i in entities_df.index:
            if entities_df.iloc[i]['occupancy'].lower() in ['single family house', 'single family home', 
                                    'single family dwelling', 'single family residence',
                                    'sfr', 'sfh', 'sfd', 'mobile home']:
                real_property = SingleFamilyResidential(
                                            occupancy = entities_df.iloc[i]['occupancy'],
                                            tenure = entities_df.iloc[i]['tenure'],
                                            address = entities_df.iloc[i]['address'],
                                            longitude = entities_df.iloc[i]['longitude'],
                                            latitude = entities_df.iloc[i]['latitude'],
                                            value = entities_df.iloc[i]['value'],
                                            cost = entities_df.iloc[i]['monthly_cost'],
                                            area = entities_df.iloc[i]['area'],
                                            bedrooms = entities_df.iloc[i]['bedrooms'],
                                            bathrooms = entities_df.iloc[i]['bathrooms'],
                                            listed = entities_df.iloc[i]['listed'],
                                            damage_state = entities_df.iloc[i]['damage_state'],
                                            building_stock = building_stock
                                                    )
                                                    
                
            
            else:
                raise AttributeError("Specified occupancy type ({0}) associated with entity \'{1}\' not supported. Can't complete import.".format(entities_df.iloc[i]['occupancy'], entities_df.iloc[i]['name']))
                return
                
            entity = Owner(env, 
                            name = entities_df.iloc[i]['name'],
                            savings = entities_df.iloc[i]['savings'],
                            insurance = entities_df.iloc[i]['insurance'],
                            credit = entities_df.iloc[i]['credit'],
                            write_story = write_story,
                            real_property = real_property
                            )

            entity.property.owner = entity
            building_stock.put(real_property)
            entities.append(entity)    
        return entities
    
    elif entity_type.lower() == 'ownerhousehold' or entity_type.lower() == 'owner household':
        # Populate the env with entities from the entities dataframe
        for i in entities_df.index:
            if entities_df.iloc[i]['occupancy'].lower() in ['single family house', 'single family home', 
                                    'single family dwelling', 'single family residence',
                                    'sfr', 'sfh', 'sfd', 'mobile home']:                  
                real_property = SingleFamilyResidential(
                                                    occupancy = entities_df.iloc[i]['occupancy'],
                                                    tenure = entities_df.iloc[i]['tenure'],
                                                    address = entities_df.iloc[i]['address'],
                                                    longitude = entities_df.iloc[i]['longitude'],
                                                    latitude = entities_df.iloc[i]['latitude'],
                                                    value = entities_df.iloc[i]['value'],
                                                    cost = entities_df.iloc[i]['monthly_cost'],
                                                    area = entities_df.iloc[i]['area'],
                                                    bedrooms = entities_df.iloc[i]['bedrooms'],
                                                    bathrooms = entities_df.iloc[i]['bathrooms'],
                                                    listed = entities_df.iloc[i]['listed'],
                                                    damage_state = entities_df.iloc[i]['damage_state'],
                                                    building_stock = building_stock
                                                    )
                
                
                
            else:
                raise AttributeError("Specified occupancy type ({0}) associated with entity \'{1}\' not supported. Can't complete import.".format(entities_df.iloc[i]['occupancy'], entities_df.iloc[i]['name']))
                return
            
            entity = OwnerHousehold(env, 
                                    name = entities_df.iloc[i]['name'],
                                    income = entities_df.iloc[i]['income'],
                                    savings = entities_df.iloc[i]['savings'],
                                    insurance = entities_df.iloc[i]['insurance'],
                                    credit = entities_df.iloc[i]['credit'],
                                    real_property = real_property,
                                    write_story = write_story
                                    )

            entity.property.owner = entity  
            building_stock.put(real_property)                              
            entities.append(entity)
        return entities
    elif entity_type.lower() == 'renterhousehold' or entity_type.lower() == 'renter household':
        # Populate the env with entities from the entities dataframe
        for i in entities_df.index:
            if entities_df.iloc[i]['occupancy'].lower() in ['single family house', 'single family home', 
                                    'single family dwelling', 'single family residence',
                                    'sfr', 'sfh', 'sfd', 'mobile home']:                           
                real_property = SingleFamilyResidential(
                                            occupancy = entities_df.iloc[i]['occupancy'],
                                            tenure = entities_df.iloc[i]['tenure'],
                                            address = entities_df.iloc[i]['address'],
                                            longitude = entities_df.iloc[i]['longitude'],
                                            latitude = entities_df.iloc[i]['latitude'],
                                            value = entities_df.iloc[i]['value'],
                                            cost = entities_df.iloc[i]['monthly_cost'],
                                            area = entities_df.iloc[i]['area'],
                                            bedrooms = entities_df.iloc[i]['bedrooms'],
                                            bathrooms = entities_df.iloc[i]['bathrooms'],
                                            listed = entities_df.iloc[i]['listed'],
                                            damage_state = entities_df.iloc[i]['damage_state'],
                                            building_stock = building_stock
                                                        )
            else:
                raise AttributeError("Specified occupancy type ({0}) associated with entity \'{1}\' not supported. Can't complete import.".format(entities_df.iloc[i]['occupancy'], entities_df.iloc[i]['name']))
                return                      

            entity = RenterHousehold(env, 
                                        name = entities_df.iloc[i]['name'],
                                        income = entities_df.iloc[i]['income'],
                                        savings = entities_df.iloc[i]['savings'],
                                        insurance = entities_df.iloc[i]['insurance'],
                                        credit = entities_df.iloc[i]['credit'],
                                        write_story = write_story,
                                        residence = real_property
                                        )
            
            entity.landlord = Landlord(env, 
                                        name = entities_df.iloc[i]['landlord'],
                                        savings = entities_df.iloc[i]['landlord_savings'],
                                        insurance = entities_df.iloc[i]['landlord_insurance'],
                                        credit = entities_df.iloc[i]['landlord_credit'],
                                        real_property = real_property,
                                        write_story = write_story
                                        )
                    
            entity.landlord.tenant = entity
            entity.landlord.property.owner = entity.landlord
            building_stock.put(real_property)
            entities.append(entity)
        return entities
    elif entity_type.lower() == 'landlord':
        # Populate the env with entities from the entities dataframe
        for i in entities_df.index:
            if entities_df.iloc[i]['occupancy'].lower() in ['single family house', 'single family home', 
                                    'single family dwelling', 'single family residence',
                                    'sfr', 'sfh', 'sfd', 'mobile home']: 
                real_property = SingleFamilyResidential(
                                            occupancy = entities_df.iloc[i]['occupancy'],
                                            tenure = entities_df.iloc[i]['tenure'],
                                            address = entities_df.iloc[i]['address'],
                                            longitude = entities_df.iloc[i]['longitude'],
                                            latitude = entities_df.iloc[i]['latitude'],
                                            value = entities_df.iloc[i]['value'],
                                            cost = entities_df.iloc[i]['monthly_cost'],
                                            area = entities_df.iloc[i]['area'],
                                            bedrooms = entities_df.iloc[i]['bedrooms'],
                                            bathrooms = entities_df.iloc[i]['bathrooms'],
                                            listed = entities_df.iloc[i]['listed'],
                                            damage_state = entities_df.iloc[i]['damage_state'],
                                            building_stock = building_stock
                                                        )
                
            else:
                raise AttributeError("Specified occupancy type ({0}) associated with entity \'{1}\' not supported. Can't complete import.".format(entities_df.iloc[i]['occupancy'], entities_df.iloc[i]['name']))
                return
                                                        
            entity = Landlord(env, 
                                        name = entities_df.iloc[i]['landlord'],
                                        savings = entities_df.iloc[i]['landlord_savings'],
                                        insurance = entities_df.iloc[i]['landlord_insurance'],
                                        credit = entities_df.iloc[i]['landlord_credit'],
                                        real_property = real_property,
                                        write_story = write_story
                                        )
            
            entity.property.owner = entity
            building_stock.put(real_property)
            entities.append(entity)                                            
        return entities
    else:
        raise AttributeError("Entity type ({0}) not recognized. Can't complete import.".format(entity_type))
        return
    # except:
    #     warnings.showwarning('importEntities: Unexpected missing attribute. Attribute value set to None.',
    #                             DeprecationWarning, filename = sys.stderr,
    #                             lineno=312)

def output_summary(entities, entity_type):
    """ A band-aid function for printing out simulation outputs for entities
    
    """
    if entity_type.lower() in ['ownerhousehold', 'owner household']:
        num_damaged = 0
        num_rebuilt = 0
        num_gave_up_funding_search = 0
        num_relocated = 0
        num_homesearch = 0
        num_gave_up_home_search = 0
        num_vacant_fixed = 0

        for household in entities:
            if household.residence.damage_state != None: num_damaged += 1
            if household.repair_get != None: num_rebuilt += 1
            if household.gave_up_funding_search: num_gave_up_funding_search += 1
            if household.home_put != None: num_homesearch += 1
            if household.home_get != None: num_relocated += 1
            if household.gave_up_home_search: num_gave_up_home_search += 1
          
        print('{0} out of {1} owners suffered damage to their homes.\n'.format(num_damaged, len(entities)),
          '{0} out of {1} owners rebuilt or repaired their damaged home.\n'.format(num_rebuilt, len(entities)),
            '{0} out of {1} owners gave up searching for money.\n'.format(num_gave_up_funding_search, len(entities)),
          '{0} out of {1} owners searchesd for a new home.\n'.format(num_homesearch, len(entities)),
            '{0} out of {1} owners bought a new home.\n'.format(num_relocated, len(entities)),
            '{0} out of {1} owners gave up searching for a home.'.format(num_gave_up_home_search, len(entities))
            )
    if entity_type.lower() in ['renterhousehold', 'renter household']:
        num_damaged = 0
        num_rebuilt = 0
        num_relocated = 0
        num_displaced = 0
        num_gave_up_funding_search = 0
        num_gave_up_home_search = 0
        num_vacant_fixed = 0

        for renter in entities:
            if renter.landlord.property.damage_state != None: num_damaged += 1
            if renter.landlord.repair_get != None: num_rebuilt += 1
            if renter.landlord.gave_up_funding_search != None: num_gave_up_funding_search += 1
            if not renter.residence: num_displaced += 1
            if renter.gave_up_home_search: num_displaced += 1

        print('{0} out of {1} renters\' homes suffered damage.\n'.format(num_damaged, len(entities)),
              '{0} out of {1} renters\' damaged home was rebuilt or repaired.\n'.format(num_rebuilt, len(entities)),
              '{0} out of {1} renters\' were displaced.\n'.format(num_displaced, len(entities)),
              '{0} landlords gave up searching for repair money.'.format(num_gave_up_funding_search)
             )

def households_to_df(entities):
    """
    
    *** This works but is a bandaid for saving simulation outputs 
    for external visualization or stats. *** Create output file for visualizing ***
    
    *** Needs to be generalized, e.g., so can process RenterHouseholds. ***
    
    """
    attributes = list(vars(entities[0]).keys()) #gets all potential column names
    attributes.extend(list(vars(entities[0].residence).keys()))
    df = pd.DataFrame(columns=attributes)
    new_column={}
     
    for i in entities: #loop through all entities
        
        i.story = i.story_to_text()
        i.stock = np.nan
        
        # Add residence attributes to entity level
        # This exports attributes of first (or only) residence
        try:
            i.latitude = i.prior_residences[0].latitude
            i.longitude = i.prior_residences[0].longitude
            i.damage_state_start = i.prior_residences[0].damage_state_start
            i.damage_state = i.prior_residences[0].damage_state
            i.damage_value = i.prior_residences[0].damage_value    
            i.area = i.prior_residences[0].area
            i.bedrooms = i.prior_residences[0].bedrooms
            i.address = i.prior_residences[0].address
            i.listed = i.prior_residences[0].listed
            i.value = i.prior_residences[0].value
            i.permit = i.prior_residences[0].permit
            i.monthly_cost = i.prior_residences[0].monthly_cost
            i.bathrooms = i.prior_residences[0].bathrooms
            i.inspected = i.prior_residences[0].inspected
            i.occupancy = i.prior_residences[0].occupancy
            i.owner = i.prior_residences[0].owner
            i.damage_value_start = i.prior_residences[0].damage_value_start
            i.recovery_limit_state_start = i.prior_residences[0].recovery_limit_state_start
            i.recovery_limit_state = i.prior_residences[0].recovery_limit_state
            i.assessment = i.prior_residences[0].assessment
            
        except IndexError:
            i.latitude = i.residence.latitude
            i.longitude = i.residence.longitude
            i.damage_state_start = i.residence.damage_state_start
            i.damage_state = i.residence.damage_state
            i.damage_value = i.residence.damage_value    
            i.area = i.residence.area
            i.bedrooms = i.residence.bedrooms
            i.address = i.residence.address
            i.listed = i.residence.listed
            i.value = i.residence.value
            i.permit = i.residence.permit
            i.monthly_cost = i.residence.monthly_cost
            i.bathrooms = i.residence.bathrooms
            i.inspected = i.residence.inspected
            i.occupancy = i.residence.occupancy
            i.owner = i.residence.owner
            i.damage_value_start = i.residence.damage_value_start
            i.recovery_limit_state_start = i.residence.recovery_limit_state_start
            i.recovery_limit_state = i.residence.recovery_limit_state
            i.assessment = i.residence.assessment
        
        i.residence = np.nan
        i.prior_residences = np.nan
        
        #loop through the attributes in our list of column names we want
        for attribute in attributes: 
            try:
                new_column[attribute] = i.__getattribute__(attribute)      
            except ValueError:
                new_column[attribute] = np.nan
            except AttributeError as e:
                new_column[attribute] = np.nan
                print("Household {0} had an attribrute error, {1}".format(i.name, e))
            
        #Turn newly made column into a dataframe where it can be combined with the df
        df_column = pd.DataFrame([new_column]) 

        df = df.append(df_column, ignore_index=True)
        
    return df

         
