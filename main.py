import relation
import variable
import domain
import itertools
import assignment

def backtracking_solver(constraints: list[relation.DiscreteRelation]):
    vars = set(itertools.chain.from_iterable(relation._variables for relation in constraints))
    curr_space = relation.Relation.pruned_space_for_all(constraints)
    curr_assignment = assignment.Assignment()

    def helper():
        if len(curr_assignment) == len(vars):
            return all(relation.satisfied(curr_assignment) for relation in constraints)
        
        assign_var = min(vars, key=lambda var: float("inf") if var in curr_assignment else len(curr_space[var]))
        for val in curr_space[assign_var]:
            # FIXME: this checks for value validity, but I think we can guarantee that it's valid
            curr_assignment[assign_var] = val
            # TODO: Constraint propagation here?
            if helper():
                return True
            curr_assignment.unassign(assign_var)
        return False
    
    return curr_assignment

if __name__ == '__main__':
    pass
