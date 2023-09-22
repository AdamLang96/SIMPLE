from laserkhet import LaserKhet
import numpy as np
from random import sample
import time
lk = LaserKhet()
lk.reset()
play_game = True
i=0
n_turns = 0
while play_game:  
    mask = lk.legal_actions()
    action = lk.action_space.sample(mask=mask)
    row, col, direction = lk.convert_action_to_coords(action)
    print(f'move [{row},{col}] {lk.action_list[direction]}')
    boardstate, turn, done, reward = lk.step(action)
    print(f'current player: {lk.current_player_num}')
    print(lk.reward_counter)
    print(reward)
    n_turns += 1
    if turn == "Invalid Action" or done:
        print(f'n turns {n_turns}')
        print(turn)
        lk.render()
        play_game = False
        