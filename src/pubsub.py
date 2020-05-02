class Subscriber:
    def update(self, message):
        print('{} got message "{}"'.format(self.name, message))

class Publisher:
    def __init__(self, events):
        self.events = { event : dict() for event in events }
        self.subscribers = dict()

    def get_subscribers(self, event):
        return self.events[event]

    def subscribe(self, sub, event, handler=None):
        if handler == None:
            handler = getattr(sub, 'update')
        self.get_subscribers(event)[sub] = handler

    def unsubscribe(self, event, sub):
        del self.get_subscribers(event)[sub]

    def dispatch(self, event, payload):
        for subscriber, handler in self.get_subscribers(event).items():
            handler(payload)