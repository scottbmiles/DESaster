# -*- coding: utf-8 -*-
"""
Created on Wed Jan 6 09:44:46 2016

@author: dhuling

"""
import random, pprint
import simpy
env = simpy.Environment()
class Structure(object):
    
    def __init__(self, structure, _type):
        self.uid = structure
        if _type == None:
            self.type = random.choice(["House", "Business", "Public"])
        else:
            self.type = _type
        self.value = random.randint(60000, 1000000)
        self.damage = random.randint(1, 100000)
        self.bedrooms = random.randint(1, 4)
        
inputs = [x for x in range(15)]
structures = [Structure(x, None) for x in inputs]
def name():
    for i in range(11, 100):
        yield i
a = name()

housing_stock = simpy.FilterStore(env)
for i in structures:
    housing_stock.put(i)
   
def sell(env):
    yield env.timeout(4)
    yield housing_stock.put(Structure(next(a), "House"))
#Here i envision this being a method in the household entity class. The bedroom
#requirements and that stuff would be an attribute of the household's need.
def search(env, name):
    
    g = yield housing_stock.get(lambda filt: filt.type == "House" and filt.bedrooms >= 2)
    yield env.timeout(0.25)
    print('{2} recieved {0} at {1}'.format(g.uid, env.now, name))
    #print name, g.uid, env.now
    
names = ["a","b","c","d","e","f","g","h","i","j"]
for i in names:
    env.process(search(env, i))

env.process(sell(env))

env.run(until=10)

for i in housing_stock.items:
    pprint.pprint([i.type, i.value, i.damage, i.bedrooms])

"""
for j in housing_stock.get_queue:
    pprint.pprint([j.type, j.value, j.damage, j.bedrooms])    
#print housing_stock.get_queue"""

print("There are {0} households still waiting for housing".format(len(housing_stock.get_queue)))

