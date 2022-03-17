from ctypes import Union
import enum
import math
from typing import Tuple
from mesa import Agent

class AgentStates(enum.Enum):
    waiting = enum.auto()
    seeking = enum.auto()
    allowing = enum.auto()
    sitting = enum.auto()

class BoardingAgent(Agent):
    def __init__(self, unique_id, model, target_seat):
        super().__init__(unique_id, model)

        self.targets = [target_seat]
        self.state = AgentStates.seeking

    @staticmethod
    def direction_sign(direction):
        if direction > 0:
            return 1
        elif direction < 0:
            return -1
        else:
            return 0

    # returns the next point to move to
    def navigate(self) -> Tuple[int, int]:
        # If the targets are empty don't move
        if len(self.targets) == 0:
            return self.pos

        target = self.targets[0]

        # First move in the y direction
        y_diff = target[1] - self.pos[1]
        x_diff = target[0] - self.pos[0]

        y_pos = self.pos[1]
        x_pos = self.pos[0]

        # if target[0] == 3:
        #     print(x_pos)
        #     x_pos += BoardingAgent.direction_sign(x_diff)
            
        #     # If we've found the row navigate left or right.
        #     if x_diff == 0:
        #         y_pos += BoardingAgent.direction_sign(y_diff)

        #     if (x_pos, y_pos) == target:
        #         self.targets.pop()

        #     return (x_pos, y_pos)


        y_pos += BoardingAgent.direction_sign(y_diff)
        # If we've found the row navigate left or right.
        if y_diff == 0:
            x_pos += BoardingAgent.direction_sign(x_diff)

        if (x_pos, y_pos) == target:

            self.targets.pop()

        return (x_pos, y_pos)

    def move_down_aisle(self):
        # self.state = AgentStates.waiting
        pass

    def check_if_path_aisle_blocked(self, target) -> Tuple[int, int]:

        if target[0] > 3:
            bounds = (4, target[0])
        else:
            bounds = (target[0], 3)

        for x in range(bounds[0], bounds[1]):
            print(x)
            # breakpoint()
            cell = self.model.grid[((x, target[1]))]
            if len(cell) > 0 and cell[0].state == AgentStates.sitting:
                return (x, target[1])

        return None

    def move(self):
        # y_position = self.pos[1] if self.pos[1] == 9 else self.pos[1] + 1

        new_position = self.navigate()

     
        # if self.state == AgentStates.waiting:
        #     cell = self.model.grid[(self.pos[0], self.pos[1] + 2)]
        #     # if len(cell) > 0 and cell[0].state == AgentStates.allowing:
        #     #     self.state = AgentStates.seeking

        #     return

        if self.model.grid.is_cell_empty(new_position):
            self.model.grid.move_agent(self, new_position)

        # if len(self.targets) == 0 and self.state == AgentStates.seeking:
        #     self.state = AgentStates.sitting
        
        # if len(self.targets) >= 1:
        #     if self.targets[0][1] - self.pos[1] == 1:
        #         # print("One seat away")
        #         # self.state = AgentStates.waiting
        #         aisle_block = self.check_if_path_aisle_blocked(self.targets[0])

        #         if aisle_block:
        #             print("aisle_block:")
        #             print(aisle_block)

        #             self.model.grid[aisle_block][0].targets.append((self.pos[0],self.pos[1] + 2))
        #             self.model.grid[aisle_block][0].state = AgentStates.allowing

        #             self.state = AgentStates.waiting
            # print('stuck!')

    def target_str(self):
        if len(self.targets) == 0:
            return "N"
        return str(self.targets[0])

    def step(self):
        self.move()