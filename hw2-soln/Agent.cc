// Agent.cc
//
// HW2 Fall 2021

#include <iostream>
#include "Agent.h"

#include "Action.h"
#include "Location.h"
#include "Orientation.h"

using namespace std;

Agent::Agent ()
{

}

Agent::~Agent ()
{

}

void Agent::Initialize ()
{
	worldState.agentLocation = Location(1,1);
	worldState.agentOrientation = RIGHT;
	worldState.agentHasArrow = true;
	worldState.agentHasGold = false;
	actionList.clear();
	previousAction = CLIMB; // dummy action to start
}

Action Agent::Process (Percept& percept)
{
	UpdateState(percept);
	if (actionList.empty()) {
		if (percept.Glitter) { // Rule 3a
			actionList.push_back(GRAB);
		} else if (worldState.agentHasGold && (worldState.agentLocation == Location(1,1))) { // Rule 3b
			actionList.push_back(CLIMB);
		} else if (percept.Stench && worldState.agentHasArrow) { // Rule 3c
			actionList.push_back(SHOOT);
		} else { // Rule 3d
			int randomActionIndex = rand() % 3; // 0=GOFORWARD, 1=TURNLEFT, 2=TURNRIGHT
			Action randomAction = (Action) randomActionIndex;
			actionList.push_back(randomAction);
		}
	}
	Action action = actionList.front();
	actionList.pop_front();
	previousAction = action;
	return action;
}

void Agent::GameOver (int score)
{

}

void Agent::UpdateState (Percept& percept) {
	int orientationInt = (int) worldState.agentOrientation;
	switch (previousAction) {
	case GOFORWARD:
		if (! percept.Bump) {
			Move();
		}
		break;
	case TURNLEFT:
		worldState.agentOrientation = (Orientation) ((orientationInt + 1) % 4);
		break;
	case TURNRIGHT:
		orientationInt--;
		if (orientationInt < 0) orientationInt = 3;
		worldState.agentOrientation = (Orientation) orientationInt;
		break;
	case GRAB:
		worldState.agentHasGold = true; // Only GRAB when there's gold
		break;
	case SHOOT:
		worldState.agentHasArrow = false;
	case CLIMB:
		break;
	}
}
	
void Agent::Move() {
	switch (worldState.agentOrientation) {
	case RIGHT:
		worldState.agentLocation.X++;
		break;
	case UP:
		worldState.agentLocation.Y++;
		break;
	case LEFT:
		worldState.agentLocation.X--;
		break;
	case DOWN:
		worldState.agentLocation.Y--;
		break;
	}
}


