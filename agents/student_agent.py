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

        #move selection
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
                
                moving_agent_child = (s_x + d_x, s_y + d_y)

                in_board = moving_agent_child[0] >= 0 and moving_agent_child[1] >= 0 
                in_bound = moving_agent_child[0] < len(chess_board) and moving_agent_child[1] < len(chess_board)
                barrier = chess_board [s_x,s_y,self.dir_map[direction]]
                
                if in_board and in_bound and not barrier:

                    distance_to_enemy = math.hypot(moving_agent_child[0] - adv_pos[0], moving_agent_child[1] - adv_pos[1])
                    if (distance_to_enemy <= math.hypot(best_move[0] - adv_pos[0], best_move[1] - adv_pos[1])):
                        best_move = moving_agent_child
            
            if best_move != moving_agent_parent:
                moving_agent_parent = best_move
            k = k + 1

        my_pos = moving_agent_child

        # barrier selection

        e_down = adv_pos[0] == my_pos[0] + 1 and adv_pos[1] == my_pos[1]
        e_up = adv_pos[0] == my_pos[0] - 1 and adv_pos[1] == my_pos[1]
        e_right = adv_pos[0] == my_pos[0] and adv_pos[1] == my_pos[1] + 1
        e_left = adv_pos[0] == my_pos[0] and adv_pos[1] == my_pos[1] - 1

        if e_down and not chess_board [my_pos[0],my_pos[1], self.dir_map["d"]]:
            barrier = self.dir_map["d"]
        
        elif e_up and not chess_board [my_pos[0],my_pos[1], self.dir_map["u"]]:
            barrier = self.dir_map["u"]

        elif e_right and not chess_board [my_pos[0],my_pos[1], self.dir_map["r"]]:
            barrier = self.dir_map["r"]
        
        elif e_left and not chess_board [my_pos[0],my_pos[1], self.dir_map["l"]]:
            barrier = self.dir_map["l"]
        
        else:
            print("choosing random barrier")
            valid_barrier = (0,1,2,3)
            cur_bar = chess_board [my_pos[0],my_pos[1]]
            valid_barrier = [i for i, cur_bar in enumerate(valid_barrier) if cur_bar]
            barrier = random.choice(valid_barrier)

        return my_pos, barrier
