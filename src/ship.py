# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 14:17:11 2024

@author: ACER
"""
from typing import List, Tuple


class Ship():
    def __init__(self, size: int, rotated: bool) -> None:
        self.size: int = size
        self.isRotated: bool = rotated # True = vertical, False = horizontal
        self.pos: List[Tuple[int, int]] = []
