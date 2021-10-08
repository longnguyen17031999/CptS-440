# Agent.py
#
# HW2 Fall 2021

from random import randint
import Action
import Orientation

class WorldState:
    def __init__(self):
        self.agentLocation = [1,1]
        self.agentOrientation = Orientation.RIGHT
        self.agentHasArrow = True
        self.agentHasGold = False

class Agent:
    def __init__(self):
        self.worldState = WorldState()
        self.previousAction = Action.CLIMB
        self.actionList = []
    
    def __del__(self):
        pass
    
    def Initialize(self):
        self.worldState.agentLocation = [1,1]
        self.worldState.agentOrientation = Orientation.RIGHT
        self.worldState.agentHasArrow = True
        self.worldState.agentHasGold = False
        self.previousAction = Action.CLIMB
        self.actionList = []

    
    def Process(self, percept):
        self.UpdateState(percept)
        if not self.actionList:
            if percept.glitter: # Rule 3a
                self.actionList.append(Action.GRAB)
            elif (self.worldState.agentHasGold and (self.worldState.agentLocation == [1,1])): # Rule 3b
                self.actionList.append(Action.CLIMB)
            elif percept.stench and self.worldState.agentHasArrow: # Rule 3c
                self.actionList.append(Action.SHOOT)
            else: # Rule 3d
                randomAction = randint(0,2) # 0=GOFORWARD, 1=TURNLEFT, 2=TURNRIGHT
                self.actionList.append(randomAction)
        action = self.actionList.pop(0)
        self.previousAction = action
        return action

    def UpdateState(self, percept):
        currentOrientation = self.worldState.agentOrientation
        if (self.previousAction == Action.GOFORWARD):
            if (not percept.bump):
                self.Move()
        if (self.previousAction == Action.TURNLEFT):
            self.worldState.agentOrientation = (currentOrientation + 1) % 4
        if (self.previousAction == Action.TURNRIGHT):
            currentOrientation -= 1
            if (currentOrientation < 0):
                currentOrientation = 3
            self.worldState.agentOrientation = currentOrientation
        if (self.previousAction == Action.GRAB):
            self.worldState.agentHasGold = True # Only GRAB when there's gold
        if (self.previousAction == Action.SHOOT):
            self.worldState.agentHasArrow = False
        # Nothing to do for CLIMB

    def Move(self):
        X = self.worldState.agentLocation[0]
        Y = self.worldState.agentLocation[1]
        if (self.worldState.agentOrientation == Orientation.RIGHT):
            X = X + 1
        if (self.worldState.agentOrientation == Orientation.UP):
            Y = Y + 1
        if (self.worldState.agentOrientation == Orientation.LEFT):
            X = X - 1
        if (self.worldState.agentOrientation == Orientation.DOWN):
            Y = Y - 1
        self.worldState.agentLocation = [X,Y]
    
    def GameOver(self, score):
        pass
