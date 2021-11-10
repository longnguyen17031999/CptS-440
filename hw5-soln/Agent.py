# Agent.py
#
# Fall 2021 HW5 solution.
#
# Written by Larry Holder.

import Action
import Percept
import Orientation
import Search

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
    
    def __del__(self):
        pass
    
    def Initialize(self):
        # Initialize agent back to the beginning of the world
        self.agentLocation = [1,1]
        self.agentOrientation = Orientation.RIGHT
        self.agentHasGold = False
        self.lastAction = Action.CLIMB # dummy action
        self.actionList = []
    
    # Input percept is a dictionary [perceptName: boolean]
    def Process (self, percept):
        actionList2 = []
        self.UpdateState(self.lastAction, percept)
        if (self.actionList == []):
            if (percept.glitter):
                # HW5.4: If there is gold, then GRAB it
                print("Found gold. Grabbing it.")
                self.actionList.append(Action.GRAB)
            elif (self.agentHasGold and (self.agentLocation == [1,1])):
                # HW5.5: If agent has gold and is in (1,1), then CLIMB
                print("Have gold and in (1,1). Climbing.")
                self.actionList.append(Action.CLIMB)
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
            else:
                # HW5.8: If safe unvisited location, then navigate there (should be one)
                safeUnvisitedLocation = self.SafeUnvisitedLocation()
                print("Moving to safe unvisited location " + str(safeUnvisitedLocation))
                actionList2 = self.searchEngine.FindPath(self.agentLocation, self.agentOrientation,
                                                         safeUnvisitedLocation, self.agentOrientation)
                if actionList2:
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
            percept = Percept.Percept() # dummy, values don't matter
            self.UpdateState(Action.GOFORWARD, percept, game_over=True)
            location = self.agentLocation
            if location not in self.unsafeLocations:
                self.unsafeLocations.append(location)
            self.searchEngine.RemoveSafeLocation(location[0], location[1])
            print("Found unsafe location " + str(location))
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
    
    def UpdateSafeLocations(self, location):
        # HW5 requirement 3b, and HW5 clarification about not known to be unsafe locations
        # Add current and adjacent locations to safe locations, unless known to be unsafe.
        if location not in self.safeLocations:
            self.safeLocations.append(location)
            self.searchEngine.AddSafeLocation(location[0], location[1])
        for adj_loc in self.AdjacentLocations(location):
            if (adj_loc not in self.safeLocations) and (adj_loc not in self.unsafeLocations):
                self.safeLocations.append(adj_loc)
                self.searchEngine.AddSafeLocation(adj_loc[0], adj_loc[1])
        
    def SafeUnvisitedLocation(self):
        # Find and return safe unvisited location
        for location in self.safeLocations:
            if location not in self.visitedLocations:
                return location
        return None
    
    def RemoveOutsideLocations(self):
        # Know exact world size, so remove locations outside the world.
        boundary = self.worldSize + 1
        for i in range(1,boundary):
            if [i,boundary] in self.safeLocations:
                self.safeLocations.remove([i,boundary])
                self.searchEngine.RemoveSafeLocation(i, boundary)
            if [boundary, i] in self.safeLocations:
                self.safeLocations.remove([boundary, i])
                self.searchEngine.RemoveSafeLocation(boundary, i)
        if [boundary, boundary] in self.safeLocations:
            self.safeLocations.remove([boundary, boundary])
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
