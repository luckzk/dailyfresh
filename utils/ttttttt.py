class A:
    def fun(self):
        pass


class B:
    def fun(self):
        pass


class C(A, B):
    def fun(self):
        pass

print(C.__mro__)
