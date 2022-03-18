from typing import List, Tuple
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector

import random
import copy
import numpy as np

from boarding_model.agent import AgentStates, BoardingAgent
from boarding_model.boarding_group import BoardingGroup, BoardingGroupRandomiser

def remove_three(l):
    return list(map(lambda x: BoardingGroup(width=3, height=1, square=True).xor(x), l))

top_to_bottom_boarding_class = remove_three([
    BoardingGroup(y_offset=0, height=11),
    BoardingGroup(y_offset=11, height=11),
    BoardingGroup(y_offset=22, height=11)
])

outside_in_boarding_class = remove_three([
    BoardingGroup(aisle_extent=1,
                  height=33).xor(BoardingGroup(aisle_extent=0, height=33)),
    BoardingGroup(aisle_extent=2,
                  height=33).xor(BoardingGroup(aisle_extent=1, height=33)),
    BoardingGroup(aisle_extent=2, height=33)
])

random_boarding_class = remove_three([
    BoardingGroup(height=33),
])

class BoardingModel(Model):
    def __init__(
        self,
        N=100,
        width=10,
        height=10,
        boarding_class=random_boarding_class,
    ):

        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)

        randomiser = BoardingGroupRandomiser()

        # print(boarding_class)

        bacl = list(copy.copy(boarding_class))

        randomiser.shuffle_boarding_class(bacl)

        self.boarding_class = bacl

        self.add_boarding_group(self.boarding_class.pop().targets)

        self.datacollector = DataCollector(
            model_reporters={"is_complete": self.check_completed})

        self.running = True

    def add_boarding_group(self, targets):
        # print(targets)

        for target in targets:
            a = BoardingAgent(f"{target[0]},{target[1]}",
                              self,
                              target_seat=target,
                              baggage=np.random.choice(
                                  np.arange(0, 4), p=[0.1, 0.75, 0.1, 0.05]))
            self.schedule.add(a)
            self.grid.place_agent(a, (self.grid.width // 2, 0))

    def step(self):
        if self.check_boarding_group() and len(self.boarding_class) > 0:
            self.add_boarding_group(self.boarding_class.pop().targets)

        self.datacollector.collect(self)

        self.schedule.step()

    def check_boarding_group(self) -> bool:
        return not any(
            map(lambda x: x.state == AgentStates.starting,
                self.schedule.agent_buffer()))

    def check_completed(self) -> bool:
        return all(
            map(lambda x: x.state == AgentStates.sitting,
                self.schedule.agent_buffer()))

    def run_model(self, n):
        for i in range(n):
            self.step()