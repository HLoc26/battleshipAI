# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 14:22:07 2024

@author: ACER
"""
import numpy as np
from typing import List, Tuple
from ship import Ship



class Grid():
    def __init__(self, GRID_SIZE: int) -> None:
        self.GRID_SIZE: int = GRID_SIZE
        self.grid: np.ndarray = np.zeros((GRID_SIZE, GRID_SIZE))
        self.shipPos: List[Tuple[int, int]] = []
        self.shotSquares: List[Tuple[int, int]] = []

    def add_ship(self, ship: Ship, pos: Tuple[int, int]) -> None:
        '''
        Add ship to the grid.
    
        :param ship: The Ship object.
        :param pos: the position where the user clicks to place the ship.
        :returns: None.
        :raises IndexError: When the ship is placed out of the grid, raise error.
        '''
        def place_ship_segment(xPos, yPos):
            '''Helper function to save the ship positions of squares
            
            :param xPos: The x position of square.
            :param yPos: The y position of square.
            :returns: None.
            '''
            curPos = (xPos, yPos)
            ship.pos.append(curPos)
            self.grid[xPos][yPos] = 1
            self.shipPos.append(curPos)
    
        if not ship.isRotated:  # Horizontal ship
            for i in range(ship.size):
                try:
                    xPos = pos[0]
                    yPos = pos[1] + i
                    if yPos >= self.GRID_SIZE:
                        raise IndexError(f"Out of bound, moved from {pos} to.")
                    place_ship_segment(xPos, yPos)
                except IndexError as e:
                    yPos = self.GRID_SIZE - 1 - i
                    print(e, (xPos, yPos))
                    place_ship_segment(xPos, yPos)
    
        else:  # Vertical ship
            for i in range(ship.size):
                try:
                    xPos = pos[0] + i
                    yPos = pos[1]
                    if xPos >= self.GRID_SIZE:
                        raise IndexError(f"Out of bound, moved from {pos} to.")
                    place_ship_segment(xPos, yPos)
                except IndexError as e:
                    xPos = self.GRID_SIZE - 1 - i
                    print(e, (xPos, yPos))
                    place_ship_segment(xPos, yPos)

                
    def shot(self, pos: Tuple[int, int]) -> int:
        '''Return True if hit, else return False
        
        :param pos: The position to attack.
        :returns: 1 if hit, 0 if missed, -1 if invalid attack.
        :raise IndexError: If player attack outside of grid.
        '''
        try:
            if pos[0] < 0 or pos[1] < 0 or pos[0] >= self.GRID_SIZE or pos[1] >= self.GRID_SIZE:
                raise IndexError("Attack out of range.")
        except IndexError as e:
            print(e)
            return -1
        