# -*- coding: utf-8 -*-
"""
Created on Wed Jan 20 14:14:36 2016

@author: Derek
"""

from desaster import config
#from matplotlib.pyplot import hist
def view_config():
    var = vars(config)
    conf = dir(config)
    result = {}
    for i in conf:
        if "__" not in i and "random" not in i:
            print ("{} = {}".format(i, var[i]))
            #print (i)
            result[i] = var[i]
            
        else:
            pass
    return result
        
#Commented out until i figure out the backend problem
"""        
def view_hist_plot(ent, thing):
    #thing is the variable we want to track. its a string
    #entity is the entity container full of objects
    plot_list = []
    for i in ent:
        plot_list.append(ent[i].__getattribute__(thing))
        plot_list.sort()
        
    return hist(plot_list, bins = 30)
    """