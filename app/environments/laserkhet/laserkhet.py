from gym import Env
from gym.spaces import Discrete, Box, Dict, MultiDiscrete, Tuple
from pieces import Sphinx, Scarab, Pharaoh, Anubis, Pyramid, Piece
import numpy as np
import json
from copy import deepcopy

class LaserKhet(Env):
    metadata = {'render.modes': ['human']}
    def __init__(self, verbose = False, manual = False):
        
        super(LaserKhet, self).__init__()
        self.name = "LaserKhet"
        self.manual = manual
        self.grid_width = 10
        self.grid_height = 8
        self.num_sqaures = self.grid_height * self.grid_width
        self.grid_shape = (self.grid_height, self.grid_width)
        self.action_list = [
            "skip", #always good
            "rotate_clockwise", #check player piece
            "rotate_counterclockwise", #check player piece
            "up", # check player piece, check bounds, check empty, check full
            "down", #check player piece, check bounds, check empty, check full
            "left", #check player piece, check bounds, check empty, check full
            "right", #check player piece, check bounds, check empty, check full
            "top_left", #check player piece, check bounds, check empty, check full
            "top_right", #check player piece, check bounds, check empty, check full
            "bottom_left", #check player piece, check bounds, check empty, check full
            "bottom_right", #check player piece, check bounds, check empty, check full
            "scarab__swap_up",#check player piece, check bounds, check full, check piece
            "scarab__swap_down",#check player piece, check bounds, check full, check piece
            "scarab__swap_left",#check player piece, check bounds, check full, check piece
            "scarab__swap_right",#check player piece, check bounds, check full, check piece
            "scarab__swap_top_left",#check player piece, check bounds, check full, check piece
            "scarab__swap_top_right",#check player piece, check bounds, check full, check piece
            "scarab__swap_bottom_left",#check player piece, check bounds, check full, check piece
            "scarab__swap_bottom_right"]#check player piece, check bounds, check full, check piece
        
        self.length_action_list = len(self.action_list)
        self.action_space = Discrete(self.grid_height*self.grid_width*self.length_action_list, start=0)
        self.observation_space = Box(low=0, high=4, shape=(self.grid_height, self.grid_width, 4), dtype=np.uint8)
        self.n_players = 2
        self.current_player_num = 0
    
    def check_bounds(self, row, col):
      if row < 0 or row > self.grid_height - 1 or col < 0 or col > self.grid_width - 1:
       return 0 #out of bounds
      else:
         return 1
    
    def check_empty(self, row, col):
       return self.board["position"][row][col]
          
    def check_player_piece(self, row, col):
       if self.current_player_num == self.board["player_piece"][row][col]:
          return 1
       else:
          return 0
       
    def new_coords(self, row, col, direction):
        if direction == "up":
          row = row - 1
        elif direction == "down":
          row = row + 1
        elif direction == "left":
           col = col - 1
        elif direction == "right":
           col = col + 1
        elif direction == "top_left":
          row = row - 1
          col = col - 1
        elif direction == "bottom_left":
          row = row + 1
          col = col - 1
        elif direction == "top_right":
           row = row - 1
           col = col +1
        elif direction == "bottom_right":
           row = row + 1 
           col = col + 1
        return row, col
       
    def check_translate(self, row, col, direction):
        if self.board["name"][row][col] == self.name_map["Pharaoh"]:
           return 0
        new_row, new_col = self.new_coords(row, col, direction)
        bounds = self.check_bounds(new_row, new_col)
        if not bounds:
           return 0
        check_empty = self.check_empty(new_row, new_col)
        if bounds and (not check_empty):
           return 1
        else:
           return 0
    
    def check_scarab_swap(self, row, col, direction):
        new_row, new_col = self.new_coords(row, col, direction)
        bounds = self.check_bounds(new_row, new_col)
        if not bounds:
           return 0
        if self.check_empty(new_row, new_col) and bounds:
          if self.board["name"][new_row][new_col] == self.name_map["Anubis"] or self.board["name"][new_row][new_col] == self.name_map["Pyramid"]:
             return 1
        return 0

    def render(self):
        pass

    def step(self):
        pass
    
    def convert_action_to_coords(self, action):
       floored_element = np.floor(action / self.length_action_list)
       floored_row_n = max(0, np.floor(floored_element / self.grid_width))
       floored_col = floored_element % (self.grid_width)
       n_action = action - (floored_element*self.length_action_list)
       return (int(floored_row_n), int(floored_col), int(n_action))

    def is_legal_action(self, action):
       coords = self.convert_action_to_coords(action=action)
       available_actions = self.available_actions()
       if available_actions[coords[0]][coords[1]][coords[2]]:
          return coords
       else:
          return False
    
    def rotate(self, coords,  direction = "clockwise"):
        orientation = self.board["orientation"][coords[0]][coords[1]]
        orientation = json.loads(self.orientation_map[orientation])
        piece = Piece(orientation=orientation, name =None, player=None)
        if direction == "clockwise":
            piece.rotate_clockwise()
            orientation = piece.orientation
        if direction == "counter-clockwise":
            piece.rotate_counter_clockwise()
            orientation = piece.orientation
        self.board["orientation"][coords[0]][coords[1]] = self.orientation_map.index(json.dumps(orientation))
    
    def translate(self, coords,  direction):
       if self.check_translate(coords[0], coords[1], direction):
          name = self.board["name"][coords[0]][coords[1]]
          orientation = self.board["orientation"][coords[0]][coords[1]]
          player_piece = self.board["player_piece"][coords[0]][coords[1]]
          
          row, col = self.new_coords(coords[0], coords[1])
          self.board["position"][row][col] = 1
          self.board["name"][row][col] = name
          self.board["orientation"][row][col] = orientation
          self.board["player_piece"][row][col] = player_piece
          
          self.board["position"][coords[0]][coords[1]] = 0
          self.board["name"][coords[0]][coords[1]] = 0
          self.board["orientation"][coords[0]][coords[1]] = 0
          self.board["player_piece"][coords[0]][coords[1]] = 0
          return 1
       else:
          return 0
       
    def scarab_swap(self, coords, direction):
       if self.check_scarab_swap(coords[0], coords[1], direction):
          row, col = self.new_coords(coords[0], coords[1])
          
          name = self.board["name"][row][col]
          orientation = self.board["orientation"][row][col]
          player_piece = self.board["player_piece"][row][col]
          
          self.board["name"][row][col] = self.board["name"][coords[0]][coords[1]]
          self.board["orientation"][row][col] = self.board["orientation"][coords[0]][coords[1]]
          self.board["player_piece"][row][col] = self.board["player_piece"][coords[0]][coords[1]]
          
          self.board["name"][coords[0]][coords[1]] = name
          self.board["orientation"][coords[0]][coords[1]] = orientation
          self.board["player_piece"][coords[0]][coords[1]] = player_piece
          return 1
       else:
          return 0
    
    def skip(self, coords):
       self.board = self.board
       return 1
       
    def perform_action(self, action):
       coords = self.is_legal_action(action)
       if coords:
          temp_board = deepcopy(self.board)
          if self.action_list[coords[2]] == "skip":
             pass
          elif self.action_list[coords[2]] == "rotate_clockwise":
             pass
          elif self.action_list[coords[2]] == "rotate_counter_clockwise":
             pass
          elif self.action_list[coords[2]] == "up":
             pass
          elif self.action_list[coords[2]] == "down":
             pass
          elif self.action_list[coords[2]] == "left":
             pass
          elif self.action_list[coords[2]] == "right":
             pass
          elif self.action_list[coords[2]] == "top_left":
             pass
          elif self.action_list[coords[2]] == "top_right":
             pass
          elif self.action_list[coords[2]] == "bottom_left":
             pass
          elif self.action_list[coords[2]] == "bottom_right":
             pass
          elif self.action_list[coords[2]] == "scarab_swap_up":
             pass
          elif self.action_list[coords[2]] == "scarab_swap_down":
             pass
          elif self.action_list[coords[2]] == "scarab_swap_left":
             pass
          elif self.action_list[coords[2]] == "scarab_swap_right":
             pass
          elif self.action_list[coords[2]] == "scarab_swap_top_left":
             pass
          elif self.action_list[coords[2]] == "scarab_swap_top_right":
             pass
          elif self.action_list[coords[2]] == "scarab_swap_bottom_left":
             pass
          elif self.action_list[coords[2]] == "scarab_swap_bottom_right":
             pass
          
       
    def available_actions(self):
        available_actions = np.array([])
        for row in range(len(self.board["position"])):
            actions_row = np.array([])
            for col in range(len(self.board["position"][row])):
                player_piece = self.check_player_piece(row, col) and self.check_empty(row, col)
                actions = np.array([1], dtype=np.uint8)
                if not player_piece:
                    actions = np.concatenate((actions, np.zeros((len(self.action_list) - 1), dtype=np.uint8)))
                else:
                    actions = np.array([1,1,1]) #skip, rotate clockwise, rotate_counter_clockwise
                    actions=np.append(actions, self.check_translate(row, col, "up"))
                    actions=np.append(actions, self.check_translate(row, col, "down"))
                    actions=np.append(actions, self.check_translate(row, col, "left"))
                    actions=np.append(actions, self.check_translate(row, col, "right"))
                    actions=np.append(actions, self.check_translate(row, col, "top_left"))
                    actions=np.append(actions, self.check_translate(row, col, "bottom_left"))
                    actions=np.append(actions, self.check_translate(row, col, "top_right"))
                    actions=np.append(actions, self.check_translate(row, col, "bottom_right"))
                    if self.board["name"][row][col] != self.name_map["Scarab"]:
                        actions = np.concatenate((actions, np.zeros(8, dtype=np.uint8)))
                    else:
                        actions=np.append(actions, self.check_scarab_swap(row, col, "up"))
                        actions=np.append(actions, self.check_scarab_swap(row, col, "down"))
                        actions=np.append(actions, self.check_scarab_swap(row, col, "left"))
                        actions=np.append(actions, self.check_scarab_swap(row, col, "right"))
                        actions=np.append(actions, self.check_scarab_swap(row, col, "top_left"))
                        actions=np.append(actions, self.check_scarab_swap(row, col, "bottom_left"))
                        actions=np.append(actions, self.check_scarab_swap(row, col, "top_right"))
                        actions=np.append(actions, self.check_scarab_swap(row, col, "bottom_right"))
                
                actions_row = np.append(actions_row, actions)
            available_actions = np.append(available_actions,actions_row)
        shaped_actions = np.reshape(available_actions, (10, 8, 19))
        return shaped_actions
                
    def set_board(self, name, row, col, player, orientation = [0,1]):
        self.name_map = {"Sphinx": 0, "Scarab":1, "Pharaoh":2, "Anubis":3, "Pyramid":4}
        self.orientation_map = ["[0, 1]", "[1, 0]", "[0, -1]", "[-1, 0]"]
        self.board["position"][row][col] = 1
        self.board["name"][row][col] = self.name_map[name]
        self.board["orientation"][row][col] = self.orientation_map.index(json.dumps(orientation))
        self.board["player_piece"][row][col] = player
        
        
    def reset(self):
        self.board = {"position": np.zeros(shape = self.grid_shape, dtype = np.uint8),
                      "orientation": np.zeros( shape = self.grid_shape, dtype = np.uint8),
                      "name": np.zeros( shape = self.grid_shape, dtype = np.uint8),
                      "player_piece": np.zeros( shape = self.grid_shape, dtype = np.uint8)}
        
        self.sphinx_map = [np.array([7,9]), np.array([0,0])]
        self.num_pieces_p1 = 13
        self.num_pieces_p2 = 13
        
        
        # self.board[0][0] = Sphinx(player  = 1)
        self.set_board("Sphinx", 0, 0, 1, orientation=[0,-1])
        # self.board[0][4] = Anubis(player  = 1)
        self.set_board("Anubis", 0, 4, 1, orientation=[0,-1])
        # self.board[0][5] = Pharaoh(player = 1)
        self.set_board("Pharaoh", 0, 5, 1, orientation=[0,-1])
        # self.board[0][6] = Anubis(player  = 1)
        self.set_board("Anubis", 0, 6, 1, orientation=[0,-1])
        # self.board[0][7] = Pyramid(player = 1, orientation = [0,-1])
        self.set_board("Pyramid", 0, 7, 1, orientation=[0,-1])

        # #row 1 
        # self.board[1][2] = Pyramid(player=1, orientation=[-1,0])
        self.set_board("Pyramid", 1, 2, 1, orientation=[-1,0])
        # #row 3 
        # self.board[2][3] = Pyramid(player=0, orientation=[0,1])
        self.set_board("Pyramid", 2, 3, 0, orientation=[-1,0])

        # #row4
        # self.board[3][0] = Pyramid(player=1, orientation=[1,0])
        self.set_board("Pyramid", 3, 0, 1, orientation=[1,0]) 
        # self.board[3][2] = Pyramid(player=0, orientation=[-1,0])
        self.set_board("Pyramid", 3, 2, 0, orientation=[-1,0]) 
        # self.board[3][4] = Scarab(player=1,orientation=[0,1])
        self.set_board("Scarab", 3, 4, 1, orientation=[0,1])
        # self.board[3][5] = Scarab(player=1,orientation=[1,0])
        self.set_board("Scarab", 3, 5, 1, orientation=[1,0])
        # self.board[3][7] = Pyramid(player=1,orientation=[0,-1]) 
        self.set_board("Pyramid", 3, 7, 1, orientation=[0,-1])
        # self.board[3][9] = Pyramid(player=0,orientation=[0,1]) 
        self.set_board("Pyramid", 3, 9, 0, orientation=[0,1])

        # #row5
        # self.board[4][0] = Pyramid(player=1,orientation=[0,-1]) 
        self.set_board("Pyramid", 4, 0, 1, orientation=[0,-1])
        # self.board[4][2] = Pyramid(player=0,orientation=[0,1])
        self.set_board("Pyramid", 4, 2, 0, orientation=[0,1]) 
        # self.board[4][4] = Scarab(player=0,orientation=[-1, 0])
        self.set_board("Scarab", 4, 4, 0, orientation=[-1, 0]) 
        # self.board[4][5] = Scarab(player=0,orientation=[0,-1])
        self.set_board("Scarab", 4, 5, 0, orientation=[0,-1]) 
        # self.board[4][7] = Pyramid(player=1,orientation=[1,0])  
        self.set_board("Pyramid", 4, 7, 1, orientation=[1,0]) 
        # self.board[4][9] = Pyramid(player=0,orientation=[-1,0])          
        self.set_board("Pyramid", 4, 9, 0, orientation=[-1,0]) 

        # #row 6
        # self.board[5][6] = Pyramid(player=1,orientation=[0,-1]) 
        self.set_board("Pyramid", 5, 6, 1, orientation=[0,-1]) 

        # #row 7 
        # self.board[6][7] = Pyramid(player=0,orientation=[1,0]) 
        self.set_board("Pyramid", 6, 7, 0, orientation=[1, 0]) 

        # #row 8 (bottom)
        # self.board[7][9] = Sphinx(player=0)
        self.set_board("Sphinx", 7, 9, 0, orientation=[0,1]) 
        # self.board[7][5] = Anubis(player=0)
        self.set_board("Anubis", 7, 5, 0, orientation=[0,1]) 
        # self.board[7][4] = Pharaoh(player=0)
        self.set_board("Pharaoh", 7, 4, 0, orientation=[0,1]) 
        # self.board[7][3] = Anubis(player=0)
        self.set_board("Anubis", 7, 3, 0,  orientation=[0,1]) 
        # self.board[7][2] = Pyramid(player=0, orientation=[0,1])
        self.set_board("Pyramid", 7, 2, 0, orientation=[0,1])
        self.boardstate = np.dstack([self.board["position"], self.board["name"],self.board["orientation"], self.board["player_piece"]]) 


board = LaserKhet()
board.reset()
board.list2.append(5)
print(board.list1)


