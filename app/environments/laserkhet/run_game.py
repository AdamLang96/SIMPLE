from laserkhet import LaserKhet

lk = LaserKhet()
lk.reset()
n_turns = 0
while True:
    # Take a random action
    action = lk.action_space.sample()
    boardstate, turn, done, reward = lk.step(action)
    print(turn)
    print(done)
    n_turns += 1
    if done == True:
        print(f"number_turns: {n_turns}")
        print(f"# of pieces for p1: {lk.num_pieces_p1}")
        print(f"# of pieces for p2: {lk.num_pieces_p2}")
        break
    
    
    