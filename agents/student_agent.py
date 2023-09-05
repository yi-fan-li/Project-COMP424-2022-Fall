# Student agent: Add your own agent here
from agents.agent import Agent
from store import register_agent
import sys
# added import
from copy import deepcopy
import random
import math
from collections import deque
import timeit

def check_endgame(chess_board, my_pos, adv_pos):
    """
    Check if the game ends and compute the current score of the agents.

    Returns
    -------
    is_endgame : int
        -1 if game not finished
        0 if adversary agent wins
        1 if my agent wins
        2 if game is a tie
    player_scores : int
        p0_score is adversary agent score
        p1_score is my agent score
    """
    # Union-Find
    father = dict()
    board_size = chess_board.shape[0]
    # Moves (Up, Right, Down, Left)
    moves = ((-1, 0), (0, 1), (1, 0), (0, -1))

    for r in range(board_size):
        for c in range(board_size):
            father[(r, c)] = (r, c)

    def find(pos):
        if father[pos] != pos:
            father[pos] = find(father[pos])
        return father[pos]

    def union(pos1, pos2):
        father[pos1] = pos2

    for r in range(board_size):
        for c in range(board_size):
            for direction, move in enumerate(moves[1:3]):
                # Only check down and right
                if chess_board[r, c, direction + 1]:
                    continue
                pos_a = find((r, c))
                pos_b = find((r + move[0], c + move[1]))
                if pos_a != pos_b:
                    union(pos_a, pos_b)

    for r in range(board_size):
        for c in range(board_size):
            find((r, c))
    # P1 is my_pos
    # P0 is adv_pos
    p0_r = find(tuple(adv_pos))
    p1_r = find(tuple(my_pos))
    p0_score = list(father.values()).count(p0_r)
    p1_score = list(father.values()).count(p1_r)

    if p0_r == p1_r:
        # game not finished
        return -1

    player_win = None
    win_blocks = -1
    if p0_score > p1_score:
        player_win = 0
        win_blocks = p0_score
    elif p0_score < p1_score:
        player_win = 1
        win_blocks = p1_score
    else:
        player_win = 2  # Tie
    return player_win

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

        self.moves = ((-1, 0), (0, 1), (1, 0), (0, -1))

        self.root = None

        self.autoplay = True

    def step(self, chess_board, my_pos, adv_pos, max_step):

        if self.root == None:
            #if this is the first move, at the initial state of the board.
            self.root = MonteCarloTreeSearchNode(chess_board, my_pos, adv_pos, max_step)
            best_child = self.root.mCTreeSearch(root = True)
        
        else:
            self.root.board = chess_board
            self.root.adv_pos = adv_pos
            self.root.purge()
            best_child = self.root.mCTreeSearch(root = False)

        best_move = best_child.my_pos
        dir = best_child.dir
        self.root = best_child
        del self.root.parent
        self.root.parent = None
        return best_move, dir




