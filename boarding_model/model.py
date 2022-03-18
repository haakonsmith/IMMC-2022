from typing import List, Tuple
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector

from boarding_model.agent import AgentStates, BoardingAgent

class BoardingGroup():
    def __init__(self, y_offset=0) -> None:
        self.aisle = 3
        self.width = 7
        self.height = 10 + y_offset
        self.y_offset = y_offset

        self.targets = self.generate_targets()

    def generate_targets(self) -> List[Tuple[int,int]]:
        targets = []

        for y in range(2 + self.y_offset, self.height - 1):
            for x in range(self.width):
                if x == self.aisle:
                    continue
                target_seat = (x, y)

                targets.append(target_seat)

        return targets




class BoardingModel(Model):
    def __init__(self, N=100, width=10, height=10):
        self.num_agents = N
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)

        self.boarding_offset = 2

        self.add_boarding_group(BoardingGroup(y_offset=(self.boarding_offset + 1) * 7))

        self.datacollector = DataCollector(
            model_reporters={"is_complete": self.check_completed}
        )

        

        self.running = True

    def add_boarding_group(self, group):
        for target in group.targets:
            a = BoardingAgent(f"{target[0]},{target[1]}", self, target_seat=target)
            self.schedule.add(a)
            self.grid.place_agent(a, (self.grid.width // 2, 0))

    def step(self):
        if self.check_boarding_group() and self.boarding_offset >= 0:
            self.add_boarding_group(BoardingGroup(y_offset=self.boarding_offset * 7))
            self.boarding_offset -= 1

        self.datacollector.collect(self)

        self.schedule.step()

    def check_boarding_group(self) -> bool:
        return not any(map(lambda x: x.state == AgentStates.starting, self.schedule.agent_buffer()))

    def check_completed(self) -> bool:
        return all(map(lambda x: x.state == AgentStates.sitting, self.schedule.agent_buffer()))

    def run_model(self, n):
        for i in range(n):
            self.step()