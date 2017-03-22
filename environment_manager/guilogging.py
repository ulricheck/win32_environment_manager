import logging
from atom.api import Atom, Typed, List, Event, observe


class ConsoleWindowLogHandler(logging.Handler):

    def __init__(self, parent):
        super(ConsoleWindowLogHandler, self).__init__()
        self.parent = parent

    def emit(self, logRecord):
        message = str(logRecord.getMessage())
        self.parent.logevent(message)

class Syslog(Atom):

    logitems = List()
    logevent = Event()

    handler = Typed(ConsoleWindowLogHandler)

    def _default_handler(self):
        return ConsoleWindowLogHandler(self)

    @observe("logevent")
    def _handle_logevent(self, change):
        self.logitems.append(change["value"])
