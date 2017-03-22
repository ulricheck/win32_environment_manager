import logging

from atom.api import Atom, Value, Typed, Dict, Event, Instance, observe
from .guilogging import Syslog
from .model import ConfigurationManager, Configuration, ChangeList


log = logging.getLogger(__name__)


class AppState(Atom):
    context = Dict()
    config = Typed(ConfigurationManager)

    active_config = Instance(Configuration)
    active_changelist = Instance(ChangeList)

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

    # @observe("active_config")
    # def _handle_config_change(self, change):
    #     print change

    def activate_configuration(self, name):
        self.deactivate_configuration()
        if name in self.config.configurations:
            log.info("Activating Configuration: %s" % name)
            self.active_config = self.config.configurations[name]
            self.active_changelist = self.active_config.get_config().get_change_list()
            self.active_changelist.execute_do_change()

            self.active_config.is_active = True

    def deactivate_configuration(self):
        if self.active_config is not None:
            cfg = self.active_config
            log.info("Deactivating Configuration: %s" % cfg.name)

            if self.active_changelist is not None:
                self.active_changelist.execute_undo_change()
            self.active_changelist = None

            cfg.is_active = False

