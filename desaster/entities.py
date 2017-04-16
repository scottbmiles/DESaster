# -*- coding: utf-8 -*-
"""
Module of classes for implementing DESaster entities, such as households and
businesses.

Classes:
Entity(object)
Owner(Entity)
Household(Entity)
OwnerHousehold(Owner, Household)
RenterHousehold(Entity, Household)
Landlord(Owner)

@author: Scott Miles (milessb@uw.edu), Derek Huling
"""
# Import Residence() class in order to assign entitys a residence.
from desaster.structures import SingleFamilyResidential
from desaster.io import random_duration_function
import names

class Entity(object):
    """A base class for representing entities, such as households, businesses, 
    agencies, NGOs, etc. At the moment moment the only attribute in common for 
    all entities are having a name and the potential to record the story of their
    recovery events.
    
    Methods:
    __init__(self, env, name, write_story = False)
    """
    def __init__(self, env, name, write_story = False):
        """

        Keyword Arguments:
        env -- Pointer to SimPy env environment.
        name -- A string indicating the entities name.
        write_story -- Boolean indicating whether to track an entity's story.
        """
        self.env = env
        
        # Household attributes
        self.name = name   # Name associated with occupant of the home %***%
        self.write_story = write_story # Boolean. Whether to track the entity's story.

        # Household env outputs
        self.story = []  # The story of events for each entity

    def story_to_text(self):
        """Join list of story strings into a single story string."""
        return ''.join(self.story)

class Owner(Entity):
    """An class that inherits from the Entity() class to represent any entity
    that owns property. Such entities require having attributes of insurance and
    savings (to facilate repairing or replacing the property). An owner does not 
    necessarily have a residence (e.g., landlord). For the most part this is class
    is to define subclasses with Owner() attributes.
    
    Methods:
    __init__(self, env, name, attributes_df, building_stock = None, write_story = False)
    """
    def __init__(self, env, name, attributes_df, building_stock = None, write_story = False):
        """Initiate several attributes related to an Owner entity.
        No universal methods have been define for the Owner class yet. methods
        are currently specified in subclasses of Owner.

        Keyword Arguments:
        env -- Pointer to SimPy env environment.
        attributes_df -- Dataframe row w/ entity input attributes.
        building_stock -- a SimPy FilterStore that acts as an occupied building stock.
                        The owner's property is added to the occupied building stock.
        write_story -- Boolean indicating whether to track the entity's story.
        
        Inheritance:
        Subclass of entities.Entity()
        """
        Entity.__init__(self, env, name, write_story)

        # Attributes
        self.insurance = attributes_df['Owner Insurance']  # Hazard-specific insurance coverage: coverage / residence.value
        self.savings = attributes_df['Savings']  # Amount of entity savings in $

        # Owner env outputs
        self.inspection_put = None  # Time put request in for house inspection
        self.inspection_get = None  # Time get  house inspection
        self.claim_put = None  # Time put request in for insurance settlement
        self.claim_get = None  # Time get insurance claim settled
        self.claim_payout = 0.0  # Amount of insurance claim payout
        self.assistance_put = None  # Time put request in for FEMA assistance
        self.assistance_get = None  # Time get FEMA assistance
        self.assistance_request = 0.0  # Amount of money requested from FEMA
        self.assistance_payout = 0.0  # Amount of assistance provided by FEMA
        self.money_to_rebuild = self.savings  # Total funds available to entity to rebuild house
        self.repair_put = None  # Time put request in for house rebuild
        self.repair_get = None  # Time get house rebuild completed
        self.loan_put = None  # Time put request for loan
        self.loan_get = None  # Time get requested loan
        self.loan_amount = 0.0  # Amount of loan received
        self.permit_put = None  # Time put request for building permit
        self.permit_get = None  # Time get requested building permit
        self.assessment_put = None  # Time put request for engineering assessment
        self.assessment_get = None  # Time put request for engineering assessment
        self.gave_up_funding_search = None  # Time entity gave up on some funding 
                                            # process; obviously can't keep track 
                                            # of multiple give ups
        self.prior_property = None

        # If no housing stock was specified, it indicates that do not want to 
        # associate a property with the entity. Useful for bulk processing of 
        # building stocks.
        if building_stock != None:
            self.property = SingleFamilyResidential(attributes_df)
            building_stock.put(self.property)
            
        if self.write_story:
            # Start stories with non-disaster attributes
            self.story.append('{0} owns a residence. '.format(self.name))

