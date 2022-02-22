
from abc import ABC, abstractmethod

class DisplayAPI(ABC):
    @abstractmethod
    def display(self):
        pass
    
class Print(DisplayAPI):
    def display(self, some_shit):
        print(some_shit.data)
    
class Display(DisplayAPI):
    def display(self, some_shit):
        display(some_shit.data)
    