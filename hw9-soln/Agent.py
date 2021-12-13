# Agent.py
#
# Fall 2021 HW9 solution.
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
        # HW9
        self.wumpusLocation = [0,0] # Wumpus location unknown
        self.wumpusAlive = True
        self.agentHasArrow = True
        self.stenchLocations = []
        self.breezeLocations = []
    
    def __del__(self):
        pass
    
    def Initialize(self):
        # Initialize agent back to the beginning of the world
        self.agentLocation = [1,1]
        self.agentOrientation = Orientation.RIGHT
        self.agentHasGold = False
        self.lastAction = Action.CLIMB # dummy action
        self.actionList = []
        # HW9
        self.agentHasArrow = True
        self.wumpusAlive = True
        if self.wumpusLocation in self.safeLocations:
            self.safeLocations.remove(self.wumpusLocation)
        self.searchEngine.RemoveSafeLocation(self.wumpusLocation[0], self.wumpusLocation[1])
    
    # Input percept is a dictionary [perceptName: boolean]
    def Process (self, percept):
        actionList2 = []
        self.UpdateState(self.lastAction, percept)
        if (self.actionList == []) and (percept.glitter):
            # HW5.4: If there is gold, then GRAB it
            print("Found gold. Grabbing it.")
            self.actionList.append(Action.GRAB)
        if (self.actionList == []) and (self.agentHasGold) and (self.agentLocation == [1,1]):
            # HW5.5: If agent has gold and is in (1,1), then CLIMB
            print("Have gold and in (1,1). Climbing.")
            self.actionList.append(Action.CLIMB)
        if (self.actionList == []) and (not self.agentHasGold) and (self.goldLocation != [0,0]):
            # HW5.6: If agent doesn't have gold, but knows its location, then navigate to that location
            print("Moving to known gold location (" + str(self.goldLocation[0]) + "," + str(self.goldLocation[1]) + ").")
            actionList2 = self.searchEngine.FindPath(self.agentLocation, self.agentOrientation,
                                                     self.goldLocation, self.agentOrientation)
            self.actionList.extend(actionList2)
        if (self.actionList == []) and (self.agentHasGold) and (self.agentLocation != [1,1]):
            # HW5.7: If agent has gold, but isn't in (1,1), then navigate to (1,1)
            print("Have gold. Moving to (1,1).")
            actionList2 = self.searchEngine.FindPath(self.agentLocation, self.agentOrientation, [1,1], self.agentOrientation)
            self.actionList.extend(actionList2)
        if (self.actionList == []):
            # If there's a safe unvisited location, so try to navigate there (may not be one for HW9)
            safeUnvisitedLocation = self.SafeUnvisitedLocation()
            if safeUnvisitedLocation:
                print("Moving to safe unvisited location " + str(safeUnvisitedLocation))
                actionList2 = self.searchEngine.FindPath(self.agentLocation, self.agentOrientation, safeUnvisitedLocation, self.agentOrientation)
                if actionList2:
                    self.actionList.extend(actionList2)
        if (self.actionList == []) and self.WumpusCanBeShot():
            wumpusShootLocation, wumpusShootOrientation = self.WumpusShootPosition() # HW9
            # Move to wumpus kill location and SHOOT
            print("Moving to shoot wumpus " + str(wumpusShootLocation))
            actionList2 = self.searchEngine.FindPath(self.agentLocation, self.agentOrientation, wumpusShootLocation, wumpusShootOrientation)
            if actionList2:
                self.actionList.extend(actionList2)
                self.actionList.append(Action.SHOOT)
            else:
                print("ERROR: no path to wumpus shot location") # for debugging
                sys.exit(1)
        if (self.actionList == []):
            # Move to location not known to be unsafe, but not next to a stench
            notUnSafeUnvisitedLocation = self.NotUnSafeUnvisitedLocation()
            if notUnSafeUnvisitedLocation:
                print("Moving to unvisited location not known to be unsafe " + str(notUnSafeUnvisitedLocation))
                actionList2 = self.searchEngine.FindPath(self.agentLocation, self.agentOrientation, notUnSafeUnvisitedLocation, self.agentOrientation)
                if actionList2:
                    self.actionList.extend(actionList2)
        if (self.actionList == []):
            print("ERROR: action list empty") # for debugging
            sys.exit(1)
        action = self.actionList.pop(0)
        self.lastAction = action
        return action
    
    def GameOver(self, score):
        if score < -1000:
            # Agent died by going forward into pit
            percept = Percept.Percept() # dummy, values don't matter
            self.UpdateState(Action.GOFORWARD, percept, game_over=True)
            location = self.agentLocation
            if location in self.safeLocations:
                self.safeLocations.remove(location)
            self.AddLocation(location, self.unsafeLocations)
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
        
        # HW9: If we're shooting, then it will always work
        if (lastAction == Action.SHOOT): # HW9
            self.agentHasArrow = False
            self.wumpusAlive = False
            self.AddLocation(self.wumpusLocation, self.safeLocations, addToSearch=True)
            
        if (lastAction == Action.CLIMB):
            pass # do nothing; if CLIMB worked, this won't be executed anyway
        
        # HW9
        if percept.stench:
            self.AddLocation(self.agentLocation, self.stenchLocations)
        if percept.breeze:
            self.AddLocation(self.agentLocation, self.breezeLocations)
            
        # HW5 requirement 3a
        if percept.glitter:
            self.goldLocation = self.agentLocation
            print("Found gold at " + str(self.goldLocation))
        # HW5 clarification: track world size
        new_max = max(self.agentLocation[0], self.agentLocation[1])
        if new_max > self.worldSize:
            self.worldSize = new_max
        if (self.wumpusLocation == [0,0]):
            self.LocateWumpus()
        # HW5 requirement 3b
        if not game_over:
            self.UpdateSafeLocations(self.agentLocation)
        # HW5 requirement 3c
        self.AddLocation(self.agentLocation, self.visitedLocations)
    
    def UpdateSafeLocations(self, location):
        # HW5 requirement 3b, and HW5 clarification about not known to be unsafe locations
        # Add current and adjacent locations to safe locations, unless known to be unsafe.
        # HW9: If location has stench, and wumpus still alive, then don't add adjacent locations
        self.AddLocation(location, self.safeLocations, addToSearch=True)
        if (location not in self.stenchLocations) or (not self.wumpusAlive):
            for adj_loc in self.AdjacentLocations(location):
                if (adj_loc not in self.unsafeLocations):
                    self.AddLocation(adj_loc, self.safeLocations, addToSearch=True)
        # Handle special case where location is the wumpus location
        # Recheck locations adjacent to stenches; some may have been skipped while wumpus alive
        if location == self.wumpusLocation:
            for location in self.stenchLocations:
                for adj_loc in self.AdjacentLocations(location):
                    if adj_loc not in self.unsafeLocations:
                        self.AddLocation(adj_loc, self.safeLocations, addToSearch=True)
        
    def SafeUnvisitedLocation(self):
        # Find and return safe unvisited location
        for location in self.safeLocations:
            if location not in self.visitedLocations:
                return location
        return None
    
    def NotUnSafeUnvisitedLocation(self):
        # Find and return unvisited location not known to be unsafe (excluding possible wumpus location)
        for location in self.visitedLocations:
            if location not in self.stenchLocations:
                for adj_loc in self.AdjacentLocations(location):
                    if (adj_loc not in self.visitedLocations) and (adj_loc not in self.unsafeLocations):
                        return adj_loc
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
    
    def AddLocation(self, location, location_list, addToSearch=False):
        if location not in location_list:
            location_list.append(location)
        if addToSearch:
            self.searchEngine.AddSafeLocation(location[0], location[1])
    
    def LocateWumpus(self):
        # Check stench and safe location info to see if wumpus can be located.
        # If located, then other locations adjacent to stenches are safe.
        for stench_location_1 in self.stenchLocations:
            x1 = stench_location_1[0]
            y1 = stench_location_1[1]
            for stench_location_2 in self.stenchLocations:
                x2 = stench_location_2[0]
                y2 = stench_location_2[1]
                if (x1 == x2-1) and (y1 == y2 - 1) and ([x1+1,y1] in self.safeLocations):
                    self.wumpusLocation = [x1,y1+1]
                if (x1 == x2-1) and (y1 == y2 - 1) and ([x1,y1+1] in self.safeLocations):
                    self.wumpusLocation = [x1+1,y1]
                if (x1 == x2+1) and (y1 == y2 - 1) and ([x1-1,y1] in self.safeLocations):
                    self.wumpusLocation = [x1,y1+1]
                if (x1 == x2+1) and (y1 == y2 - 1) and ([x1,y1+1] in self.safeLocations):
                    self.wumpusLocation = [x1-1,y1]
        if (self.wumpusLocation != [0,0]):
            print("Found wumpus at " + str(self.wumpusLocation))
    
    def WumpusCanBeShot(self): # HW9
        # Return True is Wumpus can be shot, i.e., wumpus is alive, wumpus location known,
        # agent has arrow, and there is a safe location in the same row or column as the wumpus.
        if not self.wumpusAlive:
            return False
        if self.wumpusLocation == [0,0]:
            return False
        if not self.agentHasArrow:
            return False
        for location in self.safeLocations:
            if (location[0] == self.wumpusLocation[0]) or (location[1] == self.wumpusLocation[1]):
                return True
        return False
    
    def WumpusShootPosition(self): # HW9
        # Return safe location in same row or column as wumpus and orientation facing wumpus.
        # Assumes Wumpus can be shot, i.e., location known.
        for location in self.safeLocations:
            if (location[0] == self.wumpusLocation[0]): # location above or below wumpus
                orientation = Orientation.UP
                if location[1] > self.wumpusLocation[1]:
                    orientation = Orientation.DOWN
                return location, orientation
            if (location[1] == self.wumpusLocation[1]): # location left or right of wumpus
                orientation = Orientation.RIGHT
                if location[0] > self.wumpusLocation[0]:
                    orientation = Orientation.LEFT
                return location, orientation
        return None, None # should never get here
