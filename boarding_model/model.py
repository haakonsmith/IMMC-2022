from typing import List, Tuple
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector

import random
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

    def generate_targets(self) -> List[Tuple[int,int]]:
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

        return result

class BoardingModel(Model):
    def __init__(self, N=100, width=10, height=10):
        self.num_agents = N
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)

        self.boarding_offset = 3
        
        # self.boarding_group = BoardingGroup(height=30, aisle_extent=self.boarding_offset)
        self.boarding_group = BoardingGroup(y_offset=self.boarding_offset*7)
        self.add_boarding_group(self.boarding_group.targets)

        self.datacollector = DataCollector(
            model_reporters={"is_complete": self.check_completed}
        )

        self.running = True

    def add_boarding_group(self, targets):
        for target in targets:
            a = BoardingAgent(f"{target[0]},{target[1]}", self, target_seat=target, baggage=np.random.choice(np.arange(0, 4), p=[0.1, 0.75, 0.1, 0.05]))
            self.schedule.add(a)
            self.grid.place_agent(a, (self.grid.width // 2, 0))

    def step(self):
        if self.check_boarding_group() and self.boarding_offset > 0:
            self.boarding_offset -= 1
            # bg = BoardingGroup(aisle_extent=self.boarding_offset, height=30)
            bg = BoardingGroup(y_offset=self.boarding_offset*7)
            self.add_boarding_group(self.boarding_group.xor(bg))
            self.boarding_group = bg

        self.datacollector.collect(self)

        self.schedule.step()

    def check_boarding_group(self) -> bool:
        return not any(map(lambda x: x.state == AgentStates.starting, self.schedule.agent_buffer()))

    def check_completed(self) -> bool:
        return all(map(lambda x: x.state == AgentStates.sitting, self.schedule.agent_buffer()))

    def run_model(self, n):
        for i in range(n):
            self.step()