class Household(Entity):
    """Define a Household() class to represent a group of persons that reside
    together as a single dwelling unit. A Household() object can not own property,
    but does have a residence. For the most part this is class is to define 
    subclasses with Household() attributes.
    
    Methods:
    __init__(self, env, name, attributes_df, residence, write_story = False)
    """
    def __init__(self, env, name, attributes_df, residence, write_story = False):
        """Initiate a entities.Household() object.

        Keyword Arguments:  
        env -- Pointer to SimPy env environment.
        name -- A string indicating the entity's name.
        attributes_df -- Dataframe row w/ entity input attributes.
        residence -- A building object, such as structures.SingleFamilyResidential()
                    that serves as the entity's temporary or permanent residence.
        write_story -- Boolean indicating whether to track a entitys story.
        """
        Entity.__init__(self, env, name, write_story)

        # Attributes
        self.residence = residence

        # Entity outputs
        self.home_search_start = None  # Time started searching for a new home
        self.home_search_stop = None  # Time found a new home
        self.gave_up_home_search = None  # Whether entity gave up search for home
        self.home_put = None # The time when the entity put's in a request for a home. 
                                # None if request never made.
        self.home_get = None # The time when the entity receives a home. 
                                # None if never received.
        self.prior_residence = [] # An empty list to record each residence that 
                                    # the entity vacates.

        if self.write_story:
            self.story.append('{0} resides at {1}. '.format(
                                                            self.name, 
                                                            self.residence.address
                                                            )
                            )

class OwnerHousehold(Owner, Household):
    """The OwnerHousehold() class has attributes of both entities.Owner() and
    entities.Household() classes. It can own property and has a residence, which
    do not have to be the same. The OwnerHousehold() class includes methods to
    look for a new home to purchase (property), as well as to occupy a residence
    (not necessarily it's property).
    
    Methods:
    replace_home(self, search_patience, building_stock)
    occupy(self, duration_prob_dist, callbacks = None)
    """
    def __init__(self, env, name, attributes_df, building_stock, write_story = False):
        """Define entity inputs and outputs attributes.
        Initiate entity's story list string.

        Keyword Arguments:
        env -- Pointer to SimPy env environment.
        attributes_df -- Dataframe row w/ entity input attributes.
        building_stock -- a SimPy FilterStore that acts as an occupied housing stock
        write_story -- Boolean indicating whether to track a entitys story.
        """
        Owner.__init__(self, env, name, attributes_df, building_stock, write_story)
        Household.__init__(self, env, name, attributes_df, self.property, write_story)

        # Attributes

        # Entity outputs
        if self.write_story:
            # Set story with non-disaster attributes.
            self.story.append(
            '{0} owns and lives in a {1} room {2} at {3} worth ${4:,.0f}. '.format(self.name,
                                                            self.residence.bedrooms,
                                                            self.residence.occupancy.lower(),
                                                            self.residence.address,
                                                            self.residence.value
                                                            )
                                )

    def replace_home(self, search_patience, building_stock):
        """A process (generator) representing entity search for permanent housing
        based on housing preferences, available housing stock, and patience finding
        a new home.

        Keyword Arguments:
        search_patience -- The search duration in which the entity is willing to wait
                            to find a new home. Does not include the process of
                            securing money.
        building_stock -- A SimPy FilterStore that contains one or more
                        residential building objects (e.g., structures.SingleFamilyResidential) 
                        that represent vacant homes for purchase.

        Returns or Attribute Changes:
        self.story -- Process outcomes appended to story.
        self.home_search_start -- Record time home search starts
        self.home_search_stop -- Record time home search stops
        self.residence -- Potentially assigned a new residence object.
        self.gave_up_home_search -- Set with env.now to indicate if and when 
                                    search patience runs out.
        self.story -- If write_story == True, append entity story strings
        """
        # Record when housing search starts
        # Calculate the time that housing search patience ends
        # If write_story, write search start time to entity's story
        self.home_search_start = self.env.now
        patience_end = self.home_search_start + search_patience

        # Record entity's previous residence
        self.prior_property = self.property

        # Define timeout process representing entity's *remaining* search patience.
        # Return 'Gave up' if timeout process completes.
        find_search_patience = self.env.timeout(patience_end - self.env.now,
            value='Gave up')

        # Define a FilterStore.get process to find a new home to buy from the vacant
        # for sale stock with similar attributes as current home.
        if self.write_story:
            self.story.append(
                '{0} started searching for a new {1} {2:,.0f} days after the event. '.format(
                self.name.title(), self.property.occupancy.lower(),
                self.home_search_start)
                )
        new_home = building_stock.get(lambda findHome:
                        (
                            findHome.damage_state == 'None'
                            or findHome.damage_state == 'Slight'
                        )
                        and findHome.occupancy.lower() == self.property.occupancy.lower()
                        and findHome.bedrooms >= self.property.bedrooms
                        and findHome.value <= self.property.value
                        and findHome.inspected == True
                       )
        print(new_home)
        # Yield both the patience timeout and the housing stock FilterStore get.
        # Wait until one or the other process is completed.
        # Assign the process that is completed first to the variable.
        home_search_outcome = yield find_search_patience | new_home

        # Exit the function if the patience timeout completes before a suitable
        # home is found in the housing stock.
        if home_search_outcome == {find_search_patience: 'Gave up'}:
            self.gave_up_home_search = self.env.now

            # If write_story, note in the story that the entity gave up
            # the search.
            if self.write_story:
                self.story.append(
                    'On day {0:,.0f}, after a {1:,.0f} day search, {2} gave up looking for a new home in the local area. '.format(
                        self.env.now,
                        self.env.now - self.home_search_start,
                        self.name.title()
                        )
                    )
            return

        # If a new home is found before patience runs out place entity's current
        # residence in vacant housing stock -- "sell" the home.
        if self.property:
            yield building_stock.put(self.property)

        # Set the newly found home as the entity's property.
        self.property = home_search_outcome[new_home]

        # Record the time that the housing search ends.
        self.home_search_stop = self.env.now

        # If write_story is True, then write results of successful home search to
        # entity's story.
        if self.write_story:
            self.story.append(
                'On day {0:,.0f}, {1} purchased a {2} at {3} with a value of ${4:,.0f} and ${5:,.0f} of damage. '.format(
                    self.home_search_stop,
                    self.name.title(), self.property.occupancy.lower(),
                    self.property.address,
                    self.property.value,
                    self.property.damage_value
                    )
                )
    
    def occupy(self, duration_prob_dist, callbacks = None):
        """Define process for occupying a residence. Currently the method only
        allows for the case of occupying a property (assigning property as its
        residence). Potentially, eventually need logic that allows for occupying residences 
        that are not it's property.

        Keyword Arguments:
        duration_prob_dist -- A io.DurationProbabilityDistribution object that defines
                                the duration related to how long it takes the entity
                                to occupy a dwelling.
        callbacks -- a generator function containing processes to start after the
                        completion of this process.


        Returns or Attribute Changes:
        self.story -- Summary of process outcome as string.
        self.residence -- Assign the owner's property object as residence.
        """
        calc_duration = random_duration_function(duration_prob_dist)
        
        # Yield timeout equivalent to time required to move back into home.
        yield self.env.timeout(calc_duration())

        # Make the entity's property also their residence
        self.residence = self.property
        
        #If true, write process outcome to story
        if self.write_story:
            self.story.append(
                            "{0} occupied the {1} {2:.0f} days after the event. ".format(
                                                                                            self.name.title(),
                                                                                            self.residence.occupancy.lower(),
                                                                                            self.env.now)
                            )

        if callbacks is not None:
            yield self.env.process(callbacks)
        else:
            pass

