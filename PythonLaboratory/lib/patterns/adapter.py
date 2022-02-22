import string
from typing import Callable, TypeVar
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

if __name__ == '__main__':
    s=None
    s2=Adapter(s, test=lambda: print('test passed') )
    s2.test()


