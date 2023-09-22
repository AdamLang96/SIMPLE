from pieces import Sphinx, Scarab, Pharaoh, Anubis, Pyramid
import numpy as np
from copy import deepcopy

class Classic():
    def __init__(self):
        self.width = 10
        self.height = 8
        self.board = np.zeros((self.height, self.width), dtype = object)
        self.sphinx_map = {"1": np.array([7,9]), "2":np.array([0,0])}
        self.num_pieces_p1 = 13
        self.num_pieces_p2 = 13
        
        self.board[0][0] = Sphinx(player="2")
        self.board[0][4] = Anubis(player="2")
        self.board[0][5] = Pharaoh(player="2")
        self.board[0][6] = Anubis(player="2")
        self.board[0][7] = Pyramid(player="2", orientation=[0,-1])

        #row 1 
        self.board[1][2] = Pyramid(player="2", orientation=[-1,0])

        #row 3 
        self.board[2][3] = Pyramid(player="1", orientation=[0,1])

        #row4
        self.board[3][0] = Pyramid(player="2", orientation=[1,0]) 
        self.board[3][2] = Pyramid(player="1", orientation=[-1,0])
        self.board[3][4] = Scarab(player="2",orientation=[0,1])
        self.board[3][5] = Scarab(player="2",orientation=[1,0])
        self.board[3][7] = Pyramid(player="2",orientation=[0,-1]) 
        self.board[3][9] = Pyramid(player="1",orientation=[0,1]) 

        #row5
        self.board[4][0] = Pyramid(player="2",orientation=[0,-1]) 
        self.board[4][2] = Pyramid(player="1",orientation=[0,1]) 
        self.board[4][4] = Scarab(player="1",orientation=[-1, 0])
        self.board[4][5] = Scarab(player="1",orientation=[0,-1])
        self.board[4][7] = Pyramid(player="2",orientation=[1,0])  
        self.board[4][9] = Pyramid(player="1",orientation=[-1,0])          

        #row 6
        self.board[5][6] = Pyramid(player="2",orientation=[0,-1]) 

        #row 7 
        self.board[6][7] = Pyramid(player="1",orientation=[1,0]) 

        #row 8 (bottom)
        self.board[7][9] = Sphinx(player="1")
        self.board[7][5] = Anubis(player="1")
        self.board[7][4] = Pharaoh(player="1")
        self.board[7][3] = Anubis(player="1")
        self.board[7][2] = Pyramid(player="1", orientation=[0,1]) 
        
        self.init_board = deepcopy(self.board)
