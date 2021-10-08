# Agent.py

import Action
import random
import Orientation

class Agent:
    def __init__(self):
        pass
    
    def __del__(self):
        pass
    
    def Initialize(self):
        self.location = [1,1]
        self.orientation = Orientation.RIGHT
        #GetGoldyet = to determine if the gold has been taken
        self.GetGoldyet = False
        #ShootArrowyet = to determine if the agent still has arrow
        self.ShootArrowyet = False
    
    def Process(self, percept):

        if percept.glitter and not self.GetGoldyet:
            action = Action.GRAB
            self.GetGoldyet = True
        elif percept.stench and not self.ShootArrowyet:
            action = Action.SHOOT
            self.ShootArrowyet = True
        elif self.location == [1,1] and self.GetGoldyet:
            action = Action.CLIMB
        
        else:
            action = random.randint(0,2)

            #Updating location and orientation
            if action == Action.GOFORWARD and self.orientation == Orientation.LEFT:
                if self.location[0] > 1:
                    self.location[0] -= 1
            elif action == Action.GOFORWARD and self.orientation == Orientation.RIGHT:
                if self.location[0] < 4:
                    self.location[0] += 1
            elif action == Action.GOFORWARD and self.orientation == Orientation.UP:
                if self.location[1] < 4:
                    self.location[1] += 1
            elif action == Action.GOFORWARD and self.orientation == Orientation.DOWN:
                if self.location[1] > 1:
                    self.location[1] -= 1
            elif action == Action.TURNLEFT:
                if self.orientation == Orientation.LEFT:
                    self.orientation = Orientation.DOWN
                elif self.orientation == Orientation.DOWN:
                    self.orientation = Orientation.RIGHT
                elif self.orientation == Orientation.RIGHT:
                    self.orientation = Orientation.UP
                elif self.orientation == Orientation.UP:
                    self.orientation = Orientation.LEFT
            elif action == Action.TURNRIGHT:
                if self.orientation == Orientation.LEFT:
                    self.orientation = Orientation.UP
                elif self.orientation == Orientation.UP:
                    self.orientation = Orientation.RIGHT
                elif self.orientation == Orientation.RIGHT:
                    self.orientation = Orientation.DOWN
                elif self.orientation == Orientation.DOWN:
                    self.orientation = Orientation.LEFT

        #Printing location and orientation
        if self.GetGoldyet:
            print("Agent has gold = 1", end ="")
        else:
            print("Agent has gold = 0", end ="")
        if self.ShootArrowyet:
            print(", agent has arrow = 0")
        else:
            print(", agent has arrow = 1")
        orientation_dict = {1:"Up", 2:"Left", 3:"Down", 0:"Right"}
        print("Agent's current location is {} and orientation is {}".format(self.location,orientation_dict[self.orientation]))

        return action
    
    def GameOver(self, score):
        pass
