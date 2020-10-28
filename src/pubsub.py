import asyncio
import functools
import log

class MessageQueue:
    MAXQUEUESIZE = 20
    instance = None
    asyncOff = False
    
    def getInstance(asyncOff=False):
        if MessageQueue.instance == None: 
            MessageQueue.instance = MessageQueue.__MessageQueue__(MessageQueue.MAXQUEUESIZE)
            MessageQueue.asyncOff = asyncOff
        return MessageQueue.instance
    
    def reset(asyncOff=False):
        mq = MessageQueue.getInstance(asyncOff)
        if mq:
            mq.reset()
        

    def handleMessages():
        mq = MessageQueue.getInstance()
        while mq and True:
            mq.handleNextMessage()
            if not mq.hasMessages(): break

    def addMessages(messages):
        mq = MessageQueue.getInstance()
        if mq and messages:
            for msg in messages:
                mq.pushMsg(msg)
                
    def processMessages(messages):
        if MessageQueue.asyncOff:
            MessageQueue.addMessages(messages)
            MessageQueue.handleMessages()
        else:
            loop = asyncio.get_running_loop()

            try:
                callback = functools.partial(MessageQueue.addMessages, messages)
                loop.call_soon_threadsafe(callback)
            finally:
                pass

            try:
                callback = MessageQueue.handleMessages
                loop.call_soon_threadsafe(callback)
            finally:
                pass
            
    class __MessageQueue__:
        def __init__(self, maxQueueSize):
            self.queue = []
            
        def reset(self):
            self.queue = []
            
        def pushMsg(self, msg):
            self.queue.append(msg)
            
        def hasMessages(self):
            return (len(self.queue)>0)
        
        def handleNextMessage(self):
            if self.hasMessages():
                msg = self.queue.pop(0)
                if msg:
                    handler = msg[0]
                    payload = msg[1]
                    handler(payload)
                        
    def __init__(self):
        pass

    def process(self, messages):
        MessageQueue.processMessages(messages)
                   
        
class Subscriber:
    def update(self, message):
        print('{} got message "{}"'.format(self.name, message))

class Publisher:
    def __init__(self, events):
        self.mq = MessageQueue()
        self.events = { event : dict() for event in events }

    def get_subscribers(self, event):
        return self.events[event]

    def subscribe(self, sub, event, handler=None):
        if handler == None:
            handler = getattr(sub, 'update')
        if not sub in self.get_subscribers(event):
            self.get_subscribers(event)[sub] = handler

    def unsubscribe(self, event, sub):
        if event in self.events and sub in self.events[event]:
            del self.events[event][sub]

    def dispatch(self, event, payload):
        if payload:
            payload.update({"event": event})
        else:
            payload = {"event": event}

        messages = list()
        for subscriber, handler in self.get_subscribers(event).items():
            messages.append((handler, payload))

        if len(messages)>0:
            self.mq.process(messages)
