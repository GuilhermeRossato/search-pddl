from pddl.pddl_planner import PDDL_Planner
from pddl.heuristic import Heuristic
from MaxHeuristicFile import MaxHeuristic
import pddl.state
import sys

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
        # List of all past states so we never cross the same state twice
        past_states = [initial_state]
        # List of where each past state came from, so we can backtrace if needed
        backtraces = [None]
        actions_taken = [None]
        # A list to hold the cost of each path we find, so we can find which is closer
        path_costs = [0]
        # A list to keep track of all successfull path costs
        paths_heuristics = [];
        
        stateId = 0
        limit = 10000
        while (stateId < len(past_states)):
            # Iteration limiter so we don't run out of memory!
            limit -= 1 
            if (limit <= 0):
                print("Heuristic bail!")
                break
            state = past_states[stateId]
            cost = 1+path_costs[stateId]
            for action in actions:
                # Skip action if it cannot be executed at this state
                if (not self.can_apply_action_to_state(state, action)):
                    continue
                # Create new state with that action
                new_state = self.get_state_with_applied_action(state, action)
                # Check if we reached the destination
                if (self.are_goals_satisfied(new_state, positive_goals, negative_goals)):
                    return range(0, cost);
                # Skip new state if it has already been visited
                if (new_state in past_states):
                    continue
                # Add this new node to our lists
                past_states.append(new_state)
                backtraces.append(stateId)
                path_costs.append(cost)
                actions_taken.append(actions)
            stateId += 1
        
        if (debug):
            print("No path found. Returning None");
        return None


if __name__ == '__main__':
    #Student_tests
    dwr = "examples/dwr/dwr.pddl"
    pb1 = "examples/dwr/pb1.pddl"
    pb2 = "examples/dwr/pb2.pddl"
    planner = Heuristic_Planner()

    plan, time = planner.solve_file(dwr, pb1, False)
    print("Expected 17, got:", str(len(plan)) + ('. Correct!' if len(plan) == 17 else '. False!'))
    plan, time = planner.solve_file(dwr, pb2, False)
    print("Expected 0, got:", str(len(plan)) + ('. Correct!' if len(plan) == 0 else '. False!'))
