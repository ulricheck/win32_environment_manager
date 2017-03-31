Environment Variable Manager
=============================

This tool manages configuration profiles for Win32 Environment Variables. 
It is mainly targeted to shared developer workstation users, who need to change their working environment on a regular bases.
Based on a configuration file (see demo_environment.ini), a user describes sections and configurations.

A section is a set of changes that need to be made to support a single application or library. 
A change request can be any of:
- Add a new Environment Variable (add_keys)
- Remove an existing Environment Variable (remove_keys)
- Prepend an item to the PATH Variable (prepend_path)
- Append an item to the PATH Variable (append_path)

A configuration is an ordered composition of sections. 
For example if one has a section to support python and a section to support an application with python bindings, then
a configuration for this application would consist of the python and the application section (see h3d_minimal in demo-config)

Configurations are installed using the win32 api and are persistent. 
Whenever a profile is changed, the current active changes are undone before a new profile is installed.
The application prevents from being launched multiple times and stores a recovery file to undo changes at the next launch if it happens to exit without cleaning up.


Installation:
- pip install -f requirements.txt
- python setup.py install

Usage:
- envmgr -C path/to/config_file.ini


Notes to self for further development:
- PyQT5 SystemTray: https://github.com/baoboa/pyqt5/blob/master/examples/desktop/systray/systray.py
- Launching Apps from Services: https://blogs.msdn.microsoft.com/winsdk/2009/07/14/launching-an-interactive-process-from-windows-service-in-windows-vista-and-later/