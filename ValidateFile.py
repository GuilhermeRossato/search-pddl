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
		if (action is None):
			print("No action in apply action to state");
			return False;
		if (state is None):
			print("No state in apply action to state");
			return False;
		if (action.positive_preconditions is None):
			print("No action.positive_preconditions in apply action to state");
			return False;
		if (action.negative_preconditions is None):
			print("No action.negative_preconditions in apply action to state");
			return False;
		return pddl.state.applicable(state, action.positive_preconditions, action.negative_preconditions)

	def get_state_with_applied_action(self, state, action):
		return pddl.state.apply(state, action.add_effects, action.del_effects)


	# =====================================
	# Params:
	# actions -> list of ground actions
	# initial_state -> initial state of the problem file
	# positive_goals -> positive predicates of the goal
	# negative_goals -> negative predicates of the goal
	# plan -> plan parsed from a plan trace
	# =====================================
	def validate(self, actions, initial_state, positive_goals, negative_goals, plan):
		state = initial_state
		for action in plan:
			if (not self.can_apply_action_to_state(state, action)):
				break
			state = self.get_state_with_applied_action(state, action)
		return self.are_goals_satisfied(state, positive_goals, negative_goals)
