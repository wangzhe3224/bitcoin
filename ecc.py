from __future__ import annotations
from random import randint
from cmath import exp
from operator import add, sub, mul, truediv, invert
from unittest import TestCase, runner
from unittest import TestSuite, TextTestRunner
import hashlib
import hmac


def hash256(s):
    return hashlib.sha256(hashlib.sha256(s).digest()).digest()


class FieldElementZ:
    
    def __init__(self, num: int, prime: int=19) -> None:
        if num > prime or num < 0:
            error = f"Num {num} not in field range 0 to {prime}"
            raise ValueError(error)
        self.num = num
        self.prime = prime

    @classmethod
    def make(cls, num, prime) -> FieldElement:
        return cls(num, prime)

    def _two_operate(self, other, operator):
        num = operator(self.num, other.num) % self.prime
        return self.make(num, self.prime)

    def _exception_type_error(self, other):
        if self.prime != other.prime:
            raise TypeError(f"不可以对两个不同有限域的元素运算")
        
    def __repr__(self):
        return f"FieldElement_{self.prime}{self.num}"
    
    def __eq__(self, other: FieldElement):
        if other is None:
            return False
        return self.num == other.num and self.prime == other.prime
    
    def __ne__(self, __o: object) -> bool:
        return not self == __o

    def __neg__(self) -> FieldElement:
        return self.make(-(self.num) % self.prime, self.prime)

    def __add__(self, other):
        self._exception_type_error(other)
        return self._two_operate(other, add)

    def __sub__(self, other):
        self._exception_type_error(other)
        return self._two_operate(other, sub)

    def __mul__(self, other):
        self._exception_type_error(other)
        return self._two_operate(other, mul)

    def __truediv__(self, other):
        self._exception_type_error(other)
        return self._two_operate(other, mul)

    def __pow__(self, exponent):
        """
        a^p–1 = 1
        a^–3 = a^–3 ⋅ a^{p–1} = a^{p–4}
        """
        n = exponent
        while n < 0:
            n += self.prime - 1
        num = pow(self.num, n, self.prime)
        return self.make(num, self.prime)

    def __rmul__(self, coefficient):
        num = (self.num * coefficient) % self.prime
        return self.__class__(num=num, prime=self.prime)

class FieldElement:

    def __init__(self, num, prime):
        if num >= prime or num < 0:
            error = 'Num {} not in field range 0 to {}'.format(
                num, prime - 1)
            raise ValueError(error)
        self.num = num
        self.prime = prime

    def __repr__(self):
        return 'FieldElement_{}({})'.format(self.prime, self.num)

    def __eq__(self, other):
        if other is None:
            return False
        return self.num == other.num and self.prime == other.prime

    def __ne__(self, other):
        # this should be the inverse of the == operator
        return not (self == other)

    def __add__(self, other):
        if self.prime != other.prime:
            raise TypeError('Cannot add two numbers in different Fields')
        # self.num and other.num are the actual values
        # self.prime is what we need to mod against
        num = (self.num + other.num) % self.prime
        # We return an element of the same class
        return self.__class__(num, self.prime)

    def __sub__(self, other):
        if self.prime != other.prime:
            raise TypeError('Cannot subtract two numbers in different Fields')
        # self.num and other.num are the actual values
        # self.prime is what we need to mod against
        num = (self.num - other.num) % self.prime
        # We return an element of the same class
        return self.__class__(num, self.prime)

    def __mul__(self, other):
        if self.prime != other.prime:
            raise TypeError('Cannot multiply two numbers in different Fields')
        # self.num and other.num are the actual values
        # self.prime is what we need to mod against
        num = (self.num * other.num) % self.prime
        # We return an element of the same class
        return self.__class__(num, self.prime)

    def __pow__(self, exponent):
        n = exponent % (self.prime - 1)
        num = pow(self.num, n, self.prime)
        return self.__class__(num, self.prime)

    def __truediv__(self, other):
        if self.prime != other.prime:
            raise TypeError('Cannot divide two numbers in different Fields')
        # self.num and other.num are the actual values
        # self.prime is what we need to mod against
        # use fermat's little theorem:
        # self.num**(p-1) % p == 1
        # this means:
        # 1/n == pow(n, p-2, p)
        num = (self.num * pow(other.num, self.prime - 2, self.prime)) % self.prime
        # We return an element of the same class
        return self.__class__(num, self.prime)

    def __rmul__(self, coefficient):
        num = (self.num * coefficient) % self.prime
        return self.__class__(num=num, prime=self.prime)

class Point:
    """ a point on elliptic curve: y^2 = x^3 + ax + b """
    
    def __init__(self, x, y, a, b) -> None:
        self.x = x
        self.y = y
        self.a = a
        self.b = b

        if self.x is None and self.y is None:
            return 
        
        if self.y ** 2 != self.x ** 3 + a * x + b:
            raise ValueError(f"({x} {y}) is not on the curve.")
    
    def __repr__(self):
        if self.x is None:
            return 'Point(infinity)'
        elif isinstance(self.x, FieldElement):
            return 'Point({},{})_{}_{} FieldElement({})'.format(
                self.x.num, self.y.num, self.a.num, self.b.num, self.x.prime)
        else:
            return 'Point({},{})_{}_{}'.format(self.x, self.y, self.a, self.b)
    
    def make_point(self, x, y):
        return self.__class__(x, y, self.a, self.b)

    def __eq__(self, __o: object) -> bool:
        return self.x == __o.x and self.y == __o.y \
               and self.a == __o.a and self.b == __o.b

    def __add__(self, other):
        if self.a != other.a or self.b != other.b:
            raise ValueError(f"Point {self} and {other} are not on the same curve")
        
        if self.x is None:  # self is infinity
            return other
        if other.x is None:  # other is infinity
            return self

        # infinit: I
        if self.x == other.x and self.y != other.y:
            return self.make_point(None, None)

        if self.x != other.x:
            s = (other.y - self.y) / (other.x - self.x)  # 斜率
            x = s**2 - self.x - other.x
            y = s * (self.x - x) - self.y 
            return self.make_point(x, y)

        if self == other and self.y == 0 * self.x:
            return self.make_point(None, None)
        
        if self == other:
            s = (3 * self.x**2 + self.a) / (2 * self.y)
            x = s**2 - 2 * self.x
            y = s * (self.x - x) - self.y
            return self.make_point(x, y)
    
    def __rmul__(self, coefficient):
        coef = coefficient
        current = self  # <1>
        result = self.__class__(None, None, self.a, self.b)  # <2>
        while coef:
            if coef & 1:  # <3>
                result += current
            current += current  # <4>
            coef >>= 1  # <5>
        return result

def reverse_scalar_mul():
    prime = 223
    a = FieldElement(0, prime)
    b = FieldElement(7, prime)
    x = FieldElement(47, prime)
    y = FieldElement(71, prime)
    p = Point(x, y, a, b)
    
    print(p)
    for s in range(1, 21):
        res = s*p
        print('{}*(47,71)=({},{})'.format(s,res.x.num,res.y.num))

def ex5():
    """ 给出一个在 $F_223$ 的曲线： $y^2 = x^3 + 7$，找到组 $(15, 86)$ 的序（Order）？ """
    prime = 223
    a = FieldElement(0, prime)
    b = FieldElement(7, prime)
    x = FieldElement(15, prime)
    y = FieldElement(86, prime)
    p = Point(x, y, a, b)
    inf = Point(None, None, a, b)
    product = p
    count = 1
    while product != inf:
        product += p
        count += 1
        
    print(count)

def verify_bitcoin_curve():
    gx = 0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798
    gy = 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8 
    p = 2**256-2**32-977
    n = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141 
    x = FieldElement(gx, p)
    y = FieldElement(gy, p)
    seven = FieldElement(7, p)
    zero = FieldElement(0, p)
    G = Point(x, y, zero, seven)
    print(n * G)


class ECCTest(TestCase):
    
    def test_on_curve(self):
        prime = 223
        a = FieldElement(0, prime)
        b = FieldElement(7, prime)
        valid_points = ((192, 105), (17, 56), (1, 193)) 
        invalid_points = ((200, 119), (42, 99))
        for x_raw, y_raw in valid_points:
            x = FieldElement(x_raw, prime)
            y = FieldElement(y_raw, prime)
            Point(x, y, a, b)
        
        for x_raw, y_raw in invalid_points:
            x = FieldElement(x_raw, prime)
            y = FieldElement(y_raw, prime) 
            with self.assertRaises(ValueError):
                Point(x, y, a, b)
            
A = 0
B = 7
N = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141

class S256Field(FieldElement):
    P = 2**256-2**32-977 

    def __init__(self, num, prime=None):
        super().__init__(num, self.P)

    def __repr__(self):
        return '{:x}'.format(self.num).zfill(64)


class S256Point(Point):
    A = 0
    B = 7
    N = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141
    
    def __init__(self, x, y, a=None, b=None) -> None:
        a, b = S256Field(self.A), S256Field(self.B)
        if isinstance(x, int):
            super().__init__(S256Field(x), S256Field(y), a, b)
        else:
            super().__init__(x, y, a, b)

    def __rmul__(self, coefficient):
        coef = coefficient % self.N
        return super().__rmul__(coef)

    def verify(self, z, sig) -> bool:
        s_inv = pow(sig.s, self.N - 2, N)
        u = z * s_inv % self.N
        v = sig.r * s_inv % self.N 
        total = u * BITCOIN_G + v * self
        return total.x.num == sig.r


class Signature:
    
    def __init__(self, r, s) -> None:
        self.r = r
        self.s = s 
        
    def __repr__(self) -> str:
        return f"Signature({self.r},{self.s})"

BITCOIN_G = S256Point( 
    x=0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798,
    y=0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8,
)
               
class PrivateKey:
    
    def __init__(self, secret) -> None:
        self.secret = secret 
        self.point = secret * BITCOIN_G

    def hex(self):
        return '{:x}'.format(self.secret).zfill(64)

    def sign(self, z):
        # z is a hashed message
        # k = randint(0, N)
        k = self.deterministic_k(z)  # <1>
        r = (k*BITCOIN_G).x.num
        k_inv = pow(k, N-2, N)
        s = (z + r*self.secret) * k_inv % N
        # It turns out that using the low-s value will get nodes to relay our transactions. This is for malleability reasons.
        if s>N/2:
            s=N-s
        return Signature(r, s)

    def deterministic_k(self, z):
        k = b'\x00' * 32
        v = b'\x01' * 32
        if z > N:
            z -= N
        z_bytes = z.to_bytes(32, 'big')
        secret_bytes = self.secret.to_bytes(32, 'big')
        s256 = hashlib.sha256
        k = hmac.new(k, v + b'\x00' + secret_bytes + z_bytes, s256).digest()
        v = hmac.new(k, v, s256).digest()
        k = hmac.new(k, v + b'\x01' + secret_bytes + z_bytes, s256).digest()
        v = hmac.new(k, v, s256).digest()
        while True:
            v = hmac.new(k, v, s256).digest()
            candidate = int.from_bytes(v, 'big')
            if candidate >= 1 and candidate < N:
                return candidate  # <2>
            k = hmac.new(k, v + b'\x00', s256).digest()
            v = hmac.new(k, v, s256).digest()

class PrivateKeyTest(TestCase):

    def test_sign(self):
        pk = PrivateKey(randint(0, N))
        z = randint(0, 2**256)
        sig = pk.sign(z)
        self.assertTrue(pk.point.verify(z, sig))


def ex7_sign():
    e = 12345
    z = int.from_bytes(hash256(b"Programming Bitcoin"), "big")
    k = 1234567890
    r = (k * BITCOIN_G).x.num
    k_inv = pow(k, N-2, N)
    s = (z+r*e) * k_inv % N
    print(e * BITCOIN_G)
    print()
    print(hex(z))
    print(hex(r))
    print(hex(s))

if __name__ == "__main__":
    
    # p1 = Point(-1, -1, 5, 7)
    # I = Point(None, None, 5, 7)
    # assert p1 + I == p1
    # print(I)

    # # 一些测试
    # assert FieldElement(9, 19) + FieldElement(10, 19) == FieldElement(0, 19)
    # assert FieldElement(9, 19) - FieldElement(9, 19) == FieldElement(0, 19)
    # assert FieldElement(11, 19) - FieldElement(9, 19) == FieldElement(2, 19)
    # assert FieldElement(11, 19) * FieldElement(9, 19) == FieldElement(4, 19)
    # assert FieldElement(7, 13) ** (-3) == FieldElement(8, 13)

    # a = FieldElement(num=0, prime=223) 
    # b = FieldElement(num=7, prime=223) 
    # x = FieldElement(num=192, prime=223)
    # y = FieldElement(num=105, prime=223) 
    # p1 = Point(x, y, a, b)
    # print(p1)

    suite = TestSuite()
    # suite.addTest(ECCTest("test_on_curve"))
    # TextTestRunner().run(suite)

    reverse_scalar_mul()
    ex5()
    verify_bitcoin_curve()

    pk = PrivateKey(12345)
    print(pk.hex())

    ex7_sign()

    suite.addTest(PrivateKeyTest("test_sign"))
    TextTestRunner().run(suite)