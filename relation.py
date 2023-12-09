import itertools
import variable
import domain
import assignment
import space
from collections.abc import Iterator, Iterable
from typing import Optional


class Relation:
    _domain_type = domain.Domain
    _space_type = space.Space
    _count: int = 0

    def __init__(self, variables: Iterable[variable.Variable], satisfies):
        self._inputs: list[variable.Variable] = list(variables)
        self._variables: set[variable.Variable] = set(self._inputs)
        self._satisfies = satisfies
        self._default_space = self._space_type(self._variables)

        # Sequential id for each relation for hashing
        self._id: int = Relation._count
        Relation._count += 1

    def __hash__(self):
        return hash(self._id)
    
    def __eq__(self, other: "Relation"):
        return self._id == other._id
    
    def __and__(self, other: "Relation"):
        return self.__class__(
            self._inputs + other._inputs,
            lambda *args: self._satisfies(*args[:self.arity]) and other._satisfies(*args[self.arity:])
        )
    
    def __or__(self, other: "Relation"):
        return self.__class__(
            self._inputs + other._inputs,
            lambda *args: self._satisfies(args[:self.arity]) or other._satisfies(args[self.arity:])
        )

    @property
    def arity(self) -> int:
        return len(self._inputs)

    @property
    def inputs(self) -> list[variable.Variable]:
        return self._inputs.copy()
    
    @property
    def variables(self) -> set[variable.Variable]:
        return set(self._variables)
    
    @property
    def default_space(self):
        return self._default_space
    
    def incomplete(self, assign: assignment.Assignment) -> bool:
        return not all(var in assign for var in self._inputs)
    
    def satisfied(self, assign: assignment.Assignment) -> bool:
        if self.incomplete(assign):
            return False
        return self._satisfies(*assign[self._inputs])

    def violated(self, assign: assignment.Assignment) -> bool:
        if self.incomplete(assign):
            return False
        return not self._satisfies(*assign[self._inputs])
    
    def pruned_space(self, given_space: Optional[_space_type] = None) -> _space_type:
        raise NotImplementedError

    @classmethod
    def pruned_space_for_all(cls, relations: Iterable["Relation"]) -> _space_type:
        """
        Inspired by AC3
        Same basic concept:
        - have a list of constraints to deal with
        - pick one
        - prune its domain
        - add to the list any other constraints that share a domain
        - repeat until list is empty
        """

        # Setup
        all_vars = set(itertools.chain.from_iterable(relation._variables for relation in relations))
        ret_space = cls._space_type(all_vars)

        # TODO: maybe put something to not recreate this is set of constraints remains the same?
        relations_by_var = {var: [] for var in all_vars}
        for relation in relations:
            for var in relation._variables:
                relations_by_var[var].append(relation)

        # Main loop
        remaining = set(relations)
        while remaining:
            for curr in remaining:
                break

            new_space = curr.pruned_space(ret_space)
            if new_space == ret_space:
                remaining.discard(curr)
                continue
            ret_space = new_space

            for var in curr._inputs:
                remaining.update(relations_by_var[var])
            remaining.discard(curr)

        return ret_space


class DiscreteRelation(Relation):
    _domain_type = domain.Domain
    _space_type = space.DiscreteSpace

    def __init__(self, variables: Iterable[variable.Variable], satisfies):
        if not all(isinstance(var.domain, self._domain_type) for var in variables):
            raise ValueError("All variables must have discrete domains")
        super().__init__(variables, satisfies)

    def __iter__(self) -> Iterator[assignment.Assignment]:
        return self.satisfying_assignments()

    def satisfying_assignments(self, given_space: Optional["_space_type"] = None) -> Iterator[assignment.Assignment]:
        # If you and together a bunch of relations, this can be used as a brute force solver
        if given_space is None:
            given_space = self._space_type()
        return (assign for assign in given_space[self._variables] if self.satisfied(assign))
    
    def nonviolating_assignments(self, given_space: Optional[_space_type] = None) -> Iterator[assignment.Assignment]:
        if given_space is None:
            given_space = self._space_type()
        return (assign for assign in given_space[self._variables] if not self.violated(assign))

    def pruned_space(self, given_space: Optional[_space_type] = None) -> _space_type:
        ret_space = self._space_type.empty(self._variables)
        for assign in self.nonviolating_assignments(given_space):
            for var in assign:
                ret_space.add(var, assign[var])
                # TODO: add loopbreaker for when ret_space is full
        return ret_space & given_space[set(given_space.variables()) - self._variables]
        # last line is equivalent to this:
        # return ret_space & given_space
        # but the way I wrote it should be faster
    


if __name__ == "__main__":
    from time import time

    def lt(a, b): return a < b
    def is_5(a): return a == 5

    dom = domain.DiscreteDomain(range(10))
    x_dom = dom.copy(); y_dom = dom.copy(); z_dom = dom.copy()
    x_var = variable.Variable(x_dom, "x")
    y_var = variable.Variable(y_dom, "y")
    z_var = variable.Variable(z_dom, "z")

    r_x = DiscreteRelation([x_var], is_5)
    r_xy = DiscreteRelation([x_var, y_var], lt)
    r_yz = DiscreteRelation([y_var, z_var], lt)

    pruned_space = DiscreteRelation.pruned_space_for_all([r_x, r_xy, r_yz])
    print("Pruned space:")
    for var, dom in pruned_space._domains.items():
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
