from atom.api import Atom, Value, List, Dict, Str, Bool, Int, Float, Enum, Typed, Coerced, Unicode


class EnvironmentKey(Atom):
    replace = Bool(False)
    name = Unicode()
    values = List(Str)


class UserEnvironment(Atom):
    keys = Typed(EnvironmentKey)

    