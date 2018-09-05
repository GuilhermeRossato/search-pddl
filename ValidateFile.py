from pddl.pddl_parser import PDDL_Parser
from pddl.action import Action
from pddl.state import applicable, apply
import pddl

class Validator:
    def parse_plan(self, filename):
        with open(filename,'r') as f:
            plan = []
            for act in f.read().splitlines():
                act = act[1:-1].split()
                plan.append(Action(act[0], tuple(act[1:]), None, None, None, None))
            return plan

    def validate_file(self, domainfile, problemfile, planfile):
        return self.validate_plan(domainfile, problemfile, self.parse_plan(planfile))

    def validate_plan(self, domainfile, problemfile, plan):
        parser = PDDL_Parser()
        parser.parse_domain(domainfile)
        parser.parse_problem(problemfile)
        # Grounding process
        ground_actions = []
        for action in parser.actions:
            for act in action.groundify(parser.objects):
                ground_actions.append(act)
        return self.validate(ground_actions, parser.state, parser.positive_goals, parser.negative_goals, plan)
    
    # Obvious helper methods to make my code more verbose
    def are_goals_satisfied(self, initial_state, positive_goals, negative_goals):
        return (pddl.state.applicable(initial_state, positive_goals, negative_goals))

    def can_apply_action_to_state(self, state, action):
        return pddl.state.applicable(state, action.positive_preconditions, action.negative_preconditions)

    def get_state_with_applied_action(self, state, action):
        return pddl.state.apply(state, action.add_effects, action.del_effects)

    def fix_incomplete_plan(self, plan, actions):
        """
        Once upon a time someone instanced a class without it's constructor parameters.
        Little did he know that optional parameters are for parameters that are optional.
        This method tries to solve this inconsistency.
        """
        correct_plan = []
        for frankenstein in plan: # It stops being an "Action" when it becomes an incomplete object
            for action in actions:
                # Is the action it should be in the first place?
                if (action.name == frankenstein.name and action.parameters == frankenstein.parameters):
                    correct_plan.append(action)
                    continue
        return correct_plan

    # =====================================
    # Params:
    # actions -> list of ground actions
    # initial_state -> initial state of the problem file
    # positive_goals -> positive predicates of the goal
    # negative_goals -> negative predicates of the goal
    # plan -> plan parsed from a plan trace
    # 
    # Returns:
    # True when following the plan implies on finishing at a state that satisfy the goals
    # =====================================
    def validate(self, actions, initial_state, positive_goals, negative_goals, plan):
        correct_plan = self.fix_incomplete_plan(plan, actions);
        state = initial_state
        for action in correct_plan:
            if (not self.can_apply_action_to_state(state, action)):
                return False
            state = self.get_state_with_applied_action(state, action)
        # The plan only works if you finish the goal at the last step!
        return self.are_goals_satisfied(state, positive_goals, negative_goals)

if __name__ == '__main__':
    dwr = "examples/dwr/dwr.pddl"
    pb1 = "examples/dwr/pb1.pddl"
    plan1 = "examples/dwr/dwr_pb1_bfs.plan"
    plan2 = "examples/dwr/dwr_pb1_heuristic.plan"
    plan_empty = "examples/dwr/empty.plan"
    val = Validator()
    print("Expected True, got:", str(val.validate_file(dwr, pb1, plan1)))
    print("Expected True, got:", str(val.validate_file(dwr, pb1, plan2)))
    print("Expected False, got:", str(val.validate_file(dwr, pb1, plan_empty)))
