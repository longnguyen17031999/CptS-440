// Agent.h

#ifndef AGENT_H
#define AGENT_H

#include "Action.h"
#include "Percept.h"

#include "WorldState.h"
#include <list>

class Agent
{
public:
	Agent ();
	~Agent ();
	void Initialize ();
	Action Process (Percept& percept);
	void GameOver (int score);
	
	void UpdateState (Percept& percept);
	void Move();

	WorldState worldState;
	list<Action> actionList;
	Action previousAction;
};

#endif // AGENT_H
