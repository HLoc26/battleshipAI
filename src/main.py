# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 14:38:44 2024

@author: ACER
"""

from grid import Grid
from ship import Ship
import os
import numpy as np
import random 

GRID_SIZE = 10

g = Grid(GRID_SIZE)

# s1 = Ship(3, True)
# s2 = Ship(2, False)

# g.add_ship(s1, (4, 5))
# g.add_ship(s2, (0, 9))

shipCount = 3
for ship in range(shipCount):
    shipSize = random.randint(1, 9)
    shipXPos = random.randint(0, 9)
    shipYPos = random.randint(0, 9)
    shipRotate = random.randint(0, 1)
    newShip = Ship(shipSize, shipRotate)
    if g.add_ship(newShip, (shipXPos, shipYPos)):
        print(f"Placed ship size {shipSize} at ({shipXPos}, {shipYPos}) {"vertically" if shipRotate else "horizontally"}")
    else:
        print(f"Failed to place ship size {shipSize} at ({shipXPos}, {shipYPos}) {"vertically" if shipRotate else "horizontally"}")
        break
print(g.grid)
print(g.shipPos)

curGrid = np.zeros((GRID_SIZE, GRID_SIZE), )
while True:
    print("===== BATTLESHIP =====")
    print(curGrid)
    print("Input -10 for hint")
    atk = tuple(map(int, input("Attack (\"x y\"): ").split()))
    if atk[0] == -1:
        print("exit")
        break
    elif atk[0] == -10:
        print("HINT: ", list(g.shipPos)[0])
        atk = tuple(map(int, input("Attack (\"x y\"): ").split()))
    shot = g.shoot(atk)
    
    os.system("cls")        
    if shot == 1:
        print("HIT")
        curGrid[atk[0]][atk[1]] = -1
    elif shot == 0:
        print("MISS")
        curGrid[atk[0]][atk[1]] = -1
    else:
        print("INVALID")
    if len(g.shipPos) == 0:
        print("VICTORY")
        print(g.grid)
        input("Press any key to exit")