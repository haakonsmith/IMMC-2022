from ctypes import Union
import enum
import math
from typing import List, Tuple
from mesa import Agent


class AgentStates(enum.Enum):
    waiting = enum.auto()
    seeking = enum.auto()
    starting = enum.auto()
    sitting = enum.auto()


class AgentSide(enum.Enum):
    right = enum.auto()
    left = enum.auto()


class BoardingAgent(Agent):
    def __init__(self, unique_id, model, target_seat):
        super().__init__(unique_id, model)

        self.targets = [target_seat]
        self.state = AgentStates.starting

        self.elapsed_wait = 0
        self.target_time = 0


    @staticmethod
    def direction_sign(direction):
        if direction > 0:
            return 1
        elif direction < 0:
            return -1
        else:
            return 0

    def wait_for(self, t: int):
        self.target_time = t
        self.elapsed_wait = 0
        self.state = AgentStates.waiting

    def resolve_wait(self):
        if self.elapsed_wait == self.target_time and self.state == AgentStates.waiting:
            self.state = AgentStates.sitting
            self.model.grid.move_agent(self, self.targets[0])
            self.targets.pop()

        elif self.state == AgentStates.waiting:
            self.elapsed_wait += 1

    def calculate_wait_time(self):
        return self.model.random.randrange(5, 20) * len(self.get_number_of_blocking_seats())

    def get_number_of_blocking_seats(self):
        if self.get_target_side(self.targets[0]) == AgentSide.right:
            seats = filter(lambda x: x[0] >= self.targets[0][0], self.get_all_blocked_seats_for_row(self.targets[0]))

        if self.get_target_side(self.targets[0]) == AgentSide.left:
            seats = filter(lambda x: x[0] <= self.targets[0][0], self.get_all_blocked_seats_for_row(self.targets[0]))

        return list(seats)

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

        y_pos += BoardingAgent.direction_sign(y_diff)

        # If we've found the row navigate left or right.
        if y_diff == 0:
            x_pos += BoardingAgent.direction_sign(x_diff)

        return (x_pos, y_pos)

    def get_target_side(self, target):
        if target[0] > 3:
            return AgentSide.right
        else:
            return AgentSide.left

    def get_all_blocked_seats_for_row(
        self, target: Tuple[int, int]
    ) -> List[Tuple[int, int]]:
        blocked_seats = []

        if self.get_target_side(target) == AgentSide.right:
            bounds = (4, self.model.grid.width)
        else:
            bounds = (0, 4)

        for x in range(*bounds):
            if x == 3:
                continue

            pos = (x, target[1])

            if not self.model.grid.is_cell_empty(pos):
                blocked_seats.append(pos)

        return blocked_seats

    def move(self):
        new_position = self.navigate()

        if len(self.targets) > 0 and self.targets[0][1] - self.pos[1] == 1 and self.state == AgentStates.seeking:
            target = self.targets[0]

            blocked_seats = self.get_all_blocked_seats_for_row(target)

            for seat in blocked_seats:
                if (
                    self.get_target_side(target) == AgentSide.right
                    and seat[0] <= self.targets[0][0]
                ):
                    self.wait_for(self.calculate_wait_time())

                if (
                    self.get_target_side(target) == AgentSide.left
                    and seat[0] >= self.targets[0][0]
                ):
                    self.wait_for(self.calculate_wait_time())

        if self.state == AgentStates.waiting:
            return

        if self.model.grid.is_cell_empty(new_position):
            self.state = AgentStates.seeking
            self.model.grid.move_agent(self, new_position)

            if new_position == self.targets[0]:
                self.state = AgentStates.sitting
                self.targets.pop()

    def target_str(self):
        if len(self.targets) == 0:
            return "N"
        return str(self.targets[0]) 

    def step(self):
        self.move()

        self.resolve_wait()        