class RenterHousehold(Household):
    """The RenterHousehold() class has attributes of both entities.Entity() and 
    entities.Household() classes. The class does not have associated property, but
    does have an associated landlord (entities.Landlord() object). So RenterHousehold()
    objects can have both residences and landlords assigned and unassigned to 
    represent, e.g., evictions.
    
    Methods:
    replace_home(self, search_patience, building_stock)
    occupy(self, duration_prob_dist, callbacks = None)
    """
    def __init__(self, env, name, attributes_df, building_stock, write_story = False):
        """
        Keyword Arguments:
        env -- Pointer to SimPy env environment.
        name -- A string indicating the entities name.
        attributes_df -- Dataframe row w/ entity input attributes.
        building_stock -- a SimPy FilterStore that acts as an occupied rental stock
        write_story -- Boolean indicating whether to track a entitys story.
        
        Changed Attributes:
        self.landlord -- Assigns a entities.Landlord() object based on attributes_df 
        self.story -- If write_story == True, append story strings.
        
        Inheritance:
        Subclass of entities.Household()
        """

        # Attributes
        self.landlord = Landlord(env, attributes_df['Landlord'], self, attributes_df, 
                                    building_stock, write_story)

        # Initial method calls; This needs to go after landlord assignment.
        Household.__init__(self, env, name, attributes_df, self.landlord.property, 
                                                                        write_story)

        if self.write_story:
            # Set story with non-disaster attributes.
            self.story.append(
            '{0} rents and lives in a {1} room {2} at {3} worth ${4:,.0f}. '.format(
                                                            self.name,
                                                            self.residence.bedrooms,
                                                            self.residence.occupancy.lower(),
                                                            self.residence.address,
                                                            self.residence.value
                                                            )
                                )

    def replace_home(self, search_patience, building_stock):
        """A process (generator) representing RenterHousehold search for rental housing
        based on housing preferences, available rental stock, and patience for finding
        a new home.

        Keyword Arguments:
        search_patience -- The search duration in which the entity is willing to wait
                            to find a new home. Does not include the process of
                            securing money.
        building_stock -- A SimPy FilterStore that contains one or more
                        residential building objects (e.g., structures.SingleFamilyResidential
                        that represent vacant homes for rent.

        Returns or Attribute Changes:
        self.story -- Process outcomes appended to story.
        self.home_search_start -- Record time home search starts
        self.home_search_stop -- Record time home search stops
        self.residence -- Potentially assigned a new structures.Residence() object.
        self.gave_up_home_search -- Set with env.now to indicate if and when 
                                    search patience runs out.
        """
        # Record when housing search starts
        # Calculate the time that housing search patience ends
        # If write_story, write search start time to entity's story
        self.home_search_start = self.env.now
        patience_end = self.home_search_start + search_patience

        # Define timeout process representing entity's *remaining* search patience.
        # Return 'Gave up' if timeout process completes.
        find_search_patience = self.env.timeout(patience_end - self.env.now,
            value='Gave up')

        # Define a FilterStore.get process to find a new home to rent from the vacant
        # for rent stock with similar attributes as current home.

        # Need to handle eviction case (.prior_residence) and non-eviction case (.residence)
        if self.residence != None:
            if self.write_story:
                self.story.append(
                    '{0} started searching for a new {1} {2:,.0f} days after the event. '.format(
                    self.name.title(), self.residence.occupancy.lower(),
                    self.home_search_start)
                    )
            new_home = building_stock.get(lambda findHome:
                            (
                                findHome.damage_state == 'None'
                                or findHome.damage_state == 'Slight'
                            )
                            and findHome.occupancy.lower() == self.residence.occupancy.lower()
                            and findHome.bedrooms >= self.residence.bedrooms
                            and findHome.cost <= self.residence.cost
                            and findHome.inspected == True
                           )
        else:
            if self.write_story:
                self.story.append(
                    '{0} started searching for a new {1} {2:,.0f} days after the event. '.format(
                    self.name.title(), self.prior_residence[-1].occupancy.lower(),
                    self.home_search_start)
                    )
            new_home = building_stock.get(lambda findHome:
                            (
                                findHome.damage_state == 'None'
                                or findHome.damage_state == 'Slight'
                            )
                            and findHome.occupancy.lower() == self.prior_residence[-1].occupancy.lower()
                            and findHome.bedrooms >= self.prior_residence[-1].bedrooms
                            and findHome.cost <= self.prior_residence[-1].cost
                            and findHome.inspected == True
                           )

        # Yield both the patience timeout and the housing stock FilterStore get.
        # Wait until one or the other process is completed.
        # Assign the process that is completed first to the variable.
        home_search_outcome = yield find_search_patience | new_home

        # Exit the function if the patience timeout completes before a suitable
        # home is found in the housing stock.
        if home_search_outcome == {find_search_patience: 'Gave up'}:
            self.gave_up_home_search = self.env.now

            # If write_story, note in the story that the entity gave up
            # the search.
            if self.write_story:
                self.story.append(
                    'On day {0:,.0f}, after a {1:,.0f} day search, {2} gave up looking for a new home in the local area. '.format(
                        self.env.now,
                        self.env.now - self.home_search_start,
                        self.name.title()
                        )
                    )
            return

        # If a new home is found before patience runs out place entity's current
        # residence in vacant housing stock -- "sell" the home.
        if self.residence != None:
            yield building_stock.put(self.residence)

        # Set the newly found home as the entity's property.
        self.residence = home_search_outcome[new_home]

        # Record the time that the housing search ends.
        self.home_search_stop = self.env.now

        # If write_story is True, then write results of successful home search to
        # entity's story.
        if self.write_story:
            self.story.append(
                'On day {0:,.0f}, {1} leased a {2} at {3} with a rent of ${4:,.0f}. '.format(
                    self.home_search_stop,
                    self.name.title(), self.residence.occupancy.lower(),
                    self.residence.address,
                    self.residence.cost,
                    self.residence.damage_value
                    )
                )
    def occupy(self, duration_prob_dist, callbacks = None):
        """A process for a RenterHousehold to occupy a residence.
        At the moment all this does is represent some duration it takes for the 
        entity to move into a new residence. Potentially eventually can add logic
        related to, e.g., rent increases.

        Keyword Arguments:
        duration_prob_dist -- A io.DurationProbabilityDistribution object that defines
                                the duration related to how long it takes the entity
                                to occupy a dwelling.
        callbacks -- a generator function containing processes to start after the
                        completion of this process.


        Returns or Attribute Changes:
        self.story -- Summary of process outcome as string.
        """

        calc_duration = random_duration_function(duration_prob_dist)
        
        ####
        #### Hopefully put code here for checking if renter can still afford
        #### the rent. Obviously need a function somewhere that estimates rent increases.
        #### 
        
        # Yield timeout equivalent to time required to move back into home.
        yield self.env.timeout(calc_duration())

        #If true, write process outcome to story
        if self.write_story:
            self.story.append(
                            "{0} occupied the {1} {2:.0f} days after the event. ".format(
                                                                                    self.name.title(),
                                                                                    self.residence.occupancy.lower(),
                                                                                    self.env.now)
                            )

        if callbacks is not None:
            yield self.env.process(callbacks)
        else:
            pass

