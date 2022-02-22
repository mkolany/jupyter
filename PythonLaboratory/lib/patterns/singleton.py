from abc import ABCMeta

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

if __name__ == '__main__':
    # Singleton class testing
    class Test(metaclass=Singleton):
        foo=3
    class Test2(metaclass=Singleton):
        foo=2

    s=Test()
    t=Test()
    u=Test2()
    
    if(id(s)==id(t) and id(s)!=id(u)):
        print('test passed')