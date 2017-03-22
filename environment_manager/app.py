import logging

from atom.api import Atom, Value, Typed, Dict, Event
from .guilogging import Syslog

log = logging.getLogger(__name__)


class AppState(Atom):
    context = Dict()

    args = Value()
    options = Value()

    syslog = Typed(Syslog)

    app_started = Event()
    app_stopped = Event()

