# Student agent: Add your own agent here
from agents.agent import Agent
from store import register_agent
import sys
from copy import deepcopy
import random
import math


@register_agent("student_agent")
class StudentAgent(Agent):
    """
    A dummy class for your implementation. Feel free to use this class to
    add any helper functionalities needed for your agent.
    """

    def __init__(self):
        super(StudentAgent, self).__init__()
        self.name = "StudentAgent"
        self.dir_map = {
            "u": 0,
            "r": 1,
            "d": 2,
            "l": 3,
        }

        self.move_map = {
            "u": (-1,0),
            "r": (0,1),
            "d": (1,0),
            "l": (0,-1),
        }

        self.autoplay = True

    def step(self, chess_board, my_pos, adv_pos, max_step):


        moving_agent_parent = deepcopy(my_pos)

        step_left = max_step
        
        k = 0
        while (k < max_step):
            best_move = moving_agent_parent
            for direction in self.move_map:
                s_x = moving_agent_parent[0]
                s_y = moving_agent_parent[1]
                d_x = self.move_map[direction][0]
                d_y = self.move_map[direction][1]
                
                moving_agent_child = (s_x - d_x, s_y - d_y)

                in_board = moving_agent_child[0] >= 0 and moving_agent_child[1] >= 0

                barrier = chess_board [s_x,s_y,self.dir_map[direction]]
                
                if in_board and not barrier:

                    distance_to_enemy = math.hypot(moving_agent_child[0]  - adv_pos[0], moving_agent_child[1] - adv_pos[1])
                    if (distance_to_enemy < math.hypot(best_move[0] - adv_pos[0], best_move[1] - adv_pos[1])):
                        best_move = moving_agent_child
            
            moving_agent_parent = best_move
            k = k + 1

        my_pos = moving_agent_child

        if (adv_pos[0] == my_pos[0] + 1 and adv_pos[1] == my_pos[1]):
            barrier = self.dir_map["d"]
        
        elif (adv_pos[0] == my_pos[0] - 1 and adv_pos[1] == my_pos[1]):
            barrier = self.dir_map["u"]

        elif (adv_pos[0] == my_pos[0] and adv_pos[1] == my_pos[1] + 1):
            barrier = self.dir_map["r"]
        
        elif (adv_pos[0] == my_pos[0] and adv_pos[1] == my_pos[1] - 1):
            barrier = self.dir_map["l"]
        
        else:
            valid_barrier = (0,1,2,3)
            cur_bar = chess_board [my_pos[0],my_pos[1]]
            valid_barrier = [i for i, cur_bar in enumerate(valid_barrier) if cur_bar]
            barrier = random.choice(valid_barrier)
        
        

        """
        Implement the step function of your agent here.
        You can use the following variables to access the chess board:
        - chess_board: a numpy array of shape (x_max, y_max, 4)
        - my_pos: a tuple of (x, y)
        - adv_pos: a tuple of (x, y)
        - max_step: an integer

        You should return a tuple of ((x, y), dir),
        where (x, y) is the next position of your agent and dir is the direction of the wall
        you want to put on.

        Please check the sample implementation in agents/random_agent.py or agents/human_agent.py for more details.
        """
        # dummy return
        return my_pos, barrier
