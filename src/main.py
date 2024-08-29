# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 14:38:44 2024

@author: ACER
"""

from grid import Grid
from ship import Ship

GRID_SIZE = 10

g = Grid(GRID_SIZE)

s1 = Ship(3, True)
s2 = Ship(5, False)

g.add_ship(s2, (0, 9))

print(g.grid)
