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
        # To help you understand this function, it creates a planning graph like
        # the Graphplan's way of solving plans, adding to our list of states
        # until we see the possibility of solving the goals, in which case we
        # just return the level of the solution.
        
        # First let's create a Graphplan's "possible literals in state" list
        all_state_predicates = set(initial_state)
        steps_taken = 0 # levels of the relaxed version of the planning problem

        # There's a catch in negative goals when we solve by the Graphplan method.
        # 
        # Here's an example: the "not garbage" predicate cannot be added to our
        # state because its representation is NOT EXISTING in our state, the
        # implementation forces us to REMOVE garbage from our "all predicates
        # list" which would invariably make it the _not_ "all predicate list".
        # Thats a very loose proof by contradition but the idea is what matters.
        # I solved that by having negative goals be removed from the mutable
        # set below as we do actions that remove the negative goals.
        negative_goals = set(negative_goals)
        
        # Let's attempt to add all possible results into this
        # all_state_predicates until we solve the goals

        while (steps_taken < 1000): # Bail if we tried over 999 combinations of actions
            if (self.are_goals_satisfied(all_state_predicates, positive_goals, negative_goals)):
                return steps_taken # Returns the level of the graph plan
            steps_taken += 1
            # Let's create a new state with all possible state parts we can do from our current state parts
            next_state_predicates = set(all_state_predicates)
            for action in actions:
                # Skip action if it cannot be executed at this state
                if (not action.positive_preconditions.issubset(all_state_predicates)):
                    continue

                # Step in which we add all new effects to the predicate list if it did not exist
                for predicate in action.add_effects:
                    next_state_predicates.add(predicate)
                # The reason we do not add directly to our all_state_predicates is because that would add a race condition to our action skipping algorithm

                for predicate in action.del_effects:
                    # Since negative goals are fundamentally different than the positive ones, we have to remove the negative goals until they are either empty or satisfy the initial state
                    negative_goals.discard(predicate)

            # Replace our old set of state parts with the new
            del all_state_predicates # That's optional because maybe this helps garbage collection.
            all_state_predicates = next_state_predicates
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
