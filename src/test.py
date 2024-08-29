# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 13:55:22 2024

@author: ACER
"""

GRID_SIZE = 10

my_ships_pos = [(0, 1), (0, 2), (4, 5), (5, 5), (6, 5)]

my_board = [" _" * GRID_SIZE]
cols = ["  "] + [i for i in range(GRID_SIZE)]
print(*cols)
for i in range(GRID_SIZE):
    print(i, end=' ')
    for j in range(GRID_SIZE):
        if (i, j) in my_ships_pos:
            print("X", end=' ')
        else:
            print("_", end=' ')
    print()
