class Point:
    """ a point on elliptic curve: y^2 = x^3 + ax + b """
    
    def __init__(self, x, y, a, b) -> None:
        self.x = x
        self.y = y
        self.a = a
        self.b = b
        
        if self.y ** 2 != self.x ** 3 + a * x + b:
            raise ValueError(f"({x} {y}) is not on the curve.")

    def __eq__(self, __o: object) -> bool:
        return self.x == __o.x and self.y == __o.y \
               and self.a == __o.a and self.b == __o.b

    def __add__(self, other):
        if not (self == other):
            raise ValueError(f"Point {self} and {other} are not on the same curve")
        
        if self.x is None:  # self is infinity
            return other
        if other.x is None:  # other is infinity
            return self

               
if __name__ == "__main__":
    
    p1 = Point(-1, -1, 5, 7)