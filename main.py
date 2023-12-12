import relation
import variable
import domain
import itertools
import assignment

def backtracking_solver(constraints: list[relation.DiscreteRelation]):
    vars = set(itertools.chain.from_iterable(relation._variables for relation in constraints))
    curr_space = relation.DiscreteRelation.pruned_space_for_all(constraints)
    curr_assignment = assignment.Assignment()

    def helper():
        if len(curr_assignment) == len(vars):
            return all(relation.satisfied(curr_assignment) for relation in constraints)
        
        assign_var = min(vars, key=lambda var: float("inf") if var in curr_assignment else len(curr_space[var]))
        for val in curr_space[assign_var]:
            # FIXME: this checks for value validity, but I think we know guarantee that it's valid
            curr_assignment[assign_var] = val
            # TODO: Constraint propagation here?
            if helper():
                return True
            curr_assignment.unassign(assign_var)
        return False
    
    helper()
    return curr_assignment

if __name__ == '__main__':
    import space
    from time import time

    def lt(a, b): return a < b
    def is_5(a): return a == 5

    dom = domain.DiscreteDomain(range(10))
    x_dom = dom.copy(); y_dom = dom.copy(); z_dom = dom.copy()
    x_var = variable.Variable(x_dom, "x")
    y_var = variable.Variable(y_dom, "y")
    z_var = variable.Variable(z_dom, "z")

    r_x = relation.DiscreteRelation([x_var], is_5)
    r_xy = relation.DiscreteRelation([x_var, y_var], lt)
    r_yz = relation.DiscreteRelation([y_var, z_var], lt)

    pruned_space = relation.DiscreteRelation.pruned_space_for_all([r_x, r_xy, r_yz])
    print("Pruned space:")
    for var, dom in pruned_space._domains.items():
        print(var, dom.elements)

    input_space = space.Space.from_assignment(assignment.Assignment({y_var: 7}))
    pruned_space_2 = relation.DiscreteRelation.pruned_space_for_all([r_x, r_xy, r_yz], current_space=input_space, updated_variable=y_var)
    print("Pruned space after assignment:")
    for var, dom in pruned_space_2._domains.items():
        print(var, dom.elements)

    r_total = r_x & r_xy & r_yz
    s = time()
    print("Answers:")
    for ans in r_total.satisfying_assignments():
        print(ans)
    print("time:", time() - s)

    s = time()
    print("Answers from pruned space:")
    for ans in r_total.satisfying_assignments(pruned_space):
        print(ans)
    print("time:", time() - s)

    s = time()
    print("Answer from backtracking solver:")
    ans = backtracking_solver([r_x, r_xy, r_yz])
    print(ans)
    print("time:", time() - s)