class Landlord(Owner):
    """A Landlord() class is a subclass of entiites.Owner() but has an attributes
    that allows it to have a tenant (e.g., entities.RenterHousehold). Otherwise, 
    currently the same as entities.Owner().

    """
    def __init__(self, env, name, tenant, attributes_df, building_stock, write_story = False):
        """Define landlord's inputs and outputs attributes.
        Initiate landlord's story list string.

        Keyword Arguments:
        env -- Pointer to SimPy env environment.
        name -- A string indicating the entities name.
        tenant -- An entity object as the landlord's tenant (e.g., entities.RenterHousehold)
        attributes_df -- Dataframe row w/ entity input attributes.
        building_stock -- a SimPy FilterStore that acts as an occupied building stock.
                        The owner's property is added to the occupied building stock.
        write_story -- Boolean indicating whether to track a entitys story.
        
        Inheritance:
        Subclass of entities.Owner()
        """
        Owner.__init__(self, env, name, attributes_df, building_stock, write_story)

        # Landlord env inputs
        self.tenant = tenant

        # Initial method calls
        if self.write_story:
            # Set story with non-disaster attributes.
            self.story.append(
                '{0} rents out a {1} bedroom {2} at {3} worth ${4:,.0f}. '.format(
                                                        self.name,
                                                        self.property.bedrooms,
                                                        self.property.occupancy.lower(),
                                                        self.property.address,
                                                        self.property.value
                                                        )
                                )

