#!/usr/bin/env python3
from dataclasses import dataclass


@dataclass
class Node:
    id: int
    row: int
    col: int

    @property
    def address(self):
        return self.row, self.col
    
