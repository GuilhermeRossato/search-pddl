from pddl.heuristic import Heuristic
import pddl.state
import pdb

class MaxHeuristic(Heuristic):
    def are_goals_satisfied(self, initial_state, positive_goals, negative_goals):
        return (pddl.state.applicable(initial_state, positive_goals, negative_goals))

    def can_apply_action_to_state(self, state, action):
        return pddl.state.applicable(state, action.positive_preconditions, action.negative_preconditions)

    def get_state_with_applied_action(self, state, action):
        return pddl.state.apply(state, action.add_effects, action.del_effects)
    
    def h(self, actions, initial_state, positive_goals, negative_goals, debug=False):
        if (self.are_goals_satisfied(initial_state, positive_goals, negative_goals)):
            return 0
        # List of all past states so we never cross the same state twice
        past_states = [initial_state]
        # List of where each past state came from, so we can backtrace if needed
        # Spoiler alert: we won't
        backtraces = [None]
        # A list to hold the cost of each path we find, so we can find which is closer
        path_costs = [0]
        # A list to keep track of all successfull path costs
        paths_heuristics = [];

        # I prefer a non-recursive approach because... because it's better.
        stateId = 0
        limit = 1000
        if (debug):
            print("Started with "+str(len(actions))+" possible actions")
        while (stateId < len(past_states)):
            #if ((stateId % 1000) == 0):
            #   print("We are at state id", stateId)
            limit -= 1 # Throtle so that we don't run forever somehow
            if (limit <= 0):
                print("Heuristic bail!")
                break
            state = past_states[stateId]
            cost = 1+path_costs[stateId]
            if (debug):
                print("Started at state["+str(stateId)+"]: ")
                for part in state:
                    print("\t",part)
            for action in actions:
                # Skip action if it cannot be executed at this state
                if (not self.can_apply_action_to_state(state, action)):
                    #print("Cannot apply that action")
                    continue
                # Create new state with that action
                new_state = self.get_state_with_applied_action(state, action)
                # Check if we reached the destination
                if (self.are_goals_satisfied(new_state, positive_goals, negative_goals)):
                    # Record that cost, so we can compare with others
                    paths_heuristics.append(cost)
                    # We don't need to keep doing anything, so let's just skip
                    continue
                # Skip new state if it has already been visited
                if (new_state in past_states):
                    continue
                # Add this new node to our lists
                past_states.append(new_state)
                backtraces.append(stateId)
                path_costs.append(cost)
            stateId += 1
        # Return the greatest path cost we have (max)
        if (len(paths_heuristics) > 0):
            if (debug):
                print("Our return options are: ", str(paths_heuristics));
            return max(paths_heuristics)
        if (debug):
            print("No path found. Returning inf");
        return float("inf")


if __name__ == '__main__':
    from pddl.pddl_parser import PDDL_Parser
    from pddl.action import Action
    from pddl.state import applicable, apply
    import sys

    dwr = "examples/dwr/dwr.pddl"
    pb1_dwr = "examples/dwr/pb1.pddl"
    pb2_dwr = "examples/dwr/pb2.pddl"

    tsp = "examples/tsp/tsp.pddl"
    pb1_tsp = "examples/tsp/pb1.pddl"

    dinner = "examples/dinner/dinner.pddl"
    pb1_dinner = "examples/dinner/pb1.pddl"

    def parse_domain_problem(domain, problem):
        parser = PDDL_Parser()
        parser.parse_domain(domain)
        parser.parse_problem(problem)
        actions = []
        for action in parser.actions:
            for act in action.groundify(parser.objects):
                actions.append(act)
        return parser, actions

    def test_heuristic(domain, problem, h, expected):
        parser, actions = parse_domain_problem(domain, problem)
        #try:
        v = h.h(actions, parser.state, parser.positive_goals, parser.negative_goals, True)
        if (v == expected):
            print(" -> Success: "+str(v)+" == "+str(expected)+" at domain \""+str(domain)+"\"")
        else:
            print(" -> Error: "+str(v)+" != "+str(expected)+" at domain \""+str(domain)+"\"")
        #except:
            #print("Runtime Error: "+str(sys.exc_info()[0]))

    # Apply Hmax to initial states of many problems from many domains
    h = MaxHeuristic()
    test_heuristic(dwr, pb1_dwr, h, 6)
    test_heuristic(dwr, pb2_dwr, h, 0)
    test_heuristic(tsp, pb1_tsp, h, 2)
    test_heuristic(dinner, pb1_dinner, h, 1)
