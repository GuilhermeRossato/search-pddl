#!/usr/bin/env python
# Four spaces as indentation [no tabs]

import itertools

class Action:

    def __init__(self, name, parameters, positive_preconditions, negative_preconditions, add_effects, del_effects):
        self.name = name
        self.parameters = parameters
        self.positive_preconditions = positive_preconditions
        self.negative_preconditions = negative_preconditions
        self.add_effects = add_effects
        self.del_effects = del_effects

    def __str__(self):
        s = 'action: ' + self.name
        if (self.parameters):
            s += '\n  parameters: ' + str(self.parameters)
        if (self.positive_preconditions):
            s += '\n  positive_preconditions: ' + str(list(self.positive_preconditions))
        if (self.negative_preconditions):
            s += '\n  negative_preconditions: ' + str(list(self.negative_preconditions))
        if (self.add_effects):
            s += '\n  add_effects: ' + str(list(self.add_effects))
        if (self.del_effects):
            s += '\n  del_effects: ' + str(list(self.del_effects))
        s += '\n'
        return s

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def groundify(self, objects):
        if not self.parameters:
            yield self
            return
        type_map = []
        variables = []
        for var, type in self.parameters:
            type_map.append(objects[type])
            variables.append(var)
        for assignment in itertools.product(*type_map):
            positive_preconditions = self.replace(self.positive_preconditions, variables, assignment)
            negative_preconditions = self.replace(self.negative_preconditions, variables, assignment)
            add_effects = self.replace(self.add_effects, variables, assignment)
            del_effects = self.replace(self.del_effects, variables, assignment)
            yield Action(self.name, assignment, positive_preconditions, negative_preconditions, add_effects, del_effects)

    def replace(self, group, variables, assignment):
        g = []
        for pred in group:
            a = pred
            iv = 0
            for v in variables:
                while v in a:
                    i = a.index(v)
                    a = a[:i] + tuple([assignment[iv]]) + a[i+1:]
                iv += 1
            g.append(a)
        return frozenset(g)

if __name__ == '__main__':
    a = Action('move', [['?ag', 'agent'], ['?from', 'pos'], ['?to', 'pos']],
        frozenset([tuple(['at', '?ag', '?from']), tuple(['adjacent', '?from', '?to'])]),
        frozenset([tuple(['at', '?ag', '?to'])]),
        frozenset([tuple(['at', '?ag', '?to'])]),
        frozenset([tuple(['at', '?ag', '?from'])])
    )
    print(a)

    objects = {
        'agent': ['ana','bob'],
        'pos': ['p1','p2']
    }
    for act in a.groundify(objects):
        print(act)
