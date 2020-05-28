#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 23:19:06 2020

@author: luiz
"""

from . import keyDef

class individuum:
    # id:
    ident = None
    
    # pointers to other individuals:
    pater = None # format self
    mater = None # format self
    
    # name data:
    nomen = None # format tuple/list of strings. Each string is a first name or surname
    
    # other data:
    natalis = None # format (pandas?) date
    mortis = None # format (pandas?) date
    locNatalis = None
    
    
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if key == keyDef.ident:
                self.ident = value
            if key == keyDef.nomen:
                self.nomen = value
            if key == keyDef.pater:
                self.pater = value
            if key == keyDef.mater:
                self.mater = value
            if key == keyDef.natalis:
                self.natalis = value
            if key == keyDef.mortis:
                self.mortis = value
            if key == keyDef.locNatalis:
                self.locNatalis = value
                
