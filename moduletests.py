from DesignPatterns.Singleton import SingletonMeta
class MemoryBank(metaclass=SingletonMeta):
    def __init__(self, name=None):
        if name is not None:
            self.name = name
    def some_business_logic(self):
        pass
    def set(self, attr, value):   
        setattr(self, attr, value)


if __name__ == "__main__":
    # The client code.
    s1 = MemoryBank('krowa')
    