def importHouseholds(env, building_stock, entities_df, write_story = False):
    """Return list of entities.Household() objects from dataframe containing
    data describing entities' attributes.

    Keyword Arguments:
    env -- Pointer to SimPy env environment.
    building_stock -- a SimPy FilterStore that acts as an occupied building stock.
    entities_df -- Dataframe row w/ entity input attributes.
    write_story -- Boolean indicating whether to track a entitys story.
    """

    entitys = []

    # Population the env with entitys from the entitys dataframe
    for i in entities_df.index:
        entitys.append(Household(env, building_stock, entities_df.iloc[i], write_story))
    return entitys


def importOwnerHouseholds(env, building_stock, entities_df, write_story = False):
    """Return list of entities.OwnerHouseholds() objects from dataframe containing
    data describing entities' attributes.

    Keyword Arguments:
    env -- Pointer to SimPy env environment.
    building_stock -- a SimPy FilterStore that acts as an occupied building stock.
    entities_df -- Dataframe row w/ entity input attributes.
    write_story -- Boolean indicating whether to track a entitys story.
    """
    owners = []

    # Population the env with entitys from the entitys dataframe
    for i in entities_df.index:
        owners.append(OwnerHousehold(env, entities_df.iloc[i]['Name'], entities_df.iloc[i], building_stock, write_story))
    return owners

def importRenterHouseholds(env, building_stock, entities_df, write_story = False):
    """Return list of entities.RenterHousehold() objects from dataframe containing
    dataframe describing entities' attributes.

    Keyword Arguments:
    env -- Pointer to SimPy env environment.
    building_stock -- a SimPy FilterStore that acts as an occupied building stock.
    entities_df -- Dataframe row w/ entity input attributes.
    write_story -- Boolean indicating whether to track a entitys story.
    """
    renters = []

    # Population the env with entitys from the entitys dataframe
    for i in entities_df.index:
        renters.append(RenterHousehold(env, entities_df.iloc[i]['Name'], entities_df.iloc[i], building_stock, write_story))
    return renters
