from abc import ABC,abstractmethod

class AbstractConsole(ABC):
    @abstractmethod
    def print(self, *args):
        pass

class TerminalConsole(AbstractConsole):
    def __init__(self):
        pass

    def print(self, *args):
        for a in args:
            print(a, end=' ')
        print ("")



if __name__ == "__main__":
    tc = TerminalConsole()
    tc.print("this", "prints", 1, 2, 3, "to the terminal")