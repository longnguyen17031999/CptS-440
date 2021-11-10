// Agent.cc
//
// Fall 2021 HW5 solution.
//
// Written by Larry Holder.

#include <iostream>
#include <list>
#include "Agent.h"
#include "Action.h"

using namespace std;

int MySearchEngine::HeuristicFunction(SearchState* state, SearchState* goalState) {
	int cityBlock = abs(state->location.X - goalState->location.X) + abs(state->location.Y - goalState->location.Y);
	return cityBlock;
	//return 0; // not a good heuristic
}

Agent::Agent ()
{
	// Initialize new agent based on new, unknown world
	worldState.agentLocation = Location(1,1);
	worldState.agentOrientation = RIGHT;
	worldState.agentHasGold = false;
	lastAction = CLIMB; // dummy action
	worldState.worldSize = 3; // HW5: somewhere between 3x3 and 9x9
	worldSizeKnown = false;
	worldState.goldLocation = Location(0,0); // unknown
}

Agent::~Agent ()
{

}

void Agent::Initialize ()
{
	// Initialize agent back to the beginning of the world
	worldState.agentLocation = Location(1,1);
	worldState.agentOrientation = RIGHT;
	worldState.agentAlive = true;
	worldState.agentHasGold = false;
	lastAction = CLIMB; // dummy action
	actionList.clear();
}

Action Agent::Process (Percept& percept)
{
	list<Action> actionList2;
		UpdateState(lastAction, percept);
		if (actionList.empty()) {
			if (percept.Glitter) {
				// HW5.4: If there is gold, then GRAB it
				cout << "Found gold. Grabbing it.\n";
				actionList.push_back(GRAB);
			} else if (worldState.agentHasGold && (worldState.agentLocation == Location(1,1))) {
				// HW5.5: If agent has gold and is in (1,1), then CLIMB
				cout << "Have gold and in (1,1). Climbing.\n";
				actionList.push_back(CLIMB);
			} else if (!worldState.agentHasGold && !(worldState.goldLocation == Location(0,0))) {
				// HW5.6: If agent doesn't have gold, but knows its location, then navigate to that location
				cout << "Moving to known gold location (" << worldState.goldLocation.X << "," << worldState.goldLocation.Y << ").\n";
				actionList2 = searchEngine.FindPath(worldState.agentLocation, worldState.agentOrientation, worldState.goldLocation, worldState.agentOrientation);
				actionList.splice(actionList.end(), actionList2);
			} else if (worldState.agentHasGold && !(worldState.agentLocation == Location(1,1))) {
				// HW5.7: If agent has gold, but isn't in (1,1), then navigate to (1,1)
				cout << "Have gold. Moving to (1,1).\n";
				actionList2 = searchEngine.FindPath(worldState.agentLocation, worldState.agentOrientation, Location(1,1), worldState.agentOrientation);
				actionList.splice(actionList.end(), actionList2);
			} else {
				// HW5.8: If safe unvisited location, then navigate there (should be one)
				Location safeUnvisitedLocation = SafeUnvisitedLocation();
				cout << "Moving to safe unvisited location (" << safeUnvisitedLocation.X << "," << safeUnvisitedLocation.Y << ").\n";
				actionList2 = searchEngine.FindPath(worldState.agentLocation, worldState.agentOrientation, safeUnvisitedLocation, worldState.agentOrientation);
				if (!(actionList2.empty())) {
					actionList.splice(actionList.end(), actionList2);
				} else {
					cout << "ERROR: no path to safe unvisited location\n"; // for debugging
					exit(1);
				}
			}
		}
		Action action = actionList.front();
		actionList.pop_front();
		lastAction = action;
		return action;
}

void Agent::GameOver (int score)
{
	if (score < -1000) {
		// Agent died by going forward into pit or Wumpus
		Percept percept; // dummy, values don't matter
		UpdateState(GOFORWARD, percept, true);
		int X = worldState.agentLocation.X;
		int Y = worldState.agentLocation.Y;
		if (!(MemberLocation(worldState.agentLocation, unsafeLocations))) {
			unsafeLocations.push_back(worldState.agentLocation);
		}
		searchEngine.RemoveSafeLocation(X,Y);
		cout << "Found unsafe location at (" << X << "," << Y << ")\n";
	}
}

void Agent::UpdateState(Action lastAction, Percept& percept, bool gameOver) {
	int X = worldState.agentLocation.X;
	int Y = worldState.agentLocation.Y;
	Orientation orientation = worldState.agentOrientation;

	if (lastAction == TURNLEFT) {
		worldState.agentOrientation = (Orientation) ((orientation + 1) % 4);
	}
	if (lastAction == TURNRIGHT) {
		if (orientation == RIGHT) {
			worldState.agentOrientation = DOWN;
		} else {
			worldState.agentOrientation = (Orientation) (orientation - 1);
		}
	}
	if (lastAction == GOFORWARD) {
		if (percept.Bump) {
			if ((orientation == RIGHT) || (orientation == UP)) {
				cout << "World size known to be " << worldState.worldSize << "x" << worldState.worldSize << endl;
				worldSizeKnown = true;
				RemoveOutsideLocations();
			}
		} else {
			switch (orientation) {
			case UP:
				worldState.agentLocation.Y = Y + 1;
				break;
			case DOWN:
				worldState.agentLocation.Y = Y - 1;
				break;
			case LEFT:
				worldState.agentLocation.X = X - 1;
				break;
			case RIGHT:
				worldState.agentLocation.X = X + 1;
				break;
			}
		}
	}
	if (lastAction == GRAB) { // Assume GRAB only done if Glitter was present
		worldState.agentHasGold = true;
	}
	if (lastAction == CLIMB) {
		// do nothing; if CLIMB worked, this won't be executed anyway
	}
	// HW5 requirement 3a
	if (percept.Glitter) {
		worldState.goldLocation = worldState.agentLocation;
		cout << "Found gold at (" << worldState.goldLocation.X << "," << worldState.goldLocation.Y << ")\n";
	}
	// HW5 clarification: track world size
	int new_max = max(worldState.agentLocation.X, worldState.agentLocation.Y);
	if (new_max > worldState.worldSize) {
		worldState.worldSize = new_max;
	}
	// HW5 requirement 3b
	if (!gameOver) {
		UpdateSafeLocations(worldState.agentLocation);
	}
	// HW5 requirement 3c
	if (!(MemberLocation(worldState.agentLocation, visitedLocations))) {
		visitedLocations.push_back(worldState.agentLocation);
	}
}

bool Agent::MemberLocation(Location& location, list<Location>& locationList) {
	if (find(locationList.begin(), locationList.end(), location) != locationList.end()) {
		return true;
	}
	return false;
}

Location Agent::SafeUnvisitedLocation() {
	// Find and return safe unvisited location.
	list<Location>::iterator loc_itr;
	for (loc_itr = safeLocations.begin(); loc_itr != safeLocations.end(); ++loc_itr) {
		if (!(MemberLocation(*loc_itr, visitedLocations))) {
			return *loc_itr;
		}
	}
	return Location(0,0);
}

void Agent::UpdateSafeLocations(Location& location) {
	// HW5 requirement 3b, and HW5 clarification about not known to be unsafe locations
    // Add current and adjacent locations to safe locations, unless known to be unsafe.
	if (!(MemberLocation(location, safeLocations))) {
		safeLocations.push_back(location);
		searchEngine.AddSafeLocation(location.X, location.Y);
	}
	list<Location> adj_locs;
	AdjacentLocations(location, adj_locs);
	list<Location>::iterator loc_itr;
	for (loc_itr = adj_locs.begin(); loc_itr != adj_locs.end(); ++loc_itr) {
		if ((!(MemberLocation(*loc_itr, safeLocations))) && (!(MemberLocation(*loc_itr, unsafeLocations)))) {
			safeLocations.push_back(*loc_itr);
			searchEngine.AddSafeLocation(loc_itr->X, loc_itr->Y);
		}
	}
}

void Agent::RemoveOutsideLocations() {
	// Know exact world size, so remove locations outside the world.
	int boundary = worldState.worldSize + 1;
	for (int i = 1; i < boundary; ++i) {
		safeLocations.remove(Location(i,boundary));
		searchEngine.RemoveSafeLocation(i,boundary);
		safeLocations.remove(Location(boundary,i));
		searchEngine.RemoveSafeLocation(boundary,i);
	}
	safeLocations.remove(Location(boundary,boundary));
	searchEngine.RemoveSafeLocation(boundary,boundary);
}

void Agent::AdjacentLocations(Location& location, list<Location>& adjacentLocations) {
	// Append locations adjacent to given location on to give locations list.
	// One row/col beyond unknown world size is okay. Locations outside the world
	// will be removed later.
	int X = location.X;
	int Y = location.Y;
	if (X > 1) {
		adjacentLocations.push_back(Location(X-1,Y));
	}
	if (Y > 1) {
		adjacentLocations.push_back(Location(X,Y-1));
	}
	if (worldSizeKnown) {
		if (X < worldState.worldSize) {
			adjacentLocations.push_back(Location(X+1,Y));
		}
		if (Y < worldState.worldSize) {
			adjacentLocations.push_back(Location(X,Y+1));
		}
	} else {
		adjacentLocations.push_back(Location(X+1,Y));
		adjacentLocations.push_back(Location(X,Y+1));
	}
}
