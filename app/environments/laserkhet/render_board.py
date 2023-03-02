from PIL import Image
from laserkhet import LaserKhet


khet = LaserKhet()
khet.reset()

a = khet.boardstate
khet.press_laser() 

def render_board(board_state):
    grid = Image.open("/Users/adamgabriellang/Desktop/laserkhetassets/grid.png")
    player_map = ["grey", "red"] #1
    piece_map = ["sphinx", "scarab", "pharaoh", "anubis", "pyramid"]
    board_shape = board_state.shape
    for row in range(board_shape[0]):
        for col in range(board_shape[1]):
            if board_state[row][col][0]:
                bs_vec = board_state[row][col]
                url = f"/Users/adamgabriellang/Desktop/laserkhetassets/laserkhet_pieces_{player_map[bs_vec[3]]}/{piece_map[bs_vec[1]]}.png"
                im = Image.open(url).rotate(-90 * bs_vec[2])
                grid.paste(im, (col*200,row*200), mask = im)
    for laser in khet.laser_tracker:
        print(laser)
        im = Image.open("/Users/adamgabriellang/Desktop/laserkhetassets/laser.png").rotate(-90 * laser[2])
        grid.paste(im, (laser[1]*200,laser[0]*200), mask = im)
    
    grid.show()
    

render_board(a)

                