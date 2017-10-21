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

@author: Scott Miles (milessb@uw.edu)
"""
from desaster.structures import SingleFamilyResidential, Building
from desaster.hazus import setContentsDamageValueHAZUS
import names, warnings, sys
from simpy import Container

class Entity(object):
    """A base class for representing entities, such as households, businesses,
    agencies, NGOs, etc.

    Methods:
    __init__(self, env, name, write_story = False)
    story_to_text()
    
    """
    def __init__(self, env, name = None, savings = 0, insurance = 0, credit = 0, write_story = False):
        """Initiate an Entity object

        Keyword Arguments:
        env -- Pointer to SimPy env environment.
        name -- A string indicating the entities name.
        savings -- Amount of entity savings in $ 
        insurance -- Hazard-specific insurance coverage: coverage / residence.value
        credit -- A FICO-like credit score
        write_story -- Boolean indicating whether to track an entity's story.
        
        Modified Attributes
        self.recovery_funds -- initiated with value of self.savings
        """
        self.env = env

        # Entity attributes
        self.name = name   # Name associated with occupant of the home %***%
        self.write_story = write_story # Boolean. Whether to track the entity's story.
        self.insurance = insurance  # Hazard-specific insurance coverage: coverage / residence.value
        self.savings = savings  # Amount of entity savings in $
        self.credit = credit # A FICO-like credit score
        
        # Entity outputs
        self.story = []  # The story of events for each entity
        self.claim_put = None  # Time put request in for insurance settlement
        self.claim_get = None  # Time get insurance claim settled
        self.claim_amount = 0.0  # Amount of insurance claim payout
        self.fema_put = None  # Time put request in for FEMA assistance
        self.fema_get = None  # Time get FEMA assistance
        self.fema_amount = 0.0  # Amount of assistance provided by FEMA
        self.sba_put = None  # Time put request for loan
        self.sba_get = None  # Time get requested loan
        self.sba_amount = 0.0  # Amount of loan received
        
        try:
            self.recovery_funds = Container(env, init=self.savings)  # Total funds available to entity to recover; must be > 0
        except:
            self.recovery_funds = Container(env, init=1)  # init must be > 0

    def story_to_text(self):
        """Join list of story strings into a single story string."""
        return ''.join(self.story)

class Owner(Entity):
    """An class that inherits from the Entity() class to represent any entity
    that owns property.  An owner does not necessarily have a residence (e.g., 
    landlord). For the most part this is class is to define subclasses with Owner() 
    attributes.

    Methods:
    __init__(self, env, name, attributes_df, building_stock, write_story = False)
    """
    def __init__(self, env, name = None, savings = 0, insurance = 0, credit = 0, real_property = None, write_story = False):
        """Initiate several attributes related to an Owner entity.
        No universal methods have been define for the Owner class yet. methods
        are currently specified in subclasses of Owner.

        Keyword Arguments:
        env -- Pointer to SimPy env environment.
        name -- A string indicating the entities name.
        savings -- Amount of entity savings in $ 
        insurance -- Hazard-specific insurance coverage: coverage / residence.value
        credit -- A FICO-like credit score
        real_property -- A building object, such as structures.SingleFamilyResidential()

        write_story -- Boolean indicating whether to track an entity's story.
        
        
        Inheritance:
        Subclass of entities.Entity()
        """
        Entity.__init__(self, env, name, savings, insurance, credit, write_story)

        # Attributes
        self.property = real_property # A building object from desaster.structures

        # Owner env outputs
        self.inspection_put = None  # Time put request in for house inspection
        self.inspection_get = None  # Time get  house inspection

        self.assistance_payout = 0.0  # Amount of generic assistance provided (e.g., Red Cross)
        self.repair_put = None  # Time put request in for house repair
        self.repair_get = None  # Time get house repair completed
        self.demolition_put = None # Time demolition requested
        self.demolition_get = None  # Time demolition occurs

        self.permit_put = None  # Time put request for building permit
        self.permit_get = None  # Time get requested building permit
        self.assessment_put = None  # Time put request for engineering assessment
        self.assessment_get = None  # Time put request for engineering assessment
        self.gave_up_funding_search = None  # Time entity gave up on some funding
                                            # process; obviously can't keep track
                                            # of multiple give ups
        self.prior_properties = [] # A list to keep track of entity's previous properties



class Household(Entity):
    """Define a Household() class to represent a group of persons that reside
    together in a single dwelling unit. A Household() object can not own property,
    but does have a residence. For the most part this is class is to define
    subclasses with Household() attributes. Also includes methods for writing 
    household stories.

    Methods:
    __init__(self, env, name = None, savings = 0, insurance = 0, credit = 0, write_story = False)
    writeResides(self):
    writeResides(self):
    writeResides(self):
    writeOccupy(self):  

    """
    def __init__(self, env, name = None, income = float('inf'), savings = float('inf'), 
                    insurance = 1.0, credit = 850, residence = None, write_story = False):
        """Initiate a entities.Household() object.

        Keyword Arguments:
        env -- Pointer to SimPy env environment.
        name -- A string indicating the entities name.
        savings -- Amount of entity savings in $ 
        insurance -- Hazard-specific insurance coverage: coverage / residence.value
        credit -- A FICO-like credit score
        residence -- A building object, such as structures.SingleFamilyResidential()
                    that serves as the entity's temporary or permanent residence.
        write_story -- Boolean indicating whether to track a entitys story.
        
        Returns or Attribute Changes:
        self.story -- If write_story == True, append entity story strings
        """
        Entity.__init__(self, env, name, savings, insurance, credit, write_story)

        # Attributes
        self.residence = residence
        self.income = income

        # Entity outputs
        self.home_put = None  # Time started searching for a new home
        self.home_get = None  # Time found a new home
        self.gave_up_home_search = None  # Whether entity gave up search for home
        self.occupy_put = None # The time when the entity put's in a request for a home.
                                # None if request never made.
        self.occupy_get = None # The time when the entity receives a home.
                                # None if never received.
        self.prior_residences = [] # An empty list to rsecord each residence that
                                    # the entity vacates.

        self.writeResides()
                            
    def writeResides(self):
        if self.write_story:
            self.story.append('{0} resides at {1}. '.format(
                                                self.name, self.residence.address)
                            )
    
    def writeStartSearch(self):    
        if self.write_story:
            self.story.append(
                '{0} started searching for a new {1} {2:,.0f} days after the event. '.format(
                self.name.title(), self.prior_residences[-1].occupancy.lower(), self.home_put)
                )
                
    def writeGaveUp(self):
        if self.write_story:
            self.story.append(
                'On day {0:,.0f}, after a {1:,.0f} day search, {2} gave up looking for a new home in the local area. '.format(
                            self.env.now, self.env.now - self.home_put, self.name.title())
                )  
                
    def writeOccupy(self):            
        if self.write_story:
            self.story.append(
                            "{0} occupied the {1} {2:.0f} days after the event. ".format(
                            self.name.title(), self.residence.occupancy.lower(), self.occupy_get)
                            )      

class OwnerHousehold(Owner, Household):
    """The OwnerHousehold() class has attributes of both entities.Owner() and
    entities.Household() classes. It can own property and has a residence, which
    do not have to be the same. The OwnerHousehold() class includes methods to
    look for a new home to purchase (property), as well as to occupy a residence
    (not necessarily it's property). Also includes methods to write stories.

    Methods:
    replace_home(self, search_patience, building_stock)
    occupy(self, duration, callbacks = None)
    changeListing(self, listed):
    writeInitiateOwnerHousehold(self): 
    writeHomeBuy(self): 
    """
    def __init__(self, env, name = None, income = float('inf'), savings = float('inf'), 
                insurance = 1.0, credit = 850, real_property = None, write_story = False):
        """Define entity inputs and outputs attributes.
        Initiate entity's story list string.

        Keyword Arguments:
        env -- Pointer to SimPy env environment.
        name -- A string indicating the entities name.
        savings -- Amount of entity savings in $ 
        insurance -- Hazard-specific insurance coverage: coverage / residence.value
        credit -- A FICO-like credit score
        real_property -- A building object, such as structures.SingleFamilyResidential()
        residence -- A building object, such as structures.SingleFamilyResidential()
                    that serves as the entity's temporary or permanent residence.
        write_story -- Boolean indicating whether to track an entity's story.
        
        Returns or Attribute Changes:
        self.story -- If write_story == True, append entity story strings
        
        Inheritance:
        entities.Household()
        entities.Owner()
        """
        Owner.__init__(self, env, name, savings, insurance, credit, real_property, write_story)
        Household.__init__(self, env, name, income, savings, insurance, credit, self.property, write_story)

        self.writeInitiateOwnerHousehold()

    def replace_home(self, search_stock, duration, down_payment_pct = 0.10, housing_ratio = 0.3,
                        price_pct = 1.1, area_pct = 0.9, rooms_tol = 0,
                        search_patience = float('inf')):
        """A process (generator) representing entity search for permanent housing
        based on housing preferences, available housing stock, and patience finding
        a new home.

        Keyword Arguments:
        
        search_stock -- A SimPy FilterStore that contains one or more
                        residential building objects (e.g., structures.SingleFamilyResidential)
                        that represent homes owner is searching to purchase.
        duration -- A distributions.ProbabilityDistribution object, KDE_Distribution object
                                    or other type from desaster.distributions
        down_payment_pct -- Percentage of home value required for a down payment
        housing_ratio -- Maximum percentage of monthly income for acceptable monthly costs
        price_pct -- Ratio of existing home value to maximum desirable new home value
        area_pct -- Ratio of existing home area to maximum desirable new home area
        rooms_tol -- Number of fewer or additional bedroms compared to existing home 
                    area that is acceptable for new home
        search_patience -- The search duration in which the entity is willing to wait
                            to find a new home. Does not include the process of
                            securing money.

        Returns or Attribute Changes:
        self.story -- Process outcomes appended to story.
        self.home_put -- Record time home search starts
        self.home_get -- Record time home search stops
        self.residence -- Potentially assigned a new residence object.
        self.property -- Potentially assigned a new property object.
        self.property.list -- Potentially set prior property to True and new one to False
        self.prior_residences -- Potentially append a prior residence object.
        self.prior_properties -- Potentially assigned a prior property object.
        self.gave_up_home_search -- Set with env.now to indicate if and when
                                    search patience runs out.
        self.story -- If write_story == True, append entity story strings
        """
        # Record when housing search starts
        # Calculate the time that housing search patience ends
        # If write_story, write search start time to entity's story
        self.home_put = self.env.now
        patience_end = self.home_put + search_patience

        # Record current residence as prior residence, current property as
        # prior property
        self.prior_properties.append(self.property)
        if self.residence:
            self.prior_residences.append(self.residence)
        
        # Write the story
        self.writeStartSearch()
        
        # Define timeout process representing entity's patience for finding home.
        # Return 'Gave up' if timeout process completes.
        home_search_patience = self.env.timeout(patience_end - self.env.now,
            value='Gave up')
        
        # Define a FilterStore.get process to find a new home to buy from the vacant
        # for sale stock with similar attributes as *original* property.
        new_home = search_stock.get(lambda findHome:
                        findHome.damage_state == 'None'
                        and findHome.occupancy.lower() == self.prior_properties[0].occupancy.lower()
                        and (findHome.bedrooms >= self.prior_properties[0].bedrooms + rooms_tol
                        or findHome.area >= self.prior_properties[0].area * area_pct)
                        and (findHome.value <= self.prior_properties[0].value * price_pct
                        or findHome.monthly_cost <= (self.income / 12.0) * housing_ratio)
                        and findHome.listed == True
                                    )
    
        # Yield both the patience timeout and the housing stock FilterStore get.
        # Wait until one or the other process is completed.
        # Assign the process that is completed first to the variable.
        home_search_outcome = yield home_search_patience | new_home
        
        # Exit the function if the patience timeout completes before a suitable
        # home is found in the housing stock.
        if home_search_outcome == {home_search_patience: 'Gave up'}:
            del self.prior_properties[0] # Didn't replace home, so delete from prior
            del self.prior_residences[0] # Didn't replace home, so delete from prior
            self.gave_up_home_search = self.env.now
            self.writeGaveUp()
            return
        
        # Define timeout process representing entity's *remaining* search patience.
        # Return 'Gave up' if timeout process completes.
        down_payment_patience = self.env.timeout(patience_end - self.env.now,
                                                value='Gave up')

        # Withdraw 10% down payment; wait for more funds if don't have it yet
        down_payment = down_payment_pct * home_search_outcome[new_home].value
        get_down_payment = self.recovery_funds.get(down_payment)
        
        # Yield both the remaining patience timeout and down payment get.
        down_payment_outcome = yield down_payment_patience | get_down_payment
        
        # Exit the function if the patience timeout completes before a suitable
        # home is found in the housing stock.
        if down_payment_outcome == {down_payment_patience: 'Gave up'}:
            yield search_stock.put(home_search_outcome[new_home]) # Didn't buy it afterall
            del self.prior_properties[0] # Didn't replace home, so delete from prior
            del self.prior_residences[0] # Didn't replace home, so delete from prior
            self.gave_up_home_search = self.env.now
            self.writeGaveUp()
            return
        
        # If a new home is found before patience runs out set current property's
        # listed attributed to True -- put home up for sale.
        # get and put from FilterStore to tell SimPy object's state changed
        if self.property:
            self.changeListing(listed = True)
        
        # Take new home off the market and place back in housing stock
        # (in orde for SimPy to register the resource state change)
        self.changeListing(listed = False)
        
        # Take a timeout equal to specified time to close home purchase
        yield self.env.timeout(duration.rvs())
        
        # Set the newly found home as the entity's property.
        self.property = home_search_outcome[new_home]

        # Make the entity's property also their residence
        self.residence = self.property
        
        # Record the time that the housing search ends.
        self.home_get = self.env.now

        # If write_story is True, then write results of successful home search to
        # entity's story.
        self.writeHomeBuy()

    def changeListing(self, listed):
        get_home = yield self.property.stock.get(lambda getHome:
                                                    getHome.__dict__ == self.property.__dict__
                                            )
        self.residence.listed = listed
        yield self.residence.stock.put(get_home)
    
    def occupy(self, duration, callbacks = None):
        """Define process for occupying a residence--e.g., amount of time it takes
        to move into a new residence. Currently the method doesn't do much but
        make story writing simpler.

        Keyword Arguments:
        duration -- A distributions.ProbabilityDistribution object that defines
                                the duration related to how long it takes the entity
                                to occupy a dwelling.
        callbacks -- a generator function containing processes to start after the
                        completion of this process.


        Returns or Attribute Changes:
        self.story -- Summary of process outcome as string.
        self.occupy_put -- Recording beginning of occupany duration.
        self.occupy_get -- Record time of occupancy
        """
        self.occupy_put = self.env.now

        # Yield timeout equivalent to time required to move back into home.
        yield self.env.timeout(duration.rvs())

        # Record time got home
        self.occupy_get = self.env.now

        #If true, write process outcome to story
        self.writeOccupy()

        if callbacks is not None:
            yield self.env.process(callbacks)
        else:
            pass

    def writeInitiateOwnerHousehold(self):    
        if self.write_story:
            # Set story with non-disaster attributes.
            self.story.append(
            '{0} owns and lives in a {1} room {2} at {3} worth ${4:,.0f}. '.format(self.name,
            self.residence.bedrooms, self.residence.occupancy.lower(), self.residence.address,
            self.residence.value)
                                )
    
    def writeHomeBuy(self):    
        if self.write_story:
            self.story.append(
                'On day {0:,.0f}, {1} purchased a {2} at {3} with a value of ${4:,.0f}. '.format(
                self.home_get, self.name.title(), self.property.occupancy.lower(), self.property.address,
                self.property.value)
                            )
                
class RenterHousehold(Household):
    """The RenterHousehold() class has attributes of both entities.Entity() and
    entities.Household() classes. The class does not have associated property, but
    does have an associated landlord (entities.Landlord() object) that owns their 
    residence. So RenterHousehold() objects can have both residences and landlords 
    assigned and unassigned to represent, e.g., evictions.

    Methods:
    replace_home(self, search_patience, building_stock)
    occupy(self, duration, callbacks = None)
    changeListing(self, listed):
    writeInitiateRenterHousehold(self): 
    writeHomeRent(self):  
    """
    def __init__(self, env, name = None, income = float('inf'), savings = float('inf'), insurance = 1.0, credit = 850, 
                    residence = None, landlord = None, write_story = False):
        """Define entity inputs and outputs attributes.
        Initiate entity's story list string.

        Keyword Arguments:
        env -- Pointer to SimPy env environment.
        name -- A string indicating the entities name.
        savings -- Amount of entity savings in $ 
        insurance -- Hazard-specific insurance coverage: coverage / residence.value
        credit -- A FICO-like credit score
        residence -- A building object, such as structures.SingleFamilyResidential()
                    that serves as the entity's temporary or permanent residence.
        landlord -- An Owner object that represent's the renter's landlord.
        write_story -- Boolean indicating whether to track an entity's story.
        
        Returns or Attribute Changes:
        self.story -- If write_story == True, append entity story strings
        self.landlord -- Record renter's landlord
        
        Inheritance:
        Subclass of entities.Household()
        """
        # Attributes
        self.landlord = landlord

        # Initial method calls; This needs to go after landlord assignment.
        Household.__init__(self, env, name, income, savings, insurance, credit, residence, write_story)

        self.writeInitiateRenterHousehold()

    def replace_home(self, search_stock, duration, move_in_ratio = 2.5, housing_ratio = 0.3,
                area_pct = 0.9, rooms_tol = 0, notice_time = 20.0,
                search_patience = float('inf')):

        """A process (generator) representing entity search for permanent housing
        based on housing preferences, available housing stock, and patience finding
        a new home.

        Keyword Arguments:
    
        search_stock -- A SimPy FilterStore that contains one or more
                        residential building objects (e.g., structures.SingleFamilyResidential)
                        that represent homes owner is searching to purchase.
        duration -- A distributions.ProbabilityDistribution object, KDE_Distribution object
                                    or other type from desaster.distributions
        down_payment_pct -- Percentage of home value required for a down payment
        housing_ratio -- Maximum percentage of monthly income for acceptable monthly costs
        move_in_ratio -- A float value that represents move in cost of a new residence
                        as a ratio of the residence's monthly cost (rent).
        area_pct -- Ratio of existing home area to maximum desirable new home area
        rooms_tol -- Number of fewer or additional bedroms compared to existing home 
                    area that is acceptable for new home
        notice_time -- A duration that represents the amount of time between identifying
                        a desirable listing and the availability of the new residence.
        search_patience -- The search duration in which the entity is willing to wait
                            to find a new home. Does not include the process of
                            securing money.

        Returns or Attribute Changes:
        self.story -- Process outcomes appended to story.
        self.home_put -- Record time home search starts
        self.home_get -- Record time home search stops
        self.residence -- Potentially assigned a new residence object.
        self.property.listed -- Potentially set prior property to True and new one to False
        self.prior_residences -- Potentially append a prior residence object.
        self.gave_up_home_search -- Set with env.now to indicate if and when
                                    search patience runs out.
        self.story -- If write_story == True, append entity story strings
        """
        # Record when housing search starts
        # Calculate the time that housing search patience ends
        # If write_story, write search start time to entity's story
        self.home_put = self.env.now
        patience_end = self.home_put + search_patience

        # Put current residence as a prior residence
        if self.residence:
            self.prior_residences.append(self.residence)
        
        # Define timeout process representing entity's *remaining* search patience.
        # Return 'Gave up' if timeout process completes.
        find_search_patience = self.env.timeout(patience_end - self.env.now,
            value='Gave up')

        self.writeStartSearch()
        
        # Define a FilterStore.get process to find a new home to rent from the vacant
        # for rent stock with similar attributes as original residence.
        new_home = search_stock.get(lambda findHome:
                        findHome.damage_state == 'None'
                        and findHome.occupancy.lower() == self.prior_residences[0].occupancy.lower()
                        and (findHome.bedrooms >= self.prior_residences[0].bedrooms + rooms_tol
                        or findHome.area >= self.prior_residences[0].area * area_pct)
                        and findHome.monthly_cost <= (self.income / 12.0) * housing_ratio
                        and findHome.listed == True
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
            self.writeGaveUp()
            return

        # Define timeout process representing entity's *remaining* search patience.
        # Return 'Gave up' if timeout process completes.
        move_in_cost_patience = self.env.timeout(patience_end - self.env.now,
                                                value='Gave up')

        # Withdraw 10% down payment; wait for more funds if don't have it yet
        move_in_cost = move_in_ratio * home_search_outcome[new_home].monthly_cost
        
        get_move_in_cost = self.recovery_funds.get(move_in_cost)
        
        # Yield both the remaining patience timeout and down payment get.
        move_in_cost_outcome = yield move_in_cost_patience | get_move_in_cost
        
        # Exit the function if the patience timeout completes before a suitable
        # home is found in the housing stock.
        if move_in_cost_outcome == {move_in_cost_patience: 'Gave up'}:
            yield search_stock.put(home_search_outcome[new_home]) # Didn't buy it afterall
            # Put current residence as a prior residence
            if self.residence:
                del self.prior_residences[0] # Didn't replace home, so delete from prior
            self.gave_up_home_search = self.env.now
            self.writeGaveUp()
            return
        
        # If a new home is found before patience runs change current residence's 
        # listed state to True to indicate residence is for rent (if tenant has a 
        # residence)
        if self.residence:
            self.changeListing(listed = True)

        # Set the newly found home as the entity's residence.
        self.changeListing(listed = False)
        
        # Take a timeout equal to specified to notice time before can move in
        yield self.env.timeout(duration.rvs())
        
        # Set newly found home as residence
        self.residence = home_search_outcome[new_home]

        # Record the time that the housing search ends.
        self.home_get = self.env.now

        # If write_story is True, then write results of successful home search to
        # entity's story.
        self.writeHomeRent()
        
    def changeListing(self, listed):
        get_home = yield self.residence.stock.get(lambda getHome:
                                                    getHome.__dict__ == self.property.__dict__
                                            )
        self.residence.listed = listed
        yield self.residence.stock.put(get_home)
        
    def occupy(self, duration, callbacks = None):
        """A process for a RenterHousehold to occupy a residence.
        At the moment all this does is represent some duration it takes for the
        entity to move into a new residence. Potentially eventually can add logic
        related to, e.g., rent increases.

        Keyword Arguments:
        duration -- A distribution.ProbabilityDistribution object or 
                                similar that defines the duration related to how 
                                long it takes the entity to occupy a dwelling.
        callbacks -- a generator function containing processes to start after the
                        completion of this process.


        Returns or Attribute Changes:
        self.story -- Summary of process outcome as string.
        self.occupy_put -- Recording beginning of occupany duration.
        self.occupy_get -- Record time of occupancy
        """

        self.occupy_put = self.env.now
        ####
        #### Hopefully put code here for checking if renter can still afford
        #### the rent. Obviously need a function somewhere that estimates rent increases.
        ####

        # Yield timeout equivalent to time required to move back into home.
        yield self.env.timeout(duration.rvs())

        # Record time got home
        self.occupy_get = self.env.now

        self.writeOccupy()

        if callbacks is not None:
            yield self.env.process(callbacks)
        else:
            pass    
        
    def writeInitiateRenterHousehold(self):    
        if self.write_story:
            self.story.append(
            '{0} rents and lives in a {1} room {2} at {3}. '.format(
            self.name, self.residence.bedrooms, self.residence.occupancy.lower(),
            self.residence.address)
                            )                            
            
    def writeHomeRent(self):      
        if self.write_story:
            self.story.append(
                'On day {0:,.0f}, {1} leased a {2} at {3} with a rent of ${4:,.0f}. '.format(
                self.home_get, self.name.title(), self.residence.occupancy.lower(),
                self.residence.address, self.residence.monthly_cost, self.residence.damage_value)
                )                        
                
class Landlord(Owner):
    """A Landlord() class is a subclass of entiites.Owner() but has an attributes
    that allows it to have a tenant (e.g., entities.RenterHousehold). Otherwise,
    similar to entities.Owner().
    
    Methods:
    evict_tenant(self):
    writeInitiateLandlord(self):
    writeEvicted(self):
    """
    def __init__(self, env, name = None, savings = 0, insurance = 0, credit = 0, real_property = None, 
                tenant = None, write_story = False):
        """Define landlord's inputs and outputs attributes.
        Initiate landlord's story list string.

        Keyword Arguments:
        env -- Pointer to SimPy env environment.
        name -- A string indicating the entities name.
        savings -- Amount of entity savings in $ 
        insurance -- Hazard-specific insurance coverage: coverage / residence.value
        credit -- A FICO-like credit score
        real_property -- A building object, such as structures.SingleFamilyResidential()
        tenant -- A RenterHousehold object that serves landlord's tenant
        write_story -- Boolean indicating whether to track an entity's story.
        
        Modified Attributes:
        self.tenant -- Set landlord's tenant
        self.story -- Initiate landlord's story 
        
        Inheritance:
        Subclass of entities.Owner()
        """
        Owner.__init__(self, env, name, savings, insurance, credit, real_property, write_story)

        # Landlord env inputs
        self.tenant = tenant

        self.writeInitiateLandlord()
        
    def evict_tenant(self):
        self.tenant.prior_residences.append(self.tenant.residence)
        self.tenant.residence = None
        
        self.writeEvicted()
        
    def writeInitiateLandlord(self):
        if self.write_story:
            # Set story with non-disaster attributes.
            self.story.append(
                '{0} rents out a {1} bedroom {2} at {3} worth ${4:,.0f}. '.format(
                self.name, self.property.bedrooms, self.property.occupancy.lower(),
                self.property.address, self.property.value)
                                )  
    def writeEvicted(self):
        if self.tenant.write_story == True:
            self.tenant.story.append(
            '{0} was evicted because the {1} had {2} damage. '.format(
                                            self.tenant.name, self.property.occupancy.lower(),
                                            self.property.damage_state.lower()
                                                                                    )
                                        )  

