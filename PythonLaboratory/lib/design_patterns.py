
from abc import ABC, ABCMeta, abstractmethod
from typing import Callable, TypeVar, Optional, Any,  Type
T = TypeVar("T")

class Adapter:
    """
    Adapts an object by replacing methods.
    
    Usage:
        Adapter(adaptee desired_method=adaptee.method)
    """
    def __init__(self, obj: T, **adapted_methods: Callable):
        # Setting the adapted methods in the object's dict.
        self.obj = obj
        self.__dict__.update(adapted_methods)

    def __getattr__(self, attr):
        """All non-adapted calls are passed to the object."""
        return getattr(self.obj, attr)

    def original_dict(self):
        return self.obj.__dict__

class Singleton(ABCMeta):
    """
    Class of that type can be initialized only once. 
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls.__name__ not in cls._instances:
            cls._instances[cls.__name__] = super().__call__(*args, **kwargs)
        return cls._instances[cls.__name__]

    @staticmethod
    def instances():
        return Singleton._instances

    @staticmethod
    def list_instances():
        return [*Singleton._instances.values()]



# unit tests:
if __name__ == '__main__':
    # Singleton class testing
    class Test(metaclass=Singleton):
        foo=3
    class Test2(metaclass=Singleton):
        foo=2

    s=Test()
    t=Test()
    u=Test2()
    
    assert(id(s)==id(t) and id(s)!=id(u))


    # Adapter class testing
    s2=Adapter(s, shit=s.__class__.instances)
    print(type(s2), type(s))
    print(s2.shit())
    


