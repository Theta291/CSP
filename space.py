import domain
import variable
import assignment
import itertools
from typing import Optional
from collections.abc import Mapping, Iterator, Iterable


class Space:
    _domain_type = domain.Domain
    
    def __init__(self, vars: Optional[Mapping[variable.Variable, _domain_type] | Iterable[variable.Variable]] = None):
        if vars is None:
            vars = {}

        self._domains: dict[variable.Variable, self._domain_type]
        if isinstance(vars, Mapping):
            self._domains = dict(vars)
            # Restrict given domains to within variable domains
            self._domains = {var: dom & var.domain for var, dom in self._domains.items()}
        else:
            self._domains = {var: var.domain for var in vars}

    def variables(self) -> Iterator[variable.Variable]:
        yield from self._domains

    def __getitem__(self, var: variable.Variable | Iterable[variable.Variable]) -> _domain_type | type["Space"]:
        if isinstance(var, variable.Variable):
            return self._domains.get(var, var.domain)
        else:
            return self.__class__({v: self[v] for v in var})
        
    def __iter__(self):
        raise TypeError("Object not iterable")

    def __setitem__(self, var: variable.Variable, dom: _domain_type):
        self._domains[var] = var.domain & dom

    def restrict(self, var: variable.Variable, dom: _domain_type):
        """
        Same behavior as self[var] &= dom, but is more efficient
        """
        if var in self._domains:
            self._domains[var] &= dom
        else:
            self[var] = dom

    def __contains__(self, assignment: assignment.Assignment) -> bool:
        return all(var in assignment and assignment[var] in dom for var, dom in self._domains.items())

    def __and__(self, other: "Space") -> "Space":
        return self.__class__({var: self[var] & other[var] for var in set(self._domains) | set(other._domains)})

    def __or__(self, other: "Space") -> "Space":
        return self.__class__({var: self[var] | other[var] for var in set(self._domains) | set(other._domains)})
    
    @classmethod
    def empty(cls, vars: Iterable[variable.Variable]) -> "Space":
        return cls({var: domain.EMPTY_DOMAIN for var in vars})
    
    def __eq__(self, other: "Space"):
        return self._domains == other._domains
    
    @classmethod
    def from_assignment(cls, assign: assignment.Assignment) -> "Space":
        return DiscreteSpace({var: domain.SingletonDomain(assign[var]) for var in assign})


class DiscreteSpace(Space):
    _domain_type = domain.DiscreteDomain

    def __init__(self, var_to_val: Optional[Mapping[variable.Variable, _domain_type] | Iterable[variable.Variable]] = None):
        super().__init__(var_to_val)
        if not all(isinstance(var.domain, self._domain_type) for var in self._domains):
            raise ValueError("All variables must have discrete domains")
        
    def __iter__(self) -> Iterator[assignment.Assignment]:
        items = tuple(self._domains.items())
        vars, doms = zip(*items)
        for values in itertools.product(*doms):
            yield assignment.Assignment(dict(zip(vars, values)))

    def add(self, var: variable.Variable, val) -> None:
        if val not in var.domain:
            raise ValueError("Value must be within the domain with the variable")
        self._domains[var].add(val)

    @classmethod
    def empty(cls, vars: Iterable[variable.Variable]) -> "DiscreteSpace":
        return cls({var: cls._domain_type() for var in vars})
    
    def __iand__(self, other: "DiscreteSpace") -> "DiscreteSpace":
        vars = set(self._domains) | set(other._domains)
        for var in vars:
            self.restrict(var, other[var])
        return self
    
    def __ior__(self, other: "DiscreteSpace") -> "DiscreteSpace":
        vars = set(self._domains) | set(other._domains)
        for var in vars:
            self[var] |= other[var]
        return self
