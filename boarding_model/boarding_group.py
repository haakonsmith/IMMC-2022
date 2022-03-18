from os import stat
from typing import List, Tuple
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector

import math
import random
import copy
from operator import itemgetter
import numpy as np

from boarding_model.agent import AgentStates, BoardingAgent

class BoardingGroup():
    def __init__(self, y_offset=0, aisle_extent=0, width=7, height=10) -> None:
        self.aisle = 3
        self.width = width
        self.height = height + y_offset
        self.y_offset = y_offset
        self.aisle_extent = aisle_extent

        self.targets = self.generate_targets()

    def generate_targets(self) -> List[Tuple[int, int]]:
        targets = []

        width_offset = self.width // 2

        for y in range(2 + self.y_offset, self.height - 1):
            for x in range(self.width):
                if x <= width_offset + self.aisle_extent and x >= width_offset - self.aisle_extent:
                    continue
                target_seat = (x, y)

                targets.append(target_seat)

        return targets

    def xor(self, other):
        result = []

        for target in other.targets:
            if not target in self.targets:
                result.append(target)

        res = copy.copy(other)
        res.targets = result

        return res

class BoardingGroupRandomiser():
    # Takes percentage as a float from (0-1)
    def __init__(self, percentage: float = 0.05 ) -> None:
        self.percentage = percentage

    @staticmethod
    def count_targets(boarding_class: List[BoardingGroup]):
        sum = 0

        for cls in boarding_class:
            sum += len(cls.targets)

        return sum

    # Determines a value for k based on self.percent of the total number of targets
    def determine_k(self, boarding_class: List[BoardingGroup]) -> int:
        total = BoardingGroupRandomiser.count_targets(boarding_class)

        return math.floor(total * self.percentage)

    def shuffle_boarding_class(self, boarding_class: List[BoardingGroup]):
        lists = list(map(lambda x: x.targets, boarding_class))
        result = {}
      
        for i, l in enumerate(lists):
            for j, target in enumerate(l):
                result[target] = (i, j)

        targets = random.sample(result.keys(), k=self.determine_k(boarding_class))
        bacl = itemgetter(*targets)(result)
        k_shuffled = random.sample([*itemgetter(*targets)(result)], k=len(bacl))

        for i, target in enumerate(targets):
            print(target, k_shuffled[i])
            result[target] = k_shuffled[i]


        for target, class_index in result.items():
            boarding_class[class_index[0]].targets[class_index[1]] = target
