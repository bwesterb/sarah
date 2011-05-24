class Event(object):
        def __init__(self):
                self.handlers = []
        def register(self, handler):
                self.handlers.append(handler)
        def __call__(self, *args, **kwargs):
                for handler in self.handlers:
                        handler(*args, **kwargs)
