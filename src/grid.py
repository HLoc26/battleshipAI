# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 14:22:07 2024

@author: ACER
"""
import numpy as np

class Grid():
    def __init__(self, GRID_SIZE: int) -> None:
        self.GRID_SIZE = GRID_SIZE
        self.grid = np.zeros((GRID_SIZE, GRID_SIZE))

g = Grid(10)

print(g.grid)