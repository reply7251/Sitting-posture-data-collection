

class Observable:
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.observers: list[Observer] = []

    def send(self, data):
        for observer in self.observers:
            observer.update(data)
    
    def add_observer(self, observer):
        self.observers.append(observer)

class Observer:
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
    
    def update(self, data):
        pass