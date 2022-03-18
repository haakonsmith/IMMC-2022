from os import stat
from typing import List, Tuple
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector

import math
import random
import copy
import numpy as np

from operator import itemgetter

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
        # result.targets.clear()

        for target in other.targets:
            if not target in self.targets:
                result.append(target)

        res = copy.copy(other)
        res.targets = result

        return res


top_to_bottom_boarding_class = [
    BoardingGroup(y_offset=0),
    BoardingGroup(y_offset=7),
    BoardingGroup(y_offset=14),
    # BoardingGroup(y_offset=21),
    # BoardingGroup(y_offset=28)
]


class BoardingGroupRandomiser():
    # Takes percentage as a float from (0-1)
    def __init__(self, percentage: float = 0.3) -> None:
        self.percentage = percentage

    # Result comes in the form of {lists[index]: (random choices (index))}
    @staticmethod
    def select_random_items_from_lists(lists: List[List], k: int = 3):
        result = {}

        for i, l in enumerate(lists):
            result[i] = random.sample(range(len(l)), k=k)

        return result

    @staticmethod
    def swap(val1, val2):
        return (val2, val1)

    # Assumes the lengths are the same
    @staticmethod
    def swap_second_value_in_tuples(t1: List[Tuple],
                                    t2: List[Tuple],
                                    even=True):
        r1 = []
        r2 = []

        if even:
            for i, val in enumerate(t1[0::2]):
                v, v1 = BoardingGroupRandomiser.swap(t1[i][1], t2[i][1])
                r1.append((t1[i][0], v))
                r2.append((t2[i][0], v1))

        if not even:
            for i, val in enumerate(t1[0::1]):
                v, v1 = BoardingGroupRandomiser.swap(t1[i][1], t2[i][1])
                r1.append((t1[i][0], v))
                r2.append((t2[i][0], v1))

        return r1, r2

    @staticmethod
    def count_targets(boarding_class: List[BoardingGroup]):
        sum = 0

        for cls in boarding_class:
            sum += len(cls.targets)

        return sum

    # Determines a value for k based on self.percent of the total number of targets
    # Determines a value for k based on self.percent of the total number of targets
    def determine_k(self, boarding_class: List[BoardingGroup]):
        total = BoardingGroupRandomiser.count_targets(boarding_class)

        return math.floor(total * self.percentage)

    def shuffle_boarding_class(self, boarding_class: List[BoardingGroup]):
        lists = list(map(lambda x: x.targets, boarding_class))
        result = {}
      
        for i, l in enumerate(lists):
            for j, target in enumerate(l):
                result[target] = (i, j)

        # print("Before Shuffle")
        # print(result)

        targets = random.sample(result.keys(), k=30)
        bacl = itemgetter(*targets)(result)
        k_shuffled = random.sample([*itemgetter(*targets)(result)], k=len(bacl))

        print(targets)
        print(k_shuffled)

        for i, target in enumerate(targets):
            print(target, k_shuffled[i])
            result[target] = k_shuffled[i]


        for target, class_index in result.items():
            boarding_class[class_index[0]].targets[class_index[1]] = target

        # return res

outside_in_boarding_class = [
    BoardingGroup(aisle_extent=1,
                  height=30).xor(BoardingGroup(aisle_extent=0, height=30)),
    BoardingGroup(aisle_extent=2,
                  height=30).xor(BoardingGroup(aisle_extent=1, height=30)),
    BoardingGroup(aisle_extent=2, height=30)
]

# print(shuffle_boarding_class([[1,2,3,4], ['1','2','3','4'], ['7','6','5','8']]))
randomiser = BoardingGroupRandomiser(0.05)

print('normal')

for g in outside_in_boarding_class:
    print(g.targets)
randomiser.shuffle_boarding_class(outside_in_boarding_class)
print('shuffled')
for g in outside_in_boarding_class:
    print(g.targets)
#     print(g.targets)
# print(
#     list(
#         map(lambda x: x.targets,
#             randomiser.shuffle_boarding_class(outside_in_boarding_class))))
# print(swap_second_value_in_tuples([1,2,3,4], ['1','2','3','4']))