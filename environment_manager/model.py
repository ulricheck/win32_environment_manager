import os, sys
from atom.api import Atom, Value, List, Dict, Str, Bool, Int, Float, Enum, Typed, Coerced, Unicode
if sys.platform.startswith('win'):
    from environment_manager import win32env as env
else:
    from environment_manager import mockenv as env

import logging
log = logging.getLogger(__name__)


class EnvironmentValue(Atom):
    value = Unicode()

    def __repr__(self):
        return u"Value<%s>" % self.value


class EnvironmentKey(Atom):
    is_default = Bool(False)
    is_existing = Bool(False)
    is_active = Bool(False)

    key = Str()
    values = List(EnvironmentValue)

    def get_value_as_string(self):
        return os.pathsep.join([v.value for v in self.values])


    def __repr__(self):
        return u"Key<%s>:%s" % (self.key, self.values)


class Environment(Atom):
    type = Enum('SYSTEM', 'USER')
    keys = List(EnvironmentKey)


class ConfigurationSection(Atom):
    name = Str()
    add_keys = List(EnvironmentKey)
    remove_keys = List(EnvironmentKey)
    prepend_path = List(EnvironmentValue)
    append_path = List(EnvironmentValue)


class Configuration(Atom):
    name = Str()
    is_active = Bool(False)
    is_default = Bool(False)
    order = Int()
    description = Unicode()
    sections = List(ConfigurationSection)

    def get_config(self):
        add_keys = []
        remove_keys = []
        prepend_path = []
        append_path = []
        for section in self.sections:
            add_keys.extend(section.add_keys)
            remove_keys.extend(section.remove_keys)
            prepend_path.extend(section.prepend_path)
            append_path.extend(section.append_path)
        return CompositeConfig(
            name=self.name,
            add_keys=add_keys,
            remove_keys=remove_keys,
            prepend_path=prepend_path,
            append_path=append_path,
        )


class ConfigurationManager(Atom):
    sections = Dict()
    configurations = Dict()
    recovery_file = Unicode()


class Command(Atom):
    type = Enum('AddKey', 'RemoveKey', 'PrependValue', 'AppendValue', 'RemoveValue')
    name = Str()
    value = Unicode()

    def to_dict(self):
        return {k: getattr(self, k) for k in self.__atom_members__}

    @classmethod
    def from_dict(klass, values):
        return klass(**values)

    def __repr__(self):
        if self.type == 'AddKey':
            return u"AddKey(%s: %s)" % (self.name, self.value)
        elif self.type == 'RemoveKey':
            return u"RemoveKey(%s)" % (self.name,)
        elif self.type == 'PrependValue':
            return u"PrependValue(%s: %s)" % (self.name, self.value)
        elif self.type == 'AppendValue':
            return u"AppendValue(%s: %s)" % (self.name, self.value)
        elif self.type == 'RemoveValue':
            return u"RemoveValue(%s: %s)" % (self.name, self.value)
        else:
            return "Invalid Command"


class ChangeList(Atom):
    do_change = List(Command)
    undo_change = List(Command)
    job_active = Bool(False)

    def to_dict(self):
        return {"do_change": [v.to_dict() for v in self.do_change],
                "undo_change": [v.to_dict() for v in self.undo_change],
                "job_active": self.job_active,
                }

    @classmethod
    def from_dict(klass, value):
        return klass(do_change=[Command.from_dict(v) for v in value.get('do_change', [])],
                     undo_change=[Command.from_dict(v) for v in value.get('undo_change', [])],
                     job_active=value.get('job_active', False),
                     )

    def __repr__(self):
        return "Do:\n%s\n\nUndo:\n%s" % ("\n".join([str(v) for v in self.do_change]),"\n".join([str(v) for v in self.undo_change]))

    def execute(self, commands):
        all_commands = {}
        for cmd in commands:
            all_commands.setdefault(cmd.type, []).append(cmd)

        for cmd in all_commands.get('RemoveKey', []):
            log.debug(cmd)
            try:
                env.delete_key(cmd.name)
            except Exception, e:
                log.error(e)

        for cmd in all_commands.get('AddKey', []):
            log.debug(cmd)
            try:
                env.set_key(cmd.name, cmd.value)
            except Exception, e:
                log.error(e)

        all_value_keys = set()
        prepend_value = {}
        for cmd in all_commands.get('PrependValue', []):
            all_value_keys.add(cmd.name)
            prepend_value.setdefault(cmd.name, []).append(cmd.value)

        append_value = {}
        for cmd in all_commands.get('AppendValue', []):
            all_value_keys.add(cmd.name)
            append_value.setdefault(cmd.name, []).append(cmd.value)

        remove_value = {}
        for cmd in all_commands.get('RemoveValue', []):
            all_value_keys.add(cmd.name)
            remove_value.setdefault(cmd.name, []).append(cmd.value)

        for name in all_value_keys:
            prepends = prepend_value.get(name, [])
            appends = append_value.get(name, [])
            removes = remove_value.get(name, [])
            log.debug("Update %s => Prepends: %s, Appends: %s, Removes: %s" % (name, prepends, appends, removes))
            try:
                env.update_value(name, prepend_values=prepends, append_values=appends, remove_values=removes)
            except Exception, e:
                log.error(e)

    def execute_do_change(self):
        log.info("Execute Do Changes")
        self.execute(self.do_change)

    def execute_undo_change(self):
        log.info("Execute Undo Changes")
        self.execute(self.undo_change)


class CompositeConfig(Atom):
    name = Str()
    add_keys = List(EnvironmentKey)
    remove_keys = List(EnvironmentKey)
    prepend_path = List(EnvironmentValue)
    append_path = List(EnvironmentValue)

    def get_change_list(self, environment=None):
        if environment is None:
            environment = env.enum_keys()

        do_change = []
        undo_change = []
        for v in self.add_keys:
            do_change.append(Command(type='AddKey', name=v.key, value=v.get_value_as_string()))
            undo_change.insert(0, Command(type='RemoveKey', name=v.key))

        for v in self.remove_keys:
            if v.key in environment:
                do_change.insert(0, Command(type='RemoveKey', name=v.key))
                undo_change.append(Command(type='AddKey', name=v.key, value=environment[v.key]))

        for v in self.prepend_path:
            do_change.append(Command(type='PrependValue', name='PATH', value=v.value))
            undo_change.insert(0, Command(type='RemoveValue', name='PATH', value=v.value))

        for v in self.append_path:
            do_change.append(Command(type='AppendValue', name='PATH', value=v.value))
            undo_change.insert(0, Command(type='RemoveValue', name='PATH', value=v.value))

        return ChangeList(do_change=do_change, undo_change=undo_change)


def get_current_environment(user=True):
    t = "USER" if user else "SYSTEM"
    return Environment(type=t, keys=[
        EnvironmentKey(is_default=True,
                       key=k,
                       values=[EnvironmentValue(value=ev.strip()) for ev in v.split(os.pathsep)]
                       ) for k, v in enum_env(user=user).items()
        ])


def parse_config_keys(ini_cfg, section_name):
    defaults = ini_cfg.defaults().keys()
    log.info("Parse config_keys for: %s" % section_name)
    result = []
    if ini_cfg.has_section(section_name):
        for k, v in ini_cfg.items(section_name):
            if k in defaults:
                continue
            result.append(EnvironmentKey(key=k,
                                         values=[EnvironmentValue(value=ev.strip()) for ev in v.split(os.pathsep)]))
    return result


def parse_config_values(ini_cfg, section_name):
    defaults = ini_cfg.defaults().keys()
    log.debug("Parse config_values for: %s" % section_name)
    result = []
    if ini_cfg.has_section(section_name):
        items = dict(ini_cfg.items(section_name))
        keys = sorted([k for k in items.keys() if k not in defaults], lambda a, b: cmp(int(a), int(b)))
        for k in keys:
            if k in defaults:
                continue
            result.append(EnvironmentValue(value=items[k]))
    return result


def parse_config(ini_cfg):
    sections_cfg = [v.strip() for v in ini_cfg.get('environment_manager', 'sections').split(',')]
    configurations_cfg = [v.strip() for v in ini_cfg.get('environment_manager', 'configurations').split(',')]
    recovery_file = ""
    if ini_cfg.has_option('environment_manager', 'recovery_file'):
        recovery_file = ini_cfg.get('environment_manager', 'recovery_file')
    sections = {}
    for section_name in sections_cfg:
        log.debug("Add section: %s" % section_name)
        section_prefix = "section.%s" % section_name
        sections[section_name] = ConfigurationSection(
                name=section_name,
                add_keys=parse_config_keys(ini_cfg, "%s.add_keys" % section_prefix),
                remove_keys=parse_config_keys(ini_cfg, "%s.remove_keys" % section_prefix),
                prepend_path=parse_config_values(ini_cfg, "%s.prepend_path" % section_prefix),
                append_path=parse_config_values(ini_cfg, "%s.append_path" % section_prefix),
            )

    configurations = {}
    for configuration_name in configurations_cfg:
        configuration_section = "configuration.%s" % configuration_name
        if ini_cfg.has_section(configuration_section):
            is_default = ini_cfg.getboolean(configuration_section, "default")
            order = ini_cfg.getint(configuration_section, "order")
            description = ini_cfg.get(configuration_section, "description")
            snames = [v.strip() for v in ini_cfg.get(configuration_section, 'sections').split(',')]
            is_valid = True
            for name in snames:
                if name not in sections.keys():
                    log.error("Missing section: %s for configuration: %s" % (name, configuration_name))
                    is_valid = False
            if is_valid:
                log.info("Add configuration: %s" % configuration_name)
                configurations[configuration_name] = Configuration(
                        name=configuration_name,
                        is_default=is_default,
                        order=order,
                        description=description,
                        sections=[sections[k] for k in snames]
                    )
            else:
                log.error("Configuration: %s is invalid" % configuration_name)

    return ConfigurationManager(sections=sections,
                                configurations=configurations,
                                recovery_file=recovery_file)

