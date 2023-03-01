from laserkhet import LaserKhet

lk = LaserKhet()
lk.reset()

while True:
    # Take a random action
    action = lk.action_space.sample()
    boardstate, turn, done, reward = lk.step(action)
    print(turn)
    print(done)
    if done == True:
        break