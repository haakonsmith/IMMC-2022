from ctypes import Union
import enum
import math
from re import S
from typing import List, Tuple
from mesa import Agent


class AgentStates(enum.Enum):
    waiting = enum.auto()
    seeking = enum.auto()
    starting = enum.auto()
    sitting = enum.auto()
    halting = enum.auto()
    stowing = enum.auto()


class AgentSide(enum.Enum):
    right = enum.auto()
    left = enum.auto()


class BoardingAgent(Agent):
    def __init__(self, unique_id, model, target_seat, baggage=0):
        super().__init__(unique_id, model)

        self.targets = [target_seat]
        self.state = AgentStates.starting

        self.elapsed_wait = 0
        self.target_time = 0

        self.elapsed_halt = 0
        self.target_halt = 0


        # This will be added with the number of people shuffled minus 1

        self.baggage: int = baggage

        # self.baggage_time = 1
        # self.seat_exit_time  = 1
        # self.seat_enter_time = 1
        # self.shuffling_time = 1
        # self.speed = 1
        self.baggage_time = self.generate_value_pm(31, 5, 5)
        self.seat_exit_time  = self.generate_value_pm(11, 4, 2)
        self.seat_enter_time = self.generate_value_pm(27, 63, 9)
        self.shuffling_time = self.generate_value_pm(4, 1, 0)
        self.speed = self.generate_value_pm(7, 2, 2)

        self.stowing = False
        self.on_complete_halt = None

    def has_baggage(self) -> bool:
        return self.baggage > 0

    def generate_value_pm(self, med, plus, minus):
        return max(med + self.model.random.randrange(-minus, plus), 0)

    @staticmethod
    def direction_sign(direction):
        if direction > 0:
            return 1
        elif direction < 0:
            return -1
        else:
            return 0

    # These two halt functions represent the wait loop
    def halt_for(self, t: int):
        self.target_halt = t
        self.elapsed_halt = 0
        self.state = AgentStates.halting

    def resolve_halt(self):
        if self.elapsed_halt == self.target_halt and self.state == AgentStates.halting:
            self.state = AgentStates.seeking

            if self.on_complete_halt:
                self.on_complete_halt()

            self.on_complete_halt = False

        elif self.state == AgentStates.halting:
            self.elapsed_halt += 1

    # The difference between wait and halt is arbitrary but it was written in a rush and I see no benefit in wasting time fixing it.
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
        # return self.shuffling_time + len(self.get_number_of_blocking_seats()) - 1
        blocked_seats = self.get_number_of_blocking_seats()

        num_movements = 0
        
        if len(blocked_seats) == 1 and (blocked_seats[0] == 4 or blocked_seats[0] == 2):
            num_movements += 1 
        else:
            num_movements += 2 * len(blocked_seats)

        num_movements += 1 + abs(self.pos[0] - self.targets[0][0])
        # + self.seat_enter_time * (len(blocked_seats) + 1)
        return num_movements * self.speed + self.seat_exit_time * len(blocked_seats) 

        


    def calculate_stow_time(self):
        if not self.has_baggage():
            return 0

        return self.baggage_time * self.baggage

    def get_number_of_blocking_seats(self):
        if self.get_target_side(self.targets[0]) == AgentSide.right:
            comp_func = lambda x: x[0] >= self.targets[0][0]
        if self.get_target_side(self.targets[0]) == AgentSide.left:
            comp_func = lambda x: x[0] <= self.targets[0][0]

        # This just filters by only the seats on the same side as the target position.
        seats = filter(comp_func,
                       self.get_all_blocked_seats_for_row(self.targets[0]))

        # Convert generator to list
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
            self, target: Tuple[int, int]) -> List[Tuple[int, int]]:
        blocked_seats = []

        if self.get_target_side(target) == AgentSide.right:
            bounds = (4, self.model.grid.width)
        else:
            bounds = (0, 4)

        for x in range(*bounds):
            if x == 3:
                continue

            pos = (x, target[1])

            cell = self.model.grid[pos]
            if len(cell) > 0:
                blocked_seats.append(pos)

        return blocked_seats

    def check_if_position_blocks_target(self, pos):
        target = self.targets[0]

        return (self.get_target_side(target) == AgentSide.right
                and pos[0] <= self.targets[0][0]) or (
                    self.get_target_side(target) == AgentSide.left
                    and pos[0] >= self.targets[0][0])

    def move(self):
        new_position = self.navigate()

        if len(self.targets) > 0 and self.targets[0][1] - self.pos[
                1] == 1 and self.state == AgentStates.seeking:

            for seat in self.get_all_blocked_seats_for_row(self.targets[0]):
                if self.check_if_position_blocks_target(seat):
                    self.wait_for(self.calculate_wait_time() +
                                  self.calculate_stow_time())

        if self.state == AgentStates.waiting or self.state == AgentStates.halting:
            return

        if self.model.grid.is_cell_empty(new_position):
            self.state = AgentStates.seeking
            self.model.grid.move_agent(self, new_position)


            # self.halt_for(self.speed)

            if new_position == self.targets[0]:
                self.targets.pop()
                self.halt_for(self.speed + self.seat_enter_time)
                self.state = AgentStates.sitting
            else:
                self.halt_for(self.speed)

        else:
            # self.halt_for(1)
            pass

        if len(
                self.targets
        ) > 0 and self.targets[0][1] - self.pos[1] == 0 and self.has_baggage():
            self.stowing = True
            self.halt_for(self.baggage_time)
            self.on_complete_halt = self.complete_stowing
            self.baggage = 0

    def target_str(self):
        # return ""
        if len(self.targets) == 0:
            return "N"
        return str(self.targets[0])

    def complete_sitting(self):
        self.state = AgentStates.sitting

    def complete_stowing(self):
        self.stowing = False

    def complete_shuffling(self):
        self.state = AgentStates.sitting
        self.model.grid.move_agent(self, self.targets[0])
        self.targets.pop()

    def step(self):
        self.move()

        self.resolve_wait()
        self.resolve_halt()
