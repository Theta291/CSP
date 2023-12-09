from typing import Optional
import domain


class Variable:
    _names: set[str] = set()
    _unnamed: int = 0

    def __init__(self, domain: domain.Domain, name: Optional[str]=None):
        # I specifically use "Variable" instead of "self" so no variables can have the same name
        # even if they come from different subclasses
        if name is None:
            name = "x" + str(self._unnamed)
            Variable._unnamed += 1
        if name in Variable._names:
            raise ValueError("The variable name is already taken.")

        self._name: str = name
        self._names.add(name)

        self._domain: domain.Domain = domain

    @property
    def name(self) -> str:
        return self.name

    @property
    def domain(self) -> domain.Domain:
        return self._domain
    
    def __str__(self) -> str:
        return self._name
    
    def __eq__(self, other: "Variable") -> bool:
        return self._name == other._name
    
    def __hash__(self) -> int:
        return hash(self._name)
