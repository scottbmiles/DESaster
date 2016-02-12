# -*- coding: utf-8 -*-
"""
Created on Wed Jan 20 14:14:36 2016

@author: Derek
"""

from desaster import config

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
        
