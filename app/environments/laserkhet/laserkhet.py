from gym import Env
from gym.spaces import Discrete, Box
from pieces import Sphinx, Scarab, Pharaoh, Anubis, Pyramid, Piece
import numpy as np
import json
from PIL import Image
class LaserKhet(Env):
    metadata = {'render.modes': ['human']}
    def __init__(self, verbose = False, manual = False, assets_path = "/Users/adamgabriellang/Desktop/laserkhetassets", reward_weights = {'mirrors_used':.1, 
                                                                                                                                          'opponent_piece_taken':.25,
                                                                                                                                          'skips':-.1,
                                                                                                                                          'won':1}): 
        super(LaserKhet, self).__init__()
        self.name = "LaserKhet"
        self.manual = manual
        self.grid_width = 10
        self.grid_height = 8
        self.num_sqaures = self.grid_height * self.grid_width
        self.grid_shape = (self.grid_height, self.grid_width)
        self.action_list = [
            "skip", 
            "rotate_clockwise", 
            "rotate_counterclockwise", 
            "up", 
            "down", 
            "left", 
            "right", 
            "top_left", 
            "top_right", 
            "bottom_left", 
            "bottom_right", 
            "scarab__swap_up",
            "scarab__swap_down",
            "scarab__swap_left",
            "scarab__swap_right",
            "scarab__swap_top_left",
            "scarab__swap_top_right",
            "scarab__swap_bottom_left",
            "scarab__swap_bottom_right"]
        
        self.length_action_list = len(self.action_list)
        self.action_space = Discrete(self.grid_height*self.grid_width*self.length_action_list, start=0)
        self.observation_space = Box(low=0, high=4, shape=(self.grid_height, self.grid_width, 4), dtype=np.uint8)
        self.current_player_num = 1
        self.assets_path = assets_path
        self.sphinx_map = [np.array([7,9]), np.array([0,0])]
        self.reward_weights = reward_weights
        
    def player_logic(self, name, player, orientation):
        if name == 1:
            piece = Sphinx(player=player, orientation=orientation)
        elif name == 2:
            piece = Scarab(player=player, orientation=orientation)
        elif name == 3:
            piece = Pharaoh(player=player, orientation=orientation)
        elif name == 4:
            piece = Anubis(player=player, orientation=orientation)
        elif name == 5:
            piece = Pyramid(player=player, orientation=orientation)
        return piece
        
    def check_bounds(self, row, col):
      if row < 0 or row > self.grid_height - 1 or col < 0 or col > self.grid_width - 1:
         return 0
      else:
         return 1
    
    def check_empty(self, row, col):
       if not self.check_bounds(row, col):
           return 0
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
        new_row, new_col = self.new_coords(row, col, direction)
        rules = [
             (self.check_player_piece(row, col) and self.check_empty(row, col)),
             self.board["name"][row][col] != self.name_map["Sphinx"],
             self.check_bounds(new_row, new_col),
             not self.check_empty(new_row, new_col)
                ]
        if all(rules):
            return 1
        else:
            return 0
    
    def check_scarab_swap(self, row, col, direction):
        new_row, new_col = self.new_coords(row, col, direction)
        rules = [(self.check_player_piece(row, col) and self.check_empty(row, col)),
                 self.board["name"][row][row] == self.name_map["Scarab"],
                 self.check_bounds(new_row, new_col),
                 self.check_empty(new_row, new_col),
                 self.board["name"][new_row][new_col] == self.name_map["Pyramid"]]  
        if all(rules):
            return 1
        else:
            return 0

    def check_rotate(self, row, col):
        if not (self.check_player_piece(row, col) and self.check_empty(row, col)):
            return 0
        return 1
    
    def check_skip(self, row, col):
        if not (self.check_player_piece(row, col) and self.check_empty(row, col)):
            return 0
        return 1
        
    def render(self):
        grid = Image.open(f"{self.assets_path}/grid.png")
        player_map = ["grey", "red"] #1
        piece_map = ["sphinx", "scarab", "pharaoh", "anubis", "pyramid"]
        board_shape = self.boardstate.shape
        for row in range(board_shape[0]):
            for col in range(board_shape[1]):
                if self.boardstate[row][col][0]:
                    bs_vec = self.boardstate[row][col]
                    url = f"{self.assets_path}/laserkhet_pieces_{player_map[bs_vec[3]-1]}/{piece_map[bs_vec[1]-1]}.png"
                    
                    im = Image.open(url).rotate(-90 * bs_vec[2])
                    grid.paste(im, (col*200,row*200), mask = im)
        for laser in self.laser_tracker:
            im = Image.open(f"{self.assets_path}/laser.png").rotate(-90 * laser[2])
            grid.paste(im, (laser[1]*200 + 75,laser[0]*200), mask = im)
        
        grid.show()

    def update_boardstate(self):
        self.boardstate = np.dstack([self.board["position"], 
                                     self.board["name"],
                                     self.board["orientation"], 
                                     self.board["player_piece"]])
    
    def observation(self):
        player_mask = np.array(self.board['player_piece'], dtype=np.float64)
        if self.current_player_num == 1:
            player_two_location = np.where(self.board['player_piece']==2)
            player_mask[player_two_location] = -1
        else:
            player_one_location =  np.where(self.board['player_piece']==1)
            player_two_location =  np.where(self.board['player_piece']==2)
            player_mask[player_two_location]=1
            player_mask[player_one_location]=-1
        position = self.board["position"] * player_mask
        piece_names = (self.board["name"] / 5) * player_mask
        orientation = (self.board["orientation"] / 4) 
        return np.dstack([position, piece_names, orientation])

       
    def convert_action_to_coords(self, action):
       floored_element = np.floor(action / self.length_action_list)
       floored_row_n = max(0, np.floor(floored_element / self.grid_width))
       floored_col = floored_element % (self.grid_width)
       n_action = action - (floored_element*self.length_action_list)
       return (int(floored_row_n), int(floored_col), int(n_action))

    def is_legal_action(self, row, col, direction):
        if direction not in self.action_list:
            print(direction)
        if direction == 'skip':
            is_move_legal = self.check_skip(row, col)
        if direction in ['rotate_clockwise', 'rotate_counterclockwise']:
            is_move_legal = self.check_rotate(row, col)
        if direction in ["up", "down", "left", "right", "top_left", "top_right", "bottom_left", "bottom_right"]:
            is_move_legal = self.check_translate(row, col, direction)
        if direction in  ["scarab__swap_up", "scarab__swap_down", "scarab__swap_left", "scarab__swap_right",
                          "scarab__swap_top_left", "scarab__swap_top_right", "scarab__swap_bottom_left",
                          "scarab__swap_bottom_right"]:
            is_move_legal = self.check_scarab_swap(row, col, direction)
        return is_move_legal
            
    
    def rotate(self, coords,  direction):
        orientation = self.board["orientation"][coords[0]][coords[1]]
        orientation = json.loads(list(self.orientation_map.keys())[list(self.orientation_map.values()).index(orientation)])
        piece = Piece(orientation=orientation, name =None, player=None)
        if direction == "rotate_clockwise":
            piece.rotate_clockwise()
            orientation = piece.orientation
        if direction == "rotate_counterclockwise":
            piece.rotate_counter_clockwise()
            orientation = piece.orientation
        self.board["orientation"][coords[0]][coords[1]] = self.orientation_map[json.dumps(orientation.tolist())]
        return True
    
    def translate(self, coords,  direction):
        name = self.board["name"][coords[0]][coords[1]]
        orientation = self.board["orientation"][coords[0]][coords[1]]
        player_piece = self.board["player_piece"][coords[0]][coords[1]]
        row, col = self.new_coords(coords[0], coords[1], direction)
        self.board["position"][row][col] = 1
        self.board["name"][row][col] = name
        self.board["orientation"][row][col] = orientation
        self.board["player_piece"][row][col] = player_piece
        self.board["position"][coords[0]][coords[1]] = 0
        self.board["name"][coords[0]][coords[1]] = 0
        self.board["orientation"][coords[0]][coords[1]] = 0
        self.board["player_piece"][coords[0]][coords[1]] = 0
                 
    def scarab_swap(self, coords, direction):
        row, col = self.new_coords(coords[0], coords[1], direction)
        name = self.board["name"][row][col]
        orientation = self.board["orientation"][row][col]
        player_piece = self.board["player_piece"][row][col]
        self.board["name"][row][col] = self.board["name"][coords[0]][coords[1]]
        self.board["orientation"][row][col] = self.board["orientation"][coords[0]][coords[1]]
        self.board["player_piece"][row][col] = self.board["player_piece"][coords[0]][coords[1]]
        self.board["name"][coords[0]][coords[1]] = name
        self.board["orientation"][coords[0]][coords[1]] = orientation
        self.board["player_piece"][coords[0]][coords[1]] = player_piece
          
    def skip(self):
       self.board = self.board
       return 1
       
    def perform_action(self, action):
        coords = self.convert_action_to_coords(action)
        row, col, direction = coords
        direction = self.action_list[direction]
        is_move_legal = self.is_legal_action(coords[0], coords[1], direction)
        if not is_move_legal:
            return False
        if direction == "skip":
            self.reward_counter['skips'] += 1
            return 'skip'
        if direction in ['rotate_clockwise', 'rotate_counterclockwise']:
            self.rotate([row, col], direction)
        if direction in ["up", "down", "left", "right", "top_left", "top_right", "bottom_left", "bottom_right"]:
            self.translate([row, col], direction)
        if direction in  ["scarab__swap_up", "scarab__swap_down", "scarab__swap_left", "scarab__swap_right",
                          "scarab__swap_top_left", "scarab__swap_top_right", "scarab__swap_bottom_left",
                          "scarab__swap_bottom_right"]:
            self.scarab_swap([row, col], direction)
        return True
    
    def press_laser(self):
        self.laser_tracker = []
        keep_moving_laser = True
        pos = self.sphinx_map[self.current_player_num - 1]
        laser_orientation = self.board["orientation"][pos[0], pos[1]]
        laser_orientation = np.array(json.loads(list(self.orientation_map.keys())[list(self.orientation_map.values()).index(laser_orientation)]))
        while keep_moving_laser:
            if (laser_orientation == [0,1]).all():
                pos[0] -= 1
                laser = [pos[0], pos[1], 0]
            elif (laser_orientation == [0,-1]).all():
                pos[0] += 1
                laser = [pos[0], pos[1], 2]
            elif (laser_orientation == [1,0]).all():
                pos[1] += 1
                laser = [pos[0], pos[1], 1]
            else :
                pos[1] -= 1
                laser = [pos[0], pos[1], 3]
            if not self.check_bounds(pos[0], pos[1]):
                keep_moving_laser = False
                return "OOB"
            piece = self.board["position"][pos[0]][pos[1]]
            name = self.board["name"][pos[0]][pos[1]]
            orientation = self.board["orientation"][pos[0]][pos[1]]
            player = self.board["player_piece"][pos[0]][pos[1]]
            if piece:
                piece = self.player_logic(name, player, np.array(json.loads(list(self.orientation_map.keys())[list(self.orientation_map.values()).index(orientation)])))
                laser_orientation = piece.laser_deflection(laser_orientation)
                if not isinstance(laser_orientation, np.ndarray):
                    keep_moving_laser = False
                    if laser_orientation == 'hit':
                        if piece.player != self.current_player_num:
                            self.reward_counter["opponent_piece_taken"] += 1
                        if piece.name == "Pharaoh" and piece.player == 1:
                            if self.current_player_num == 2:
                                self.reward_counter["won"] = 1
                            else:
                                self.reward_counter["won"] = -1
                            return "P2W"
                        elif piece.name == "Pharaoh" and piece.player == 2:
                             if self.current_player_num == 1:
                                self.reward_counter["won"] = 1
                             else:
                                self.reward_counter["won"] = -1
                             return "P1W"
                        elif piece.player == 0:
                            self.num_pieces_p1 -= 1
                        else:
                            self.num_pieces_p2 -= 1
                        self.board["position"][pos[0]][pos[1]] = 0
                        self.board["name"][pos[0]][pos[1]] = 0
                        self.board["orientation"][pos[0]][pos[1]] = 0
                        self.board["player_piece"][pos[0]][pos[1]] = 0
                        return "hit"
                    if laser_orientation == 'hit unharmed':
                        return "hit unharmed"
                else:
                    self.reward_counter["mirrors_used"] += 1
            else:
                self.laser_tracker.append(laser)
        
    def execute_turn(self, action):
        completed_action = self.perform_action(action)
        if not completed_action:
           self.reward_counter["illegal_action"] += 1
           return "Invalid Action"
        else:
            turn = self.press_laser()
            self.update_boardstate()
            return turn
        
    def step(self, action):
        self.reward_counter = {"mirrors_used":0, "opponent_piece_taken":0, "skips":0, 'won': 0}
        count = self.reward_counter
        reward = [0,0]
        w = self.reward_weights        
        done = False
        turn = self.execute_turn(action)
        if turn == 'P2W': 
            done = True
        if turn == 'P1W':
            done = True
        # add reward here
        if self.current_player_num==1:
            self.current_player_num=2
        else:
            self.current_player_num=1
        self.sphinx_map = [np.array([7,9]), np.array([0,0])]
        r = count['mirrors_used'] * w['mirrors_used'] + count["opponent_piece_taken"] * w["opponent_piece_taken"] 
        r = r + count['skips'] * w['skips'] + count["won"] * w["won"] 
        reward[self.current_player_num - 1] = r
        return self.boardstate, turn, done, reward
            
    def legal_actions(self):
        mask = []
        for row in range(len(self.board["position"])):
            for col in range(len(self.board["position"][row])):
                for action in self.action_list:
                    mask.append(self.is_legal_action(row, col, action))
        mask = np.array(mask, dtype=np.int8)
        return mask
        
                
    def set_board(self, name, row, col, player, orientation = [0,1]):
        self.name_map = {"Sphinx": 1, "Scarab":2, "Pharaoh":3, "Anubis":4, "Pyramid":5}
        self.orientation_map = {"[0, 1]": 1, "[1, 0]": 2, "[0, -1]": 3, "[-1, 0]": 4}
        self.board["position"][row][col] = 1
        self.board["name"][row][col] = self.name_map[name]
        self.board["orientation"][row][col] = self.orientation_map[json.dumps(orientation)]
        self.board["player_piece"][row][col] = player
        
        
    def reset(self):
        self.laser_tracker = []
        self.board = {"position": np.zeros(shape = self.grid_shape, dtype = np.uint8),
                      "orientation": np.zeros( shape = self.grid_shape, dtype = np.uint8),
                      "name": np.zeros( shape = self.grid_shape, dtype = np.uint8),
                      "player_piece": np.zeros( shape = self.grid_shape, dtype = np.uint8)}
        
        self.sphinx_map = [np.array([7,9]), np.array([0,0])]
        self.num_pieces_p1 = 13
        self.num_pieces_p2 = 13
        
        
        self.set_board("Sphinx", 0, 0, 2, orientation=[0,-1])
        self.set_board("Anubis", 0, 4, 2, orientation=[0,-1])
        self.set_board("Pharaoh", 0, 5, 2, orientation=[0,-1])
        self.set_board("Anubis", 0, 6, 2, orientation=[0,-1])
        self.set_board("Pyramid", 0, 7, 2, orientation=[0,-1])

        # #row 1 
        self.set_board("Pyramid", 1, 2, 2, orientation=[-1,0])
        # #row 3 
        self.set_board("Pyramid", 2, 3, 1, orientation=[0,1])

        # #row4
        self.set_board("Pyramid", 3, 0, 2, orientation=[1,0]) 
        self.set_board("Pyramid", 3, 2, 1, orientation=[-1,0]) 
        self.set_board("Scarab", 3, 4, 2, orientation=[0,1])
        self.set_board("Scarab", 3, 5, 2, orientation=[1,0])
        self.set_board("Pyramid", 3, 7, 2, orientation=[0,-1])
        self.set_board("Pyramid", 3, 9, 1, orientation=[0,1])

        # #row5
        self.set_board("Pyramid", 4, 0, 2, orientation=[0,-1])
        self.set_board("Pyramid", 4, 2, 1, orientation=[0,1]) 
        self.set_board("Scarab", 4, 4, 1, orientation=[-1, 0]) 
        self.set_board("Scarab", 4, 5, 1, orientation=[0,-1]) 
        self.set_board("Pyramid", 4, 7, 2, orientation=[1,0]) 
        self.set_board("Pyramid", 4, 9, 1, orientation=[-1,0]) 

        # #row 6
        self.set_board("Pyramid", 5, 6, 2, orientation=[0,-1]) 

        # #row 7 
        self.set_board("Pyramid", 6, 7, 1, orientation=[1, 0]) 

        # #row 8 (bottom)
        self.set_board("Sphinx", 7, 9, 1, orientation=[0,1]) 
        self.set_board("Anubis", 7, 5, 1, orientation=[0,1]) 
        self.set_board("Pharaoh", 7, 4, 1, orientation=[0,1]) 
        self.set_board("Anubis", 7, 3, 1,  orientation=[0,1]) 
        self.set_board("Pyramid", 7, 2, 1, orientation=[0,1])
        self.boardstate = np.dstack([self.board["position"], self.board["name"],self.board["orientation"], self.board["player_piece"]]) 
        self.reward_counter = {"mirrors_used":0, "opponent_piece_taken":0, "skips":0, 'won': 0}
        self.turns = 0




