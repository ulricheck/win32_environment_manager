pyinstaller --name=EnvMgr --icon=envmgr512.icns \
--runtime-hook rthook_pyqt5.py --clean --noconfirm --windowed \
--hidden-import="enaml.core.parse_tab.lextab" \
--hidden-import="enaml.core.compiler_helpers" \
--hidden-import="enaml.core.compiler_nodes" \
--hidden-import="enaml.core.enamldef_meta" \
--hidden-import="enaml.core.template" \
--hidden-import="enaml.widgets.api" \
--hidden-import="enaml.widgets.form" \
--hidden-import="enaml.layout.api" \
environment_manager/main.py