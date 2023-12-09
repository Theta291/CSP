from collections.abc import Iterable, Iterator
from typing import Optional
from utils import Singleton


class Domain:
    def __contains__(self, val) -> bool:
        raise NotImplementedError
    
    def __and__(self, other: "Domain") -> "Domain":
        raise NotImplementedError
    
    def __iand__(self, other: "Domain") -> None:
        raise NotImplementedError
    
    def __or__(self, other: "Domain") -> "Domain":
        raise NotImplementedError
    
    def __ior__(self, other: "Domain") -> None:
        raise NotImplementedError
    
    def __eq__(self, other: "Domain") -> bool:
        raise NotImplementedError
    
    def copy(self) -> "Domain":
        raise NotImplementedError
    
    def __bool__(self) -> bool:
        raise NotImplementedError
    
    def copy(self) -> "Domain":
        raise NotImplementedError
    

class UniverseDomain(Domain, metaclass=Singleton):
    def __contains__(self, val) -> bool:
        return True
    
    def __and__(self, other: Domain) -> Domain:
        return other
    
    __rand__ = __and__
    
    def __or__(self, other: Domain) -> Domain:
        return self
    
    __ror__ = __or__
    
    def __eq__(self, other: Domain) -> bool:
        return self is other
    
    __req__ = __eq__
    
    def copy(self) -> "Domain":
        return self
    
    def __bool__(self) -> bool:
        return True
UNIVERSE_DOMAIN = UniverseDomain()
    

class EmptyDomain(Domain, metaclass=Singleton):
    def __contains__(self, val) -> bool:
        return False
    
    def __and__(self, other: "Domain") -> "Domain":
        return self
    
    __rand__ = __and__
    
    def __or__(self, other: "Domain") -> "Domain":
        return other
    
    __ror__ = __or__
    
    def __eq__(self, other: "DiscreteDomain") -> bool:
        return self is other
    
    __req__ = __eq__
    
    def copy(self) -> "Domain":
        return self
    
    def __bool__(self) -> bool:
        return False
EMPTY_DOMAIN = EmptyDomain()


class DiscreteDomain(Domain):
    def __init__(self, elts: Optional[Iterable] = None):
        if elts is None:
            elts = set()
        self.elements = set(elts)
    
    def add(self, val) -> None:
        self.elements.add(val)

    def remove(self, val) -> None:
        self.elements.discard(val)

    def copy(self) -> "DiscreteDomain":
        return self.__class__(self.elements)

    def __contains__(self, val) -> bool:
        return val in self.elements
    
    def __and__(self, other: "Domain") -> "Domain":
        if isinstance(other, DiscreteDomain):
            return self.__class__(self.elements & other.elements)
        else:
            return NotImplemented
    
    def __iand__(self, other: "Domain") -> None:
        self.elements.intersection_update(other.elements)
        return self
    
    def __or__(self, other: "Domain") -> "Domain":
        if isinstance(other, Domain):
            return self.__class__(self.elements & other.elements)
        else:
            return NotImplemented
    
    def __ior__(self, other: "Domain") -> None:
        self.elements.update(other.elements)
        return self

    def __eq__(self, other: "DiscreteDomain") -> bool:
        if isinstance(other, DiscreteDomain):
            return self.elements == other.elements
        else:
            return NotImplemented
    
    def __bool__(self) -> bool:
        return bool(self.elements)
    
    def __iter__(self) -> Iterator:
        yield from self.elements


class SingletonDomain(Domain):
    def __init__(self, elt):
        self.element = elt

    def copy(self) -> "SingletonDomain":
        return self.__class__(self.element)

    def __contains__(self, val) -> bool:
        return val == self.element
    
    def __and__(self, other: "Domain") -> "Domain":
        if isinstance(other, SingletonDomain):
            return self.copy() if self.element == other.element else EMPTY_DOMAIN
        elif isinstance(other, DiscreteDomain):
            return other.__class__(other.elements & {self.element})
        else:
            return NotImplemented
    
    def __iand__(self, other: "DiscreteDomain") -> None:
        return NotImplemented
    
    def __or__(self, other: "DiscreteDomain") -> "DiscreteDomain":
        if isinstance(other, SingletonDomain):
            return self.copy() if self.element == other.element else DiscreteDomain({self.element, other.element})
        if isinstance(other, DiscreteDomain):
            return other.__class__(other.elements | {self.element})
        else:
            return NotImplemented
    
    def __ior__(self, other: "DiscreteDomain") -> None:
        return NotImplemented

    def __eq__(self, other: "DiscreteDomain") -> bool:
        if isinstance(other, SingletonDomain):
            return self.element == other.element
        if isinstance(other, DiscreteDomain):
            return other.elements == {self.element}
        else:
            return NotImplemented
    
    def __bool__(self) -> bool:
        return True
    
    def __iter__(self) -> Iterator:
        yield self.element
