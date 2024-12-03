from abc import ABC, abstractmethod


# Abstract Subject Class
class Subject:
    def __init__(self):
        self._observers = []
    
    def add_observer(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)
    
    def remove_observer(self, observer):
        if observer in self._observers:
            self._observers.remove(observer)
    
    def notify_observers(self, **kwargs):
        for observer in self._observers:
            observer.update(**kwargs)


# Abstract Observer Class
class Observer(ABC):
    @abstractmethod
    def update(self, **kwargs):
        pass


# TIN Observer
class TINObserver(Observer):
    def __init__(self):
        self.notifications = []

    def update(self, **kwargs):
        if 'TIN' in kwargs:
            new_TIN = kwargs['TIN']
            name = kwargs['name']
            id = kwargs['id']
            message = f"TIN was changed for {name} {id}: {new_TIN}"
            self.notifications.append(message)
            print(f"{self.notifications}")

class AdvisoryObserver(Observer):
    def __init__(self):
        self.notifications = []

    def update(self, **kwargs):
        if 'product' in kwargs and kwargs['product'] == 'Advisory':
            self.notifications = []
            name = kwargs['name']
            id = kwargs['id']
            message = f"{name} {id} needs an advisory appointment."
            self.notifications.append(message)
            print(f"{self.notifications}")