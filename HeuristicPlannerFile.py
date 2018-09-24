from pddl.pddl_planner import PDDL_Planner
from pddl.heuristic import Heuristic
from MaxHeuristicFile import MaxHeuristic
import pddl.state
import sys
from heapq import heappush, heappop

class Heuristic_Planner(PDDL_Planner):

    def __init__(self, heuristic=MaxHeuristic()):
        self.h = heuristic
        
    # Obvious helper methods to make my code more verbose
    def are_goals_satisfied(self, initial_state, positive_goals, negative_goals):
        return (pddl.state.applicable(initial_state, positive_goals, negative_goals))

    def can_apply_action_to_state(self, state, action):
        return pddl.state.applicable(state, action.positive_preconditions, action.negative_preconditions)

    def get_state_with_applied_action(self, state, action):
        return pddl.state.apply(state, action.add_effects, action.del_effects)

    def push_state_to_queue(self, elements, actions, state, positive_goals, negative_goals, path_cost, backtraceId):
        # f(x) = g(x) + h(x)
        # f -> priority
        # g -> path cost result
        # h -> heuristic function result
        priority = path_cost + self.h.h(actions, state, positive_goals, negative_goals)

        # content has the following content:
        # state -> because we need to remember what states are open
        # path_cost -> so that we don't recalculate the cost everytime which is costly
        # backtraceId -> to easily re-create the backtrace
        content = [state, path_cost, backtraceId]
        heappush(elements, (priority, content))

    def pop_state_from_queue(self, elements):
        return heappop(elements)[1]

    def generate_plan(self, backtraces, backtraceId):
        limit = 10000 # Limit so we don't run out of memory
        # Hindsight is the reversed steps, since we are going backwards
        hindsight = []
        while (backtraces[backtraceId]):
            #print("Jump to ",backtraces[backtraceId][1]," at action ", backtraces[backtraceId][0].name, backtraces[backtraceId][0].parameters)
            limit -= 1;
            if (limit <= 0):
                print("Reached limit, bailing plan generation")
                return []

            backtrack = backtraces[backtraceId]
            action = backtrack[0]
            hindsight.append(action)
            if (backtraceId <= backtrack[1]):
                print("Cannot backtrack into the future, that isn't possible")
                return []
            backtraceId = backtrack[1]
        return hindsight[::-1] #Reverse hindsight to give correct output


    # -----------------------------------------------
    # Solve
    # -----------------------------------------------
    
    # =====================================
    # Params:
    # actions -> list of grounded actions
    # initial_state -> initial state of the problem file
    # positive_goals -> positive predicates of the goal
    # negative_goals -> negative predicates of the goal
    #
    # Returns:
    # A plan (list of Actions) that solves the goal from the initial_state
    # =====================================
    
    def solve(self, actions, initial_state, positive_goals, negative_goals):
        if (self.are_goals_satisfied(initial_state, positive_goals, negative_goals)):
            return 0

        elements = [];
        self.push_state_to_queue(elements, actions, initial_state, positive_goals, negative_goals, 0, 0)

        backtraces = [None]
        past_states = [initial_state]
        backtracesId = 0

        stateId = 0
        limit = 10000
        while (len(elements) > 0):
            # Iteration limiter so we don't run out of memory!
            limit -= 1 
            if (limit <= 0):
                print("Heuristic bail!")
                break

            state, path_cost, backtraceId = self.pop_state_from_queue(elements)
            cost = path_cost+1;

            for action in actions:
                # Skip action if it cannot be executed at this state
                if (not self.can_apply_action_to_state(state, action)):
                    continue
                # Create new state with that action
                new_state = self.get_state_with_applied_action(state, action)

                # Add the action to backtrace so that we can create a plan later
                backtraces.append((action, backtraceId))

                # Check if we reached the destination
                if (self.are_goals_satisfied(new_state, positive_goals, negative_goals)):
                    #print("Returning after", stateId, "expansions")
                    return self.generate_plan(backtraces, len(backtraces)-1);
                # Skip new state if it has already been visited
                if (new_state in past_states):
                    continue
                # Mark that state as visited
                past_states.append(new_state)
                # Add this new node to our lists
                self.push_state_to_queue(elements, actions, new_state, positive_goals, negative_goals, cost, len(backtraces)-1)

            stateId += 1
        return None


if __name__ == '__main__':
    #Student_tests
    dwr = "examples/dwr/dwr.pddl"
    pb1 = "examples/dwr/pb1.pddl"
    pb2 = "examples/dwr/pb2.pddl"
    planner = Heuristic_Planner()

    plan, time = planner.solve_file(dwr, pb1, False)
    if (plan == None):
        print("Expected 17, got None, False!");
    else:
        print("Expected 17, got:", str(len(plan)) + ('. Correct!' if len(plan) == 17 else '. False!'))
    plan, time = planner.solve_file(dwr, pb2, False)
    if (plan == None):
        print("Expected 0, got None, False!");
    else:
        print("Expected 0, got:", str(len(plan)) + ('. Correct!' if len(plan) == 0 else '. False!'))
