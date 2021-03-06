import os, sys
import ConfigParser
from optparse import OptionParser
import logging
import warnings
import enaml
from enaml.qt.qt_application import QtApplication

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
logging.captureWarnings(True)

import logging.config
from environment_manager.app import AppState
from environment_manager.guilogging import Syslog
from environment_manager.model import parse_config
from environment_manager.singletoninstance import SingleInstance, SingleInstanceException

def main():

    parser = OptionParser()

    parser.add_option("--py-logconfig",
                  action="store", dest="py_logconfig", default="",
                  help="python logging config file")

    # XXX care about windows default paths here
    parser.add_option("-C", "--configfile",
                  action="append", dest="configfile", default=["~/environment.conf", ],
                  help="Interactive console config file")

    syslog = Syslog()
    appstate = AppState(context=dict(),
                        syslog=syslog)

    (options, args) = parser.parse_args()

    if options.py_logconfig != "" and os.path.isfile(options.py_logconfig):
        log.info("Reloading logging config from: %s" % options.py_logconfig)
        logging.config.fileConfig(options.py_logconfig, disable_existing_loggers=False)
        log.info("Done reloading config.")

    # # activate gui logging
    # logger = logging.getLogger()
    # # add verbose flag ..
    # logger.setLevel(logging.DEBUG)
    # logger.addHandler(syslog.handler)

    appstate.args = args
    appstate.options = options

    appstate.context['args'] = args
    appstate.context['options'] = options


    # XXX care about windows default paths here
    cfgfiles = []
    for cfgname in os.environ.get("ENVIRONMENT_CONFIG_FILE", "~/environment.conf").split(os.pathsep):
        if os.path.isfile(cfgname):
            cfgfiles.append(cfgname)

    for cfgfname in options.configfile:
        if os.path.isfile(cfgfname):
            cfgfiles.append(cfgfname)
        else:
            log.warn("Skipping non-existant config file: %s" % cfgfname)

    config = ConfigParser.ConfigParser()
    config.optionxform = str
    try:
        log.info("Loading config files: %s" % (",".join(cfgfiles)))
        config.read(cfgfiles)
        appstate.config = parse_config(config)
    except Exception, e:
        log.error("Error parsing config file(s): %s" % (cfgfiles,))
        log.exception(e)

    # check that only one instance is running
    try:
        singleton_process = SingleInstance("environment_manager")
    except SingleInstanceException:
        log.error("Another Process is already running.")
        sys.exit(1)

    with enaml.imports():
        from main_view import Main

    app = QtApplication()

    view = Main(appstate=appstate)
    view.show()

    # notify application start
    appstate.app_starting()

    # Start the application event loop
    app.start()

    # free singleton
    del singleton_process

if __name__ == '__main__':
    main()