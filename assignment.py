from typing import Any, Optional, Union
import variable
from collections.abc import Iterable, Mapping, Iterator


class Assignment:
    def __init__(self, var_to_val: Optional[Mapping[variable.Variable, Any]] = None):
        if var_to_val is None:
            var_to_val = {}
        self._vals: dict[variable.Variable, Any] = dict(var_to_val)

    def __iter__(self) -> Iterator[variable.Variable]:
        yield from self._vals

    def __str__(self) -> str:
        return '[' + ', '.join(f"{var}={val}" for var, val in self._vals.items()) + ']'

    def assign(self, var: variable.Variable, val) -> None:
        if val not in var.domain:
            raise ValueError("The value is not in the variable's domain")
        self._vals[var] = val

    __setitem__ = assign

    def unassign(self, var: variable.Variable) -> None:
        self._vals.pop(var, None)

    def __contains__(self, var: variable.Variable) -> bool:
        return var in self._vals
    
    def __getitem__(self, key: Union[variable.Variable, Iterable[variable.Variable]]) -> Any:
        if isinstance(key, variable.Variable):
            return self._vals[key]
        else:
            return tuple(self[var] for var in key)
        
    def __eq__(self, other: "Assignment") -> bool:
        return self._vals == other._vals
    
    def __len__(self) -> int:
        return len(self._vals)
    
    def __bool__(self) -> bool:
        return bool(self._vals)
