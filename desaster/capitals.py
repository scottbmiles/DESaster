# -*- coding: utf-8 -*-
"""
Module of classes that represent different types of capitals used by DESaster
entities.

DESaster capitals are basically fancy wrappers of SimPy resources, containers,
stores.

Classes:
HumanCapital(object)
FinancialCapital(object)
BuiltCapital(object)
Building(BuiltCapital)
Residence(Building)

Functions:
setHousingStock(simulation, stock_df)

@author: Derek Huling, Scott Miles
"""
from simpy import Resource, Container, FilterStore
from desaster.config import structural_damage_ratios
from desaster.config import acceleration_damage_ratios
from desaster.config import drift_damage_ratios
from desaster import config
from scipy.stats import uniform, beta, weibull_min

class ProgramDuration(object):
    def __init__(self, dist='scalar', loc=0.0, scale=None, shape_a=None, shape_b=None):
        self.dist = dist
        self.loc = loc
        self.scale = scale
        self.shape_a = shape_a
        self.shape_b = shape_b

class RecoveryProgram(object):
    def __init__(self, simulation, duration=None, staff=float('inf'), budget=float('inf'),
                    max_outlay=float('inf'), max_income=float('inf'), deductible=0.0,
                    interest_rate=0.0):
        
        self.staff = Resource(simulation, capacity=staff)
        self.budget = Container(simulation, init=budget)
        self.max_outlay = max_outlay
        self.max_income = max_income
        self.deductible = deductible
        self.interest_rate = interest_rate
        
        try:
            if duration.dist == "scalar" or duration == None:
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

                
class BuiltCapital(object):
    """Define top-level class for representing the attributes and methods
    of types of built capital.

    """
    def __init__(self, simulation, asset):
        """Run initial methods for defining built capital attributes.
        
        Keyword Arguments:
        simulation -- Pointer to SimPy simulation environment.
        asset -- A dataframe row with required built capital attributes.
        """
        self.setYearBuilt(asset)
        self.setValue(asset)
        self.setDamageState(asset)
        self.setInspection(asset)
    def setYearBuilt(self, asset):
        self.age = asset['Year Built']  # Year asset was built
    def setValue(self, asset):
        self.value = asset['Value']  # Value of the asset in $
    def setDamageState(self, asset):
        self.damage_state = asset['Damage State']  # HAZUS damage state
    def setInspection(self, asset):
        self.inspected = False  # Whether the asset has been inspected

class Building(BuiltCapital):
    """Define class that inherits from BuiltCapital() for representing the
    attributes and methods of types of buildings.
    """
    def __init__(self, simulation, building):
        """Run initial methods for defining building attributes.
        
        Keyword Arguments:
        simulation -- Pointer to SimPy simulation environment.
        building -- A dataframe row with required building attributes.
        """
        #since we're overriding the base class init, we need to call it 
        #to maintain its attributes, unless we're explicitely changing
        #the structure
        BuiltCapital.__init__(self, simulation, building)
        
        
        self.setAddress(building)
        self.setOccupancy(building)
        self.setDamageValue(building)
        self.setCoordinates(building)
        self.setBuildingArea(building)
       
        self.owner = []  # Owner of building as Household() entity %***%
        self.occupant = [] # %***%
        
        self.cost = building['Cost']  # Monthly rent/mortgage of building
        
    def setAddress(self, building):
        self.address = building['Address']  # Address of building
        try: #if address isn't in dataframe, we'll just set it to none
            self.address = building['Address']  # Address of building
        except KeyError as e:
            self.address = None
    
    def setCoordinates(self, building):
        try: #if lat/long aren't in data, we'll set to none
            self.latitude = building['Latitude']
            self.longitude = building['Longitude']
        except KeyError as e:
            self.latitude = None
            self.longitude = None
    
    def setOccupancy(self, building):
        self.occupancy = building['Occupancy']  # Occupancy type of building
    
    def setBuildingArea(self, building):
        self.area = building['Area']  # Floor area of building
    
    def setDamageValue(self, building):
        """Calculate damage value for building based on occupancy type and
        HAZUS damage state.

        Function uses three lookup tables (Table 15.2, 15.3, 15.4) from the HAZUS-MH earthquake model
        technical manual for structural damage, acceleration related damage,
        and for drift related damage, respectively. Estimated damage value for
        each type of damage is summed for total damage value.
        http://www.fema.gov/media-library/assets/documents/24609
        
        Keyword Arguments:
        structural_damage_ratios -- dataframe set in config.py
        acceleration_damage_ratios -- dataframe set in config.py
        drift_damage_ratios -- dataframe set in config.py
        """
        struct_repair_ratio = structural_damage_ratios.ix[building['Occupancy']][building['Damage State']] / 100.0
        accel_repair_ratio = acceleration_damage_ratios.ix[building['Occupancy']][building['Damage State']] / 100.0
        drift_repair_ratio = drift_damage_ratios.ix[building['Occupancy']][building['Damage State']] / 100.0
        self.damage_value = building['Value']*(struct_repair_ratio +
                                                accel_repair_ratio +
                                                drift_repair_ratio)

class Residence(Building):
    """Define class that inherits from Building() for representing the
    attributes and methods of types of residences.
    """
    def __init__(self, simulation, residence):
        """Run initial methods for defining residence attributes.

        Keyword Arguments:
        simulation -- Pointer to SimPy simulation environment.
        residence -- A dataframe row with required residence attributes.
        """
        
        Building.__init__(self, simulation, residence) # %***%s
        
        self.setOccupancy(residence)
        self.setBedrooms(residence)
        self.setBathrooms(residence)
       
        # self.id = residence["ID Number"] # Derek's addition. Not sure why.
    def setOccupancy(self, residence):
        # Verify that residence dataframe has expected occupancy types
        if residence['Occupancy'] in ('Single Family Dwelling',
                            'Multi Family Dwelling', 'Mobile Home', 'Condo'):
            self.occupancy = residence['Occupancy']
        else:
            raise AttributeError(residence['Occupancy'])
    def setBedrooms(self, residence):
        self.bedrooms = residence['Bedrooms']  # Number of bedrooms in residence
    def setBathrooms(self, residence):
        self.bathrooms = residence['Bathrooms']  # Number of bathrooms in residence

def importHousingStock(simulation, stock_df):
    """Define, populate and return a SimPy FilterStore with Residence() objects to
    represent a vacant housing stock.
    
    Keyword Arguments:
    simulation -- Pointer to SimPy simulation environment.
    stock_df -- Dataframe with required attributes for each vacant home in
                the stock.
    """
    stock_fs = FilterStore(simulation)

    for i in stock_df.index:
        stock_fs.put(Residence(simulation, stock_df.loc[i]))

    return stock_fs
    
def reloadBuildingMaterial(simulation, building_material, amount=2000000):
    yield building_material.put(amount)