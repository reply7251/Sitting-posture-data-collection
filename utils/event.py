

from typing import Callable
from functools import partial
from inspect import signature

from PyQt5.QtCore import pyqtSignal, pyqtBoundSignal

__all__ = (
    'Event',
    'EventHandler',
    'listen',
    'Listener',
    'SerialReceiveEvent',
    'ExitEvent',
    'SerialStringReceiveEvent'
    'SerialNumericReceiveEvent'
)

class Event:
    def __init_subclass__(cls) -> None:
        super().__init_subclass__()

    def __init__(self) -> None:
        self.cancel = False
    
    def set_cancel(self, cancel):
        self.cancel = cancel
    
    def fire(self):
        for event_type in type(self).mro():
            for handlers in EventHandler.event_handlers.get(event_type, []):
                for handler in handlers:
                    handler(self)
                    if self.cancel:
                        break

class EventHandler:
    event_handlers: dict[Event, list[list['EventHandler']]] = {}

    def __init__(self, callback: Callable[[Event], None], event_type: type=None, priority: int=5, add=True) -> None:
        if not event_type and len(callback.__annotations__.values()) == 1:
            event_type = list(callback.__annotations__.values())[0]
        
        if not event_type or not issubclass(event_type, Event):
            event_type = Event
        
        if add:
            EventHandler.event_handlers.setdefault(event_type, [[] for _ in range(9)])[priority].append(self)

        self.event_type = event_type
        
        self.callback = callback

        self.priority = priority
        
    def __call__(self, event) -> bool:
        return self.callback(event)
    
    def removed(self):
        EventHandler.event_handlers[self.event_type][self.priority].remove(self)

class Listener:
    def __init_subclass__(cls, threaded=False) -> None:
        if threaded:
            cls._on_event = pyqtSignal(Event)
        else:
            cls._on_event = None

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        if self._on_event:
            self._with_thread()
        else:
            for key in self.__class__.__dict__.keys():
                member = getattr(self, key)
                if isinstance(member, EventHandler):
                    sign = signature(member.callback)
                    if len(sign.parameters) > 1:
                        member.callback = partial(member.callback, self)
                    continue

                if not callable(member):
                    continue

                callback: Callable = member
                
                if len(callback.__annotations__.values()) == 0:
                    continue

                event_type = list(callback.__annotations__.values())[0]
            
                if not event_type or not issubclass(event_type, Event):
                    continue

                EventHandler(partial(callback, self))
    
    def _with_thread(self):
        self.handlers: dict[Event, list[list[EventHandler]]] = {}
        self._on_event.connect(self._redirected)

        def on_event(event):
            self._on_event.emit(event)
        
        event_handler = listen()(on_event)
        
        @listen()
        def on_exit(event: ExitEvent):
            event_handler.removed()
            self.handlers.clear()

        for key in self.__class__.__dict__.keys():
            member = getattr(self, key)
            if isinstance(member, EventHandler):
                sign = signature(member.callback)
                if len(sign.parameters) > 1:
                    member.callback = partial(member.callback, self)
                member.removed()
                self.handlers.setdefault(member.event_type, [[] for _ in range(9)])[member.priority].append(member)
                continue

            if not callable(member) or isinstance(member, pyqtBoundSignal):
                continue

            callback: Callable = member
            
            if len(callback.__annotations__.values()) == 0:
                continue

            event_type = list(callback.__annotations__.values())[0]
        
            if not event_type or not issubclass(event_type, Event):
                continue

            handler = EventHandler(partial(callback, self), add=False)
            self.handlers.setdefault(event_type, [])[handler.priority].append(handler)
    
    def _redirected(self, event: Event):
        for event_type in event.__class__.mro():
            for handlers in self.handlers.get(event_type, []):
                for handler in handlers:
                    handler(event)


def listen(event: Event = None, priority: int = 5):
    def wrapper(method: Callable):
        return EventHandler(method, event, priority)
    return wrapper

class SerialReceiveEvent(Event):
    pass

class SerialNumericReceiveEvent(SerialReceiveEvent):
    def __init__(self, data: list[float]) -> None:
        super().__init__()
        self.data = data

class SerialStringReceiveEvent(SerialReceiveEvent):
    def __init__(self, data: str) -> None:
        super().__init__()
        self.data = data

class ExitEvent(Event):
    pass