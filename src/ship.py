# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 14:17:11 2024

@author: ACER
"""

class Ship():
    def __init__(self, size: int) -> None:
        self.size: int = size
        self.rotate: bool = False # True = vertical, False = horizontal
        self.pos: list[tuple[int, int]] = []
        

s = ship(3)
print(s.pos)