class T:
    def __init__(self, x):
        self.x = x

    def __add__(self, other):
        print("T add")
        return self.__class__(self.x + other.x)
    
    def __iadd__(self, other):
        print("T iadd")
        self.x += other.x
        return self
    
class U(T):
    def __add__(self, other):
        print("U add")
        return T(0)

    def __iadd__(self, other):
        print("U iadd")
        return NotImplemented


if __name__ == '__main__':
    t = U(1)
    t += U(2)
    print(t.x)
    print(type(t))
