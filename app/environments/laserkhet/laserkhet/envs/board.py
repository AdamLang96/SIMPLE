import numpy as np

class Board():
    def __init__(self):
        self.curr_player = "1"
    
    def check_move_validity(self, coords):
        if self.board[coords[0]][coords[1]] == 0:
            raise ValueError("There must be a piece at this location on the board")
        if self.board[coords[0]][coords[1]].player != self.curr_player:
            raise ValueError("You can only move your own piece")
        
    def press_laser(self):
        keep_moving_laser = True
        pos = self.sphinx_map[self.curr_player]
        if self.curr_player == "1":
            self.curr_player == "2"
        else:
            self.curr_player == "1"
        laser_orientation = self.board[pos[0], pos[1]].orientation
        while keep_moving_laser:
            if (laser_orientation == [0,1]).all():
                pos[0] -= 1
            elif (laser_orientation == [0,-1]).all():
                pos[0] += 1
            elif (laser_orientation == [1,0]).all():
                pos[1] += 1
            else :
                pos[1] -= 1
            if pos[0] < 0 or pos[0] > self.height - 1 or pos[1] < 0 or pos[1] > self.width - 1:
                print("out of bounds")
                return "out of bounds"
            print(f"laser orientation {laser_orientation}")
            print(f"pos {pos}")
            piece = self.board[pos[0]][pos[1]]
            if piece:
                print(piece)
                laser_orientation = piece.laser_deflection(laser_orientation)
                if not isinstance(laser_orientation, np.ndarray):
                    if laser_orientation == 'hit':
                        if piece.name == "Pharaoh" and piece.player == "1":
                            print("Game Over. Player 2 Wins")
                            return "Game Over. Player 2 Wins"
                        elif piece.name == "Pharaoh" and piece.player == "2":
                            print("Game Over. Player 1 Wins")
                            return "Game Over. Player 1 Wins"
                        elif piece.player == "1":
                            self.num_pieces_p1 -= 1
                        else:
                            self.num_pieces_p2 -= 1
                        self.board[pos[0]][pos[1]] = 0
                        print('hit')
                        return "hit"
                    if laser_orientation == 'hit unharmed':
                        print("hit unharmed")
                        return "hit unharmed"
        
    def rotate_piece(self, direction, coords):
        self.check_move_validity(coords)
        if direction == "clockwise":
            self.board[coords[0]][coords[1]].rotate_clockwise()
        if direction == "counter-clockwise":
            self.board[coords[0]][coords[1]].rotate_counter_clockwise()
    
    def translate_piece(self, current_coords, new_coords):
        self.check_move_validity(current_coords)
        if abs(current_coords[0] - new_coords[0]) > 1 or abs(current_coords[1] - new_coords[1]) > 1:
            raise ValueError("You can only move a piece one square in any direction per turn")
        
        elif self.board[new_coords[0]][new_coords[1]] != 0 and self.board[current_coords[0]][current_coords[1]].name != 'Scarab':
            raise ValueError("The board is already occupied in this location")
        
        elif self.board[new_coords[0]][new_coords[1]] != 0 and self.board[current_coords[0]][current_coords[1]].name == 'Scarab':
            if self.board[new_coords[0]][new_coords[1]].name == 'Anubis' or self.board[new_coords[0]][new_coords[1]].name == 'Pyramid':
                new_piece =  self.board[new_coords[0]][new_coords[1]]
                self.board[new_coords[0]][new_coords[1]] = self.board[current_coords[0]][current_coords[1]]
                self.board[current_coords[0]][current_coords[1]] = new_piece
            else:
                raise ValueError("The Scarab can only swap with an Anubis or Pyramid")
        elif self.board[current_coords[0]][current_coords[1]].name == 'Sphinx':
            raise ValueError("The Sphinx can not be moved")
        else:
            self.board[new_coords[0]][new_coords[1]] = self.board[current_coords[0]][current_coords[1]]
            self.board[current_coords[0]][current_coords[1]] = 0
        
    def reset_board(self):
        self.board = self.init_board