class MonteCarloTreeSearchNode():

    """
    Class defining the properties of a MonteCarlo Tree node
    board: state of the chessboard
    my_pos: current position of player
    adv_pos: current position of adversary
    max_step: the max number of step that can be taken this game
    dir: the direction of the wall to be placed down
    parent: parent node of the node, none for root

    variables:
    visited children: list of all possible moves
    unvisited_children: list any children nodes that have not been visited yet
    number_of_visits: number of time a node has been visited
    win: number of wins of the current node
    losing: if the node immediately loses the game
    winning: if the node immediately wins the game
    """

    def __init__(self, chessboard, my_pos, adv_pos, max_step, dir = None, parent = None):
        #positional information
        self.board = chessboard
        self.my_pos = my_pos
        self.adv_pos = adv_pos
        self.dir = dir
        self.max_step = max_step

        # win lose information
        self.number_of_visits = 0
        self.win = 0
        # win and lose flag for if the child ends the game
        self.losing = False
        self.winning = False

        # tree information
        self.parent = parent
        self.visited_children = dict()
        self.unvisited_children = dict()

    #overall tree search, return a move and a direction
    def mCTreeSearch (self, root = False):

        start = timeit.default_timer()
        stop = timeit.default_timer()

        time_left = 1.95 - (stop - start)

        #if its the root, get 30 second
        if root == True:
            time_left = 29.95 - (stop - start)
            self.expand()
        
        counter = 0
        
        # simulate while there is time left
        #while counter < 100:
        while time_left > 0:

            self.Simulate_Tree()

            stop = timeit.default_timer()
            time_left = 1.95 - (stop - start)
            if root == True:
                time_left = 29.5 - (stop - start)
            counter = counter + 1
        
        child = self.best_child()
        return child

    def best_child(self):

        best_score = 0
        for moves, childrens in self.visited_children.items():

            for child in childrens:
                end_game = check_endgame(child.board, child.my_pos, child.adv_pos)
                
                if end_game == 1:
                    child.winning == True
                    child.losing == False
                
                if end_game == 0 or end_game == 2:
                    child.losing == False
                    child.winning == True

                if child.winning == True:
                    return child

                if child.losing == False:

                    score = child.win/child.number_of_visits

                    if best_score < score:
                        best_score = score
                        best_child = child
                    
                    if not best_score == 0 and best_score == score:
                        if child.number_of_visits > best_child.number_of_visits:
                            best_child = child
            
        return best_child


    def expand (self):
        moves = ((-1, 0), (0, 1), (1, 0), (0, -1))
        opposites = {0: 2, 1: 3, 2: 0, 3: 1}

        all_my_moves = self.findAllMoves(self.board, self.my_pos, self.adv_pos, self.max_step)

        for mymove, mydir in all_my_moves:
            
            newboard = deepcopy(self.board)
            
            opposite_dir = opposites.get(mydir)
            r,c = moves[mydir]

            newboard[mymove[0]][mymove[1]][mydir] = True
            in_bound = 0 <= mymove[0] + r < newboard.shape[0] and 0 <= mymove[1] + c < newboard.shape[1]
            if in_bound:
                newboard[mymove[0] + r, mymove[1] + c, opposite_dir] = True

            childnode = MonteCarloTreeSearchNode(newboard, mymove, self.adv_pos, self.max_step, dir = mydir, parent = self)

            if self.unvisited_children.get(mymove) == None:
                same_pos_moves = [childnode]
                self.unvisited_children[mymove] = same_pos_moves
            
            else:
                same_pos_moves = self.unvisited_children.get(mymove)
                same_pos_moves.append(childnode)

            state = check_endgame(newboard, mymove, self.adv_pos)
            if state == 0 or state == 2:
                childnode.losing = True
                childnode.winning = False

            if state == 1:
                childnode.winning = True
                childnode.losing = False

    #take decision on tree policy or default policy
    def Simulate_Tree(self):
        
        winning = check_endgame(self.board, self.my_pos, self.adv_pos)

        if winning == -1:
            # if not all childrens have been explored, explored 
            not_expanded = len(self.unvisited_children) == 0 and len(self.visited_children) == 0;
            if not_expanded:
                self.expand()

            children_not_explored = len(self.unvisited_children) > 0
            if children_not_explored:
                score = self.default_policy()
            
            else :
                best_node = self.tree_policy()
                # if the node has no best node, there is no valid child, and the child is dead/a loss
                if best_node == None:
                    parent = self.parent
                    del self
                    parent.visited_children
                    return None
                best_node.Simulate_Tree()


    def tree_policy(self):
        
        # exploration constant
        c = 1.1

        if len(self.visited_children) == 0:
            print("error, there is no child for tree policy")
            return None
            
        # get the child that maximise the exploration exploitation score
        best_score = 0
        for moves, childrens in self.visited_children.items():
            for child in childrens:
                exploitation = child.win/child.number_of_visits
                exploration = c * math.sqrt(math.log(self.number_of_visits)/child.number_of_visits)
                score = exploitation + exploration
                
                if best_score < score:
                    best_score = score
                    best_child = child
            
        return best_child


    # choose a random child of the parent to simulate
    def default_policy(self):

        simulated_node = None
        move, child_list = random.choice(list(self.unvisited_children.items()))

        # if there is only one unvisited child left in the list
        if len(child_list) == 1:
            simulated_node = child_list.pop()
            self.unvisited_children.pop(move)
            
        
        # pick a random child to visite 
        else:
            index = random.randint(0,len(child_list) - 1)
            simulated_node = child_list.pop(index)
        
        # get the childrens of the simulated node set up
        simulated_node.expand()

        if self.visited_children.get(move) != None:
            visited_list = self.visited_children.get(move)
            visited_list.append(simulated_node)

        else:
            visited_list = [simulated_node]
            self.visited_children[move] = visited_list

        score = simulated_node.simulation()
        simulated_node.raveBackUp(score)

    # TBD have to be rewritten
    def raveBackUp (self, score):
        
        if self.parent != None:
            parent = self.parent

            # if the simulation ended in a win, increment the win for all child with the same pos
            if score == 1:
                # Check the visited children dict first for the score
                if parent.visited_children.get(self.my_pos) != None:
                    sameMoveList = parent.visited_children.get(self.my_pos)
                    for child in sameMoveList:
                        child.win = child.win + 1
                        child.number_of_visits = child.number_of_visits + 1

                # Check the unvisited children dict second
                if parent.unvisited_children.get(self.my_pos) != None:
                    sameMoveList = parent.unvisited_children.pop(self.my_pos)
                    for child in sameMoveList:
                        child.win = child.win + 1
                        child.number_of_visits = child.number_of_visits + 1

                        # add the unvisited childrens who have been visited now to the visited children dict
                    if parent.visited_children.get(self.my_pos) != None:
                        visited_list = parent.visited_children.get(self.my_pos)
                        visited_list.extend(sameMoveList)

                    else:
                        parent.visited_children[self.my_pos] = sameMoveList


                parent.BackUp(score)
        
            else:

                self.number_of_visits = self.number_of_visits + 1
                parent.BackUp(score)
            
        else:

            self.number_of_visits = self.number_of_visits + 1

            if score == 1:
                self.win = self.win + 1
    
    def BackUp(self, score):

        if score == 1:
            self.win = self.win + 1
            self.number_of_visits = self.number_of_visits + 1
        
        else:
            self.number_of_visits = self.number_of_visits + 1

        if self.parent != None:
            self.parent.BackUp(score)
    
    def purge(self):

        default_moves = ((-1, 0), (0, 1), (1, 0), (0, -1))
        opposites = {0: 2, 1: 3, 2: 0, 3: 1}

        all_moves = self.findAllMoves(self.board, self.my_pos, self.adv_pos, self.max_step)

        elimininated_moves = []
        for move, childrens in self.visited_children.items():
            new_childrens = []
            for index, child in enumerate(childrens):
                dir = child.dir
                if (move,dir) in all_moves:

                    newboard = deepcopy(self.board)
            
                    opposite_dir = opposites.get(child.dir)
                    r,c = default_moves[child.dir]

                    newboard[child.my_pos[0]][child.my_pos[1]][child.dir] = True
                    in_bound = 0 <= child.my_pos[0] + r < newboard.shape[0] and 0 <= child.my_pos[1] + c < newboard.shape[1]
                    if in_bound:
                        newboard[child.my_pos[0] + r, child.my_pos[1] + c, opposite_dir] = True

                    child.adv_pos = self.adv_pos
                    child.board = newboard

                    #checking the new child gamestate with the new board
                    gamestate = check_endgame(child.board, child.my_pos, child.adv_pos)
                    if gamestate == -1:
                        child.winning = False
                        child.losing = False
                    
                    elif gamestate == 1:
                        child.winning = True
                        child.losing = False
                    
                    else:
                        child.winning = False
                        child.losing = True

                    new_childrens.append(child)

            
            if len(new_childrens) == 0:
                elimininated_moves.append(move)
            
            else:
                self.visited_children[move] = new_childrens
        
        for move in elimininated_moves:
            self.visited_children.pop(move)

        elimininated_moves = []
        for move, childrens in self.unvisited_children.items():
            new_childrens = []
            for index, child in enumerate(childrens):
                dir = child.dir
                if (move,dir) in all_moves:

                    newboard = deepcopy(self.board)
            
                    opposite_dir = opposites.get(child.dir)
                    r,c = default_moves[child.dir]

                    newboard[child.my_pos[0]][child.my_pos[1]][child.dir] = True
                    in_bound = 0 <= child.my_pos[0] + r < newboard.shape[0] and 0 <= child.my_pos[1] + c < newboard.shape[1]
                    if in_bound:
                        newboard[child.my_pos[0] + r, child.my_pos[1] + c, opposite_dir] = True

                    child.adv_pos = self.adv_pos
                    child.board = newboard

                    new_childrens.append(child)

                    #checking the new child gamestate with the new board
                    gamestate = check_endgame(child.board, child.my_pos, child.adv_pos)
                    if gamestate == -1:
                        child.winning = False
                        child.losing = False
                    
                    elif gamestate == 1:
                        child.winning = True
                        child.losing = False
                    
                    else:
                        child.winning = False
                        child.losing = True

            
            if len(new_childrens) == 0:
                elimininated_moves.append(move)
            
            else:
                self.unvisited_children[move] = new_childrens
        
        for move in elimininated_moves:
            self.unvisited_children.pop(move)


    def findAllMoves(self, chess_board, my_pos, adv_pos, max_step):
        moves = ((-1, 0), (0, 1), (1, 0), (0, -1))
        # BFS
        cur_step = 0
        # queue to store position and step
        state_queue = deque()
        state_queue.append((my_pos, 0))
        # visited keeps track of visited cases
        visited = {tuple(my_pos)}
        # all_moves is a list of all moves
        all_moves = []

        for dir in range(4):
            if not chess_board[my_pos[0]][my_pos[1]][dir]:
                all_moves.append((my_pos, dir)) 

        # iterate till max step is reached
        while state_queue:

            cur_pos, cur_step = state_queue.popleft()
            r, c = cur_pos

            if cur_step >= max_step:
                break

            # checks all moves u,r,d,l
            # checks all dir for wall
            for direction, move in enumerate(moves):
                
                # checks if there is wall
                blocked = chess_board[cur_pos[0], cur_pos[1], direction]
                if blocked:
                    continue

                # next position
                next_pos = (cur_pos[0] + move[0], cur_pos[1] + move[1])
                x, y = next_pos

                # skip next position if not valid move or already visited
                if next_pos == adv_pos or tuple(next_pos) in visited:
                    continue

                # check if position is valid
                in_bound = 0 <= x < chess_board.shape[0] and 0 <= y < chess_board.shape[1]

                if in_bound:

                    for dir in range(4):
                        if not chess_board[x][y][dir]:
                            all_moves.append(((x, y), dir))       

                # update queue and visited positions
                visited.add(tuple(next_pos))
                state_queue.append((next_pos, cur_step + 1))

        return all_moves
    
    def simulation (self):
        # initiate/reset variables
        moves = ((-1, 0), (0, 1), (1, 0), (0, -1))
        opposites = {0: 2, 1: 3, 2: 0, 3: 1}

        my_pos2 = self.my_pos
        adv_pos2 = self.adv_pos
        chess_board2 = deepcopy(self.board)
        turn = 0
        my_all_moves = []
        adv_all_moves = []
        my_rand_move = ((0, 0), 0)
        adv_rand_move = ((0, 0), 0)
        # update board with my new move
        chess_board2[my_pos2[0], my_pos2[1], self.dir] = True
        # check game status
        game_status = check_endgame(chess_board2, my_pos2, adv_pos2)
        counter = 0
        if game_status != -1:
            return game_status
        """
        simulate the game till game ends
        is_endgame : int
        -1 if game not finished
        0 if adversary agent wins
        1 if my agent wins
        2 if game is a tie
        """
        while game_status < 0:
            counter = counter + 1
            if counter > 1000:
                return 2
            # adv turn
            if turn == 0:
                adv_all_moves = self.findAllMoves(chess_board2, adv_pos2, my_pos2, self.max_step)
                # if no moves, stop simulating
                if len(adv_all_moves) == 0:
                    game_status = check_endgame(chess_board2, my_pos2, adv_pos2)
                    return 1
                # choose random move
                adv_rand_move = random.choice(adv_all_moves)
                # update adv move and board
                adv_pos2 = adv_rand_move[0]

                dir_adv = adv_rand_move[1]
                opposite_dir = opposites.get(dir_adv)
                r,c = moves[dir_adv]

                chess_board2[adv_pos2[0], adv_pos2[1], dir_adv] = True

                in_bound = 0 <= adv_pos2[0] + r < chess_board2.shape[0] and 0 <= adv_pos2[1] + c < chess_board2.shape[1]
                if in_bound:
                    chess_board2[adv_pos2[0] + r, adv_pos2[1] + c, opposite_dir] = True

                # check game status and update
                game_status = check_endgame(chess_board2, my_pos2, adv_pos2)
                if game_status == 1:
                    return game_status
                elif game_status == 2:
                    return game_status
                # set temp turn to not enter next if statement
                turn = 5

            # my turn
            if turn == 1:
                my_all_moves = self.findAllMoves(chess_board2, my_pos2, adv_pos2, self.max_step)
                if len(my_all_moves) == 0:
                    game_status = check_endgame(chess_board2, my_pos2, adv_pos2)
                    return 0
                my_rand_move = random.choice(my_all_moves)
                my_pos2 = my_rand_move[0]

                dir_me = adv_rand_move[1]
                opposite_dir = opposites.get(dir_me)
                r,c = moves[dir_me]

                chess_board2[my_pos2[0], my_pos2[1], dir_me] = True
                in_bound = 0 <= my_pos2[0] + r < chess_board2.shape[0] and 0 <= my_pos2[1] + c < chess_board2.shape[1]
                if in_bound:
                    chess_board2[my_pos2[0] + r, my_pos2[1] + c, opposite_dir] = True

                game_status = check_endgame(chess_board2, my_pos2, adv_pos2)
                if game_status == 1:
                    return game_status
                elif game_status == 2:
                    return game_status
                turn = 4
            # turn = 0 is adv turn
            # turn = 1 is my turn
            turn = turn - 4
        return game_status