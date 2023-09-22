import numpy as np

class Piece():
    def __init__(self, name, player, orientation):
        # if name not in np.array(["Pyramid", "Sphinx", "Scarab", "Anubis", "Pharaoh"]):
        #     raise ValueError(f'name must be one of np.array(["Pyramid", "Sphinx", "Scarab", "Anubis", "Pharaoh"])).all(). Received {name}')
        self.name = name
        self.player = player
        self.orientation = orientation

    def rotate_clockwise(self):
        if (self.orientation == np.array([0,1])).all():
           self.orientation = np.array([1,0])
        elif (self.orientation == np.array([1,0])).all():
           self.orientation = np.array([0,-1])
        elif (self.orientation == np.array([0,-1])).all():
           self.orientation = np.array([-1,0])
        else:
           self.orientation = np.array([0,1])
       
    def rotate_counter_clockwise(self):
        if (self.orientation == np.array([0,1])).all():
           self.orientation = np.array([-1,0])
        elif (self.orientation == np.array([-1,0])).all():
           self.orientation = np.array([0,-1])  
        elif (self.orientation == np.array([0,-1])).all():
           self.orientation = np.array([1,0])
        else:
           self.orientation = np.array([0,1])

class Pyramid(Piece):
    #for the pyramid and scarab we will consider pyramid pointing to top left as np.array([0,1])).all()
    def __init__(self, *args, **kwargs):
        super(Pyramid, self).__init__(*args, **kwargs, name="Pyramid")
    
    def laser_deflection(self, laser_direction):
        if (self.orientation == np.array([0,1])).all():
            if (laser_direction == np.array([0,-1])).all() or (laser_direction == np.array([1,0])).all():
                return laser_direction[::-1] 
            else:
                return 'hit'
        
        if (self.orientation == np.array([1,0])).all():
            if (laser_direction == np.array([0,-1])).all() or (laser_direction == np.array([-1,0])).all():
                return  laser_direction[::-1] * -1
            else:
                return 'hit'

        if (self.orientation == np.array([0,-1])).all():
            if (laser_direction == np.array([0,1])).all() or (laser_direction ==np.array([-1,0])).all():
                return  laser_direction[::-1]
            else:
                return 'hit'
        
        if (self.orientation == np.array([-1,0])).all():
            if (laser_direction == np.array([0,1])).all() or (laser_direction == np.array([1,0])).all():
                return  laser_direction[::-1] * -1
            else:
                return 'hit'

class Sphinx(Piece):
    def __init__(self, *args, **kwargs):
        super(Sphinx, self).__init__(*args, **kwargs, name="Sphinx")
        
    def laser_deflection(self, laser_direction):
        return 'hit unharmed'
    
class Scarab(Piece):
    def __init__(self, *args, **kwargs):
        super(Scarab, self).__init__(*args, **kwargs, name="Scarab")
    
    def laser_deflection(self, laser_direction):
        if (self.orientation == np.array([0,1])).all() or (self.orientation == np.array([0,-1])).all():
            return laser_direction[::-1]
        
        if (self.orientation == np.array([1,0])).all() or (self.orientation == np.array([-1,0])).all():
                   return laser_direction[::-1] * -1

class Anubis(Piece):
    def __init__(self, *args, **kwargs):
        super(Anubis, self).__init__(*args, **kwargs, name="Anubis")
    def laser_deflection(self, laser_direction):
        if (np.array(laser_direction) == np.array(self.orientation) * -1).all():
            return 'hit unharmed'
        else:
            return 'hit'

class Pharaoh(Piece):
    def __init__(self, *args, **kwargs):
        super(Pharaoh, self).__init__(*args, **kwargs, name="Pharaoh")
    def laser_deflection(self, laser_direction):
        return 'hit'

