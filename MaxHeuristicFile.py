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
    
    def h(self, actions, initial_state, positive_goals, negative_goals):
        if (self.are_goals_satisfied(initial_state, positive_goals, negative_goals)):
            return 0
        past_states = [initial_state]
        backtraces = [None]
        path_costs = [0]
        paths_heuristics = [];

        stateId = 0
        limit = 1000
        while (stateId < len(past_states)):
            if (limit <= 0):
                break
            state = past_states[stateId]
            cost = 1+path_costs[stateId]
            for action in actions:
                if (not self.can_apply_action_to_state(state, action)):
                    continue
                new_state = self.get_state_with_applied_action(state, action)
                if (self.are_goals_satisfied(new_state, positive_goals, negative_goals)):
                    paths_heuristics.append(cost)
                    continue
                if (new_state in past_states):
                    continue
                past_states.append(new_state)
                backtraces.append(stateId)
                path_costs.append(cost)
            stateId += 1
        if (len(paths_heuristics) > 0):
            return max(paths_heuristics)
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
        v = h.h(actions, parser.state, parser.positive_goals, parser.negative_goals)
        if (v == expected):
            print(" -> Success: "+str(v)+" == "+str(expected)+" at domain \""+str(domain)+"\"")
        else:
            print(" -> Error: "+str(v)+" != "+str(expected)+" at domain \""+str(domain)+"\"")

    h = MaxHeuristic()
    test_heuristic(tsp, pb1_tsp, h, 2)
    #test_heuristic(dinner, pb1_dinner, h, 1)
