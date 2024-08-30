# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 14:22:07 2024

@author: ACER
"""
import numpy as np
from typing import List, Tuple, Set
from ship import Ship



class Grid():
    def __init__(self, GRID_SIZE: int) -> None:
        self.GRID_SIZE: int = GRID_SIZE
        self.grid: np.ndarray = np.zeros((GRID_SIZE, GRID_SIZE))
        self.shipPos: Set[Tuple[int, int]] = set()
        self.shotSquares: Set[Tuple[int, int]] = set()

    def add_ship(self, ship: Ship, pos: Tuple[int, int]) -> bool:
        '''
        Add ship to the grid.
    
        :param ship: The Ship object.
        :param pos: the position where the user clicks to place the ship.
        :returns: True if placed successfully, False otherwise.
        :raises IndexError: When the ship is placed out of the grid, raise error.
        '''
        def check_placeable(xPos: int, yPos: int) -> bool:
            '''Check if the position is empty to place.'''
            curPos: Tuple[int, int] = (xPos, yPos)
            if curPos not in self.shipPos:
                return True
            return False

        def get_positions(ship: Ship, pos: Tuple[int, int]) -> List[Tuple[int, int]]:
            '''Returns squares which the ship is placed on.'''
            positions: List[Tuple[int, int]] = []
            for i in range(ship.size):
                xPos: int = pos[0] + i if ship.isRotated else pos[0]
                yPos: int = pos[1] if ship.isRotated else pos[1] + i
                if xPos >= self.GRID_SIZE:
                    xPos = self.GRID_SIZE - 1 - i
                elif yPos >= self.GRID_SIZE:
                    yPos = self.GRID_SIZE - 1 - i
                canBePlaced: bool = check_placeable(xPos, yPos)
                if canBePlaced: 
                    positions.append((xPos, yPos))
                else:
                    return []
            return positions
        
        curShipPos: List[Tuple[int, int]] = get_positions(ship, pos)
        if len(curShipPos) == 0:
            return False
        for pos in curShipPos:
            ship.pos.append(pos)
            self.grid[pos[0]][pos[1]] = 1
            self.shipPos.add(pos)
        return True

    def shoot(self, attackPos: Tuple[int, int]) -> int:
        '''Return True if hit, else return False
        
        :param pos: The position to attack.
        :returns: 1 if hit, 0 if miss, -1 if invalid attack.
        :raise IndexError: If player attack outside of grid.
        '''
        try:
            if attackPos[0] < 0 or attackPos[1] < 0 or attackPos[0] >= self.GRID_SIZE or attackPos[1] >= self.GRID_SIZE:
                raise IndexError("Attack out of range.")
            self.shotSquares.add(attackPos)
            xPos = attackPos[0]
            yPos = attackPos[1]
            self.grid[xPos][yPos] = -1
            if attackPos in self.shipPos:
                self.shipPos.remove(attackPos)
                return 1 # Hit
            return 0 # Miss
        except IndexError as e:
            print(e)
            return -1 # Invalid

