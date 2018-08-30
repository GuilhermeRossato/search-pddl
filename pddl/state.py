#-----------------------------------------------
# Applicable
#
# Check if the positive and negative preconditions are met in a given state
# @return bool
#-----------------------------------------------

def applicable(state, positive, negative):
    return positive.issubset(state) and not negative.intersection(state)

#-----------------------------------------------
# Apply
#
# Given a state, apply the positive and negative effects to it
# @return frozenset A new state, modified by the effects given from the parameters
#-----------------------------------------------

def apply(state, positive, negative):
    return frozenset(state.union(positive).difference(negative))