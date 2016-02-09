# -*- coding: utf-8 -*-
"""
Created on Fri Jan 15 11:01:41 2016

@author: Derek
"""

def kwarg_test(something, **kwargs):
    print kwargs
    for name, value in kwargs.items():
        print "{0}:{1}".format(name,value)
        
        
kwarg_test(1, name="mikey", dan="dane")

from _requests.request_inspection import request_inspection
request_inspection()