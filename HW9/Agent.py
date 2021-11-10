# Agent.py
#
# Fall 2021 HW5 solution.
#
# Written by Larry Holder.

import Action
import Percept
import Orientation
import Search
import sys

class MySearchEngine(Search.SearchEngine):
    def HeuristicFunction(self, state, goalState):
        city_block = abs(state.location[0] - goalState.location[0]) + abs(state.location[1] - goalState.location[1])
        return city_block 
        #return 0 # not a good heuristic
    
class Agent:
    def __init__(self):
        # Initialize new agent based on new, unknown world
        self.agentLocation = [1,1]
        self.agentOrientation = Orientation.RIGHT
        self.agentHasGold = False
        self.lastAction = Action.CLIMB # dummy action
        self.actionList = []
        self.searchEngine = MySearchEngine()
        self.worldSize = 3 # HW5: somewhere between 3x3 and 9x9
        self.worldSizeKnown = False 
        self.goldLocation = [0,0] # unknown
        self.visitedLocations = []
        self.safeLocations = [] # For HW5, means not known to be unsafe
        self.unsafeLocations = []
        self.stenchLocations = [] # For HW9, unknown
        self.WumpusLocation = [0, 0] # For HW9, unknown
        self.WumpusDead = False # For HW9, keep track of Wumpus
    
    def __del__(self):
        pass
    
    def Initialize(self):
        # Initialize agent back to the beginning of the world
        self.agentLocation = [1,1]
        self.agentOrientation = Orientation.RIGHT
        self.agentHasGold = False
        self.lastAction = Action.CLIMB # dummy action
        self.actionList = []
        self.WumpusDead = False
        self.InitializeWumpusLocation()
    
    # Input percept is a dictionary [perceptName: boolean]
    def Process (self, percept):
        actionList2 = []
        self.UpdateState(self.lastAction, percept)
        if (self.actionList == []):
            if (percept.glitter):
                # HW5.4: If there is gold, then GRAB it
                print("Found gold. Grabbing it.")
                actionList2.append(Action.GRAB)
                self.actionList.extend(actionList2)
            elif (self.agentHasGold and (self.agentLocation == [1,1])):
                # HW5.5: If agent has gold and is in (1,1), then CLIMB
                print("Have gold and in (1,1). Climbing.")
                actionList2.append(Action.CLIMB)
                self.actionList.extend(actionList2)
            elif ((not self.agentHasGold) and (self.goldLocation != [0,0])):
                # HW5.6: If agent doesn't have gold, but knows its location, then navigate to that location
                print("Moving to known gold location (" + str(self.goldLocation[0]) + "," + str(self.goldLocation[1]) + ").")
                actionList2 = self.searchEngine.FindPath(self.agentLocation, self.agentOrientation,
                                                            self.goldLocation, self.agentOrientation)
                self.actionList.extend(actionList2)
            elif (self.agentHasGold and (self.agentLocation != [1,1])):
                # HW5.7: If agent has gold, but isn't in (1,1), then navigate to (1,1)
                print("Have gold. Moving to (1,1).")
                actionList2 = self.searchEngine.FindPath(self.agentLocation, self.agentOrientation,
                                                            [1,1], self.agentOrientation)
                self.actionList.extend(actionList2)
            if not actionList2:
                # HW5.8: If safe unvisited location, then navigate there (should be one)
                safeUnvisitedLocation = self.SafeUnvisitedLocation()
                print("Moving to safe unvisited location " + str(safeUnvisitedLocation))
                if safeUnvisitedLocation != None:
                    actionList2 = self.searchEngine.FindPath(self.agentLocation, self.agentOrientation,
                                                         safeUnvisitedLocation, self.agentOrientation)
                if actionList2:
                    self.actionList.extend(actionList2)
                else:
                    if (not self.agentHasGold):
                        if (self.WumpusLocation != [0, 0]) and (not self.WumpusDead): #Rule 4a HW9
                            targetLocation = self.FindLocationtoShoot()
                            targetOrientation = self.FindOrientationToShoot(targetLocation)
                            print(f"Moving to wumpus at {self.WumpusLocation[0]} {self.WumpusLocation[1]}")
                            actionList2 = self.searchEngine.FindPath(self.agentLocation, self.agentOrientation,
                                                    targetLocation, targetOrientation)
                            actionList2.append(Action.SHOOT)
                            actionList2.append(Action.GOFORWARD)
                            self.actionList.extend(actionList2)
                        elif self.WumpusDead: #Rule 4b HW9    
                            PotentialTargets = []
                            for x in range (1, self.worldSize+1):
                                for y in range (1, self.worldSize+1):
                                    if [x,y] not in self.visitedLocations and [x,y] not in self.unsafeLocations:
                                        PotentialTargets.append([x,y])
                            for Target in PotentialTargets:
                                self.searchEngine.safeLocations.append(Target) #Assume unvistied node is safe to travel to
                                print(f"Moving to target {Target[0]} {Target[1]}")
                                actionList2 = self.searchEngine.FindPath(self.agentLocation, self.agentOrientation, Target, Orientation.RIGHT)
                                if (actionList2):
                                    break
                                else:
                                    self.searchEngine.safeLocations.remove(Target) #If no solution found, remove assumption
                            self.actionList.extend(actionList2)
                    else:
                        print("ERROR: no path to safe unvisited location") # for debugging
                        sys.exit(1)
        action = self.actionList.pop(0)
        self.lastAction = action
        return action
    
    def GameOver(self, score):
        if score < -1000:
            # Agent died by going forward into pit or Wumpus
            percept = Percept.Percept() #dummy
            self.UpdateState(Action.GOFORWARD, percept, game_over=True)
            location = self.agentLocation
            if location not in self.unsafeLocations:
                self.unsafeLocations.append(location)
            if location in self.safeLocations:
                self.safeLocations.remove(location)
            if location in self.searchEngine.safeLocations:
                self.searchEngine.safeLocations.remove(location)
            print("Found unsafe location " + str(location))
            print(f"Wumpuslocation: {self.WumpusLocation[0]}, {self.WumpusLocation[1]}")
        return
    
    def UpdateState(self, lastAction, percept, game_over=False):
        X = self.agentLocation[0]
        Y = self.agentLocation[1]
        orientation = self.agentOrientation
        if (lastAction == Action.TURNLEFT):
            self.agentOrientation = (orientation + 1) % 4
        if (lastAction == Action.TURNRIGHT):
            if (orientation == Orientation.RIGHT):
                self.agentOrientation = Orientation.DOWN
            else:
                self.agentOrientation = orientation - 1
        if (lastAction == Action.GOFORWARD):
            if percept.bump:
                if (orientation == Orientation.RIGHT) or (orientation == Orientation.UP):
                    print("World size known to be " + str(self.worldSize) + "x" + str(self.worldSize))
                    self.worldSizeKnown = True
                    self.RemoveOutsideLocations()
            else:
                if orientation == Orientation.UP:
                    self.agentLocation = [X,Y+1]
                elif orientation == Orientation.DOWN:
                    self.agentLocation = [X,Y-1]
                elif orientation == Orientation.LEFT:
                    self.agentLocation = [X-1,Y]
                elif orientation == Orientation.RIGHT:
                    self.agentLocation = [X+1,Y]
        if (lastAction == Action.GRAB): # Assume GRAB only done if Glitter was present
                self.agentHasGold = True
        if (lastAction == Action.CLIMB):
            pass # do nothing; if CLIMB worked, this won't be executed anyway
        # HW5 requirement 3a
        if percept.glitter:
            self.goldLocation = self.agentLocation
            print("Found gold at " + str(self.goldLocation))
        # HW5 clarification: track world size
        new_max = max(self.agentLocation[0], self.agentLocation[1])
        if new_max > self.worldSize:
            self.worldSize = new_max
        # HW5 requirement 3b
        if not game_over:
            self.UpdateSafeLocations(self.agentLocation)
        # HW5 requirement 3c
        if self.agentLocation not in self.visitedLocations:
            self.visitedLocations.append(self.agentLocation)
        # HW9 Maintain information about stench locations
        if percept.stench and self.agentLocation not in self.stenchLocations:
            self.stenchLocations.append(self.agentLocation)
        # HW9 Maintain information about Wumpus alive or not
        # as well as location
        if percept.scream:
            self.WumpusDead = True
        if self.WumpusDead:
            self.RemoveWumpusfromUnsafe()
        if self.WumpusLocation == [0,0]:
            self.InferWumpus()
    
    def UpdateSafeLocations(self, location):
        # HW5 requirement 3b, and HW5 clarification about not known to be unsafe locations
        # Add current and adjacent locations to safe locations, unless known to be unsafe.
        if location not in self.safeLocations:
            self.safeLocations.append(location)
            self.searchEngine.AddSafeLocation(location[0], location[1])
        for adj_loc in self.AdjacentLocations(location):
            if (adj_loc not in self.safeLocations) and (adj_loc not in self.unsafeLocations):
                self.searchEngine.AddSafeLocation(adj_loc[0], adj_loc[1])
        
    def SafeUnvisitedLocation(self):
        # Find and return safe unvisited location
        for location in self.searchEngine.safeLocations:
            if location not in self.visitedLocations:
                return location
        return None
    
    def RemoveOutsideLocations(self):
        # Know exact world size, so remove locations outside the world.
        boundary = self.worldSize + 1
        for i in range(1,boundary):
            if [i,boundary] in self.searchEngine.safeLocations:
            #    self.safeLocations.remove([i,boundary])
                self.searchEngine.RemoveSafeLocation(i, boundary)
            if [boundary, i] in self.searchEngine.safeLocations:
            #    self.safeLocations.remove([boundary, i])
                self.searchEngine.RemoveSafeLocation(boundary, i)
        if [boundary, boundary] in self.searchEngine.safeLocations:
            #self.safeLocations.remove([boundary, boundary])
            self.searchEngine.RemoveSafeLocation(boundary, boundary)
    
    def AdjacentLocations(self, location):
        # Return list of locations adjacent to given location. One row/col beyond unknown
        # world size is okay. Locations outside the world will be removed later.
        X = location[0]
        Y = location[1]
        adj_locs = []
        if X > 1:
            adj_locs.append([X-1,Y])
        if Y > 1:
            adj_locs.append([X,Y-1])
        if self.worldSizeKnown:
            if (X < self.worldSize):
                adj_locs.append([X+1,Y])
            if (Y < self.worldSize):
                adj_locs.append([X,Y+1])
        else:
            adj_locs.append([X+1,Y])
            adj_locs.append([X,Y+1])
        return adj_locs

    def InferWumpus(self):
        for loc1 in self.stenchLocations:
            for loc2 in self.stenchLocations:
                if (loc1[0] + 1 == loc2[0]) and (loc1[1] + 1 == loc2[1]):
                    if [loc1[0] + 1, loc1[1]] in self.safeLocations:
                        self.WumpusLocation = [loc1[0], loc1[1] + 1]
                    if [loc1[0], loc1[1] + 1] in self.safeLocations:
                        self.WumpusLocation = [loc1[0] + 1, loc1[1]]
                if (loc1[0] + 1 == loc2[0]) and (loc1[1] - 1 == loc2[1]):
                    if [loc1[0] + 1, loc1[1]] in self.safeLocations:
                        self.WumpusLocation = [loc1[0], loc1[1] - 1]
                    if [loc1[0], loc1[1] - 1] in self.safeLocations:
                        self.WumpusLocation = [loc1[0] + 1, loc1[1]]
        if self.WumpusLocation != [0, 0]:
            self.unsafeLocations.append(self.WumpusLocation)
            
    def RemoveWumpusfromUnsafe(self):
        if self.WumpusLocation in self.unsafeLocations:
            self.unsafeLocations.remove(self.WumpusLocation)   
        self.UpdateSafeLocations(self.WumpusLocation)
    
    def FindLocationtoShoot(self):
        for location in self.stenchLocations:
            if location not in self.unsafeLocations:
                return location
    
    def FindOrientationToShoot(self, location):
        X = location[0]
        Y = location[1]
        HorWumpus = self.WumpusLocation[0]
        VerWumpus = self.WumpusLocation[1]
        if(X == HorWumpus) and (Y + 1 == VerWumpus):
            return Orientation.UP
        elif(X == HorWumpus) and (Y - 1 == VerWumpus):
            return Orientation.DOWN
        elif(X + 1 == HorWumpus) and (Y == VerWumpus):
            return Orientation.RIGHT
        elif(X - 1 == HorWumpus) and (Y == VerWumpus):
            return Orientation.LEFT
    
    def InitializeWumpusLocation(self):
        if self.WumpusLocation != [0,0]:
            if self.WumpusLocation in self.safeLocations:
                self.safeLocations.remove(self.WumpusLocation)
            if self.WumpusLocation in self.searchEngine.safeLocations:
                self.searchEngine.safeLocations.remove(self.WumpusLocation)
            self.unsafeLocations.append(self.WumpusLocation)