from abc import ABCMeta, abstractmethod


class MyAbc(metaclass=ABCMeta):
    @abstractmethod
    def init(self):
        pass


class A(MyAbc):
    def init(self):
        print('a init')
    

abc = A()
abc.init()