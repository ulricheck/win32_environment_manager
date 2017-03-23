import logging

from atom.api import Atom, Value, Typed, Dict, Event, Instance, Bool, Unicode, observe
from enaml.qt import QtCore
from enaml.application import deferred_call

from .guilogging import Syslog
from .model import ConfigurationManager, Configuration, ChangeList


log = logging.getLogger(__name__)


class BackgroundThread(QtCore.QThread):
    def __init__(self, processor, fname, *args):
        log.debug("Init Background Thread: %s" % fname)
        super(BackgroundThread, self).__init__()
        self.processor = processor
        self.fname = fname
        self.args = args

    def run(self):
        log.debug("BackgroundThread.run()")
        deferred_call(self.set_status, "bgThread_running", True)
        try:
            getattr(self.processor, self.fname)(*self.args)
        except Exception, e:
            log.error("Error in BackgroundThread:")
            log.exception(e)
        finally:
            deferred_call(self.set_status, "bgThread_running", False)
        log.debug("BackgroundThread Finished")

    def set_status(self, k, v):
        if hasattr(self.processor, k):
            setattr(self.processor, k, v)



class AppState(Atom):
    context = Dict()
    config = Typed(ConfigurationManager)

    active_config = Instance(Configuration)
    active_changelist = Instance(ChangeList)

    job_active = Bool(False)
    job_status = Unicode()

    bgThread = Typed(BackgroundThread)
    bgThread_running = Bool(False)

    args = Value()
    options = Value()

    syslog = Typed(Syslog)

    app_starting = Event()
    app_stopping = Event()

    @observe("app_starting")
    def _handle_setup(self, change):
        log.info("Setup Environment Manager")
        for key, cfg in self.config.configurations.items():
            if cfg.is_default:
                log.info("Found default configuration: %s" % key)
                self.activate_configuration(key)
                break

    @observe("app_stopping")
    def _handle_teardown(self, change):
        log.info("Teardown Environment Manager")
        self.deactivate_configuration()

    def activate_configuration(self, name):
        if name in self.config.configurations:
            self.bgThread = BackgroundThread(self, "_activate_configuration", name)
            self.bgThread.start()
        else:
            log.error("Invalid configuration - cannot activate")

    def _activate_configuration(self, name):
        self._deactivate_configuration()
        if name in self.config.configurations:
            log.info("Activating Configuration: %s" % name)
            deferred_call(setattr, self, "job_status", "Activating Configuration: %s" % name)

            active_config = self.config.configurations[name]

            changelist = active_config.get_config().get_change_list()
            changelist.execute_do_change()

            deferred_call(setattr, self, "active_changelist", changelist)
            deferred_call(setattr, self, "active_config", active_config)
            deferred_call(setattr, active_config, "is_active", True)

            deferred_call(setattr, self, "job_status", "")

    def deactivate_configuration(self):
        if self.active_config is not None:
            self.bgThread = BackgroundThread(self, "_deactivate_configuration")
            self.bgThread.start()

    def _deactivate_configuration(self):
        if self.active_config is not None:
            cfg = self.active_config
            log.info("Deactivating Configuration: %s" % cfg.name)
            deferred_call(setattr, self, "job_status", "Deactivating Configuration: %s" % cfg.name)

            if self.active_changelist is not None:
                changelist = self.active_changelist
                changelist.execute_undo_change()

            deferred_call(setattr, self, "active_changelist", None)

            deferred_call(setattr, cfg, "is_active", False)
            deferred_call(setattr, self, "active_config", None)

            deferred_call(setattr, self, "job_status", "")
