from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
# from mesa.datacollection import DataCollector

from boarding_model.agent import BoardingAgent


class BoardingModel(Model):
    def __init__(self, N=100, width=10, height=10):
        self.num_agents = N
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)

        for y in range(2, self.grid.height - 1):
            # print(y)

            for x in range(self.grid.width):
                # print(x)
                if x == 5:
                    continue

                target_seat = (x, y)
                print(target_seat)

                a = BoardingAgent(f"{x},{y}", self, target_seat=target_seat)
                self.schedule.add(a)
            #     # Add the agent to a random grid cell
            #     x = self.random.randrange(self.grid.width)
            #     y = self.random.randrange(self.grid.height)
                self.grid.place_agent(a, (self.grid.width // 2, 0))

        self.running = True

    def step(self):
        self.schedule.step()

    def run_model(self, n):
        for i in range(n):
            self.step()