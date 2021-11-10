# Agent.py
#
# This code works only for the testworld that comes with the simulator.

import Action
import Orientation
import Search

class MySearchEngine(Search.SearchEngine):
    def HeuristicFunction(self, state, goalState):
        #City block heuristic
        return (abs(state.location[0]-goalState.location[0]) + abs(state.location[1]-goalState.location[1]))
    
class Agent:
    def __init__(self):
        self.agentHasGold = False
        self.actionList = []
        self.searchEngine = MySearchEngine()
        self.agentLocation = [1,1]
        self.agentOrientation = Orientation.RIGHT
        self.goldLocation = []
        self.visitedLocation = []
        self.prev_action = Action.CLIMB
        self.worldsize = 3 #Assume the smallest size = 3, will update as agent discovers more
    
    def __del__(self):
        pass
    
    def Initialize(self):
        self.agentLocation = [1,1]
        self.agentOrientation = Orientation.RIGHT
        self.agentHasGold = False
        self.actionList = []
        self.prev_action = Action.CLIMB
        self.count = 0 #To track how many times agent has moved
    
    # Input percept is a dictionary [perceptName: boolean]
    def Process (self, percept):
        self.UpdateState(percept)

        #Rule 3b: Add current location to safe locations
        if (self.agentLocation not in self.visitedLocation):            
            if (self.agentLocation not in self.searchEngine.safeLocations):
                self.searchEngine.AddSafeLocation(self.agentLocation[0], self.agentLocation[1])
        
        #Rule 3c: Add current location to visited locations
        if self.agentLocation not in self.visitedLocation:
            self.visitedLocation.append(self.agentLocation)
        
        #Rule 3b: No breeze or stench, add adjacent locations to safe locations 
        if not percept.stench and not percept.breeze:
            if self.agentLocation[0] < self.worldsize:
                Right = [self.agentLocation[0]+1, self.agentLocation[1]]
                if Right not in self.searchEngine.safeLocations:
                    self.searchEngine.safeLocations.append(Right)

            if self.agentLocation[1] < self.worldsize:
                Up = [self.agentLocation[0], self.agentLocation[1]+1]
                if Up not in self.searchEngine.safeLocations:
                    self.searchEngine.safeLocations.append(Up)

            if self.agentLocation[0] > 1:
                Left = [self.agentLocation[0]-1, self.agentLocation[1]]
                if Left not in self.searchEngine.safeLocations:
                    self.searchEngine.safeLocations.append(Left)

            if self.agentLocation[1] > 1:
                Down = [self.agentLocation[0], self.agentLocation[1]-1]
                if Down not in self.searchEngine.safeLocations:
                    self.searchEngine.safeLocations.append(Down)
        
        if (self.goldLocation):
            if (not self.actionList):
                #Rule 6: Know gold location, dont have gold
                if (not self.agentHasGold):
                    self.actionList += self.searchEngine.FindPath(self.agentLocation, self.agentOrientation, self.goldLocation, Orientation.RIGHT)
                #Rule 7: Have golf, but not in [1,1]
                else:
                    self.actionList += self.searchEngine.FindPath(self.agentLocation, self.agentOrientation, [1,1], Orientation.LEFT)

        else:
            #Rule 8: Visit safe locations that has not been visited
            if (not self.actionList):
                for x in self.searchEngine.safeLocations:
                    if x not in self.visitedLocation:
                        self.actionList += self.searchEngine.FindPath(self.agentLocation, self.agentOrientation, x, self.agentOrientation)
                        break
            #Rule 8: if all safe locations has been visited, randomly test locations not known to be unsafe
            if (not self.actionList):
                PotentialTargets = []
                for x in range (1, self.worldsize+1):
                    for y in range (1, self.worldsize+1):
                        if [x,y] not in self.visitedLocation:
                            PotentialTargets.append([x,y])
                for Target in PotentialTargets:
                    self.searchEngine.safeLocations.append(Target) #Assume unvistied node is safe to travel to
                    self.actionList += self.searchEngine.FindPath(self.agentLocation, self.agentOrientation, Target, Orientation.RIGHT)
                    if (self.actionList):
                        break
                    else:
                        self.searchEngine.safeLocations.remove(Target) #If no solution found, remove assumption
        
        #Rule 3a: update gold location if perceive glitter
        if percept.glitter:
            self.goldLocation = self.agentLocation
            #Rule 4: Perceive glitter = grab
            self.agentHasGold = True
            self.actionList.insert(0, Action.GRAB)
        
        #Rule 5: have gold and in [1,1], action = Climb
        if self.agentHasGold and self.agentLocation == [1,1]:
            self.actionList.insert(0, Action.CLIMB)
        
        action = 0
        #If solution found, then pop actionList to get sequence of actions
        if self.actionList:
            action = self.actionList.pop(0)
        #If solution is still not found at this point, try to increase the world size, This is an assumption
        else:
            self.worldsize+=1
        
        self.prev_action = action
        return action


    
    def UpdateState(self, percept):
        #Tracking number of moves
        self.count += 1
        #Tracking worldsize
        world = max(self.agentLocation[0], self.agentLocation[1])
        self.worldsize = max(self.worldsize, world)
        #Update Orientation
        currentOrientation = self.agentOrientation
        if (self.prev_action == Action.GOFORWARD):
            if (not percept.bump):
                self.Move()
        if (self.prev_action == Action.TURNLEFT):
            self.agentOrientation = (currentOrientation + 1) % 4
        if (self.prev_action == Action.TURNRIGHT):
            currentOrientation -= 1
            if (currentOrientation < 0):
                currentOrientation = 3
            self.agentOrientation = currentOrientation
        # Nothing to do for CLIMB

    #Using this function to check location:
    def Move(self):
        x = self.agentLocation[0]
        y = self.agentLocation[1]
        if (self.agentOrientation == Orientation.RIGHT):
            x+=1
        if (self.agentOrientation == Orientation.UP):
            y+=1
        if (self.agentOrientation == Orientation.LEFT):
            x-=1
        if (self.agentOrientation == Orientation.DOWN):
            y-=1
        self.agentLocation = [x,y]

    #Using this function to check for boundaries - in case agent dies and its location is wrongly updated
    def fixBoundary (self, Location):
        x = Location[0]
        y = Location[1]
        if x < 1:
            x = 1
        elif x > self.worldsize:
            x = self.worldsize
        if y < 1:
            y = 1
        elif y > self.worldsize:
            y = self.worldsize
        return [x,y]

    def GameOver(self, score):
        #Using score < 999 to prevent a location from being removed from SafeLocations due to limit play = 1000
        if self.prev_action != Action.CLIMB and self.count < 999:
            self.Move()
            self.agentLocation = self.fixBoundary(self.agentLocation)
            x = self.agentLocation[0]
            y = self.agentLocation[1]
            #Rule 3d: if agent dies, update safe locations
            if self.agentLocation not in self.visitedLocation:
                self.visitedLocation.append([x,y])
            self.searchEngine.RemoveSafeLocation(x, y)