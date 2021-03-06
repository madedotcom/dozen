import collections
import sys
import os


def _make_nmtuple(name, types):
    msg = "NamedTuple('Name', [(f0, t0), (f1, t1), ...]); each t must be a type"
    nm_tpl = collections.namedtuple(name, [n for n, t in types])
    # Prior to PEP 526, only _field_types attribute was assigned.
    # Now, both __annotations__ and _field_types are used to maintain compatibility.
    nm_tpl.__annotations__ = nm_tpl._field_types = collections.OrderedDict(
        types)
    try:
        nm_tpl.__module__ = sys._getframe(2).f_globals.get(
            "__name__", "__main__")
    except (AttributeError, ValueError):
        pass

    return nm_tpl


# attributes prohibited to set in NamedTuple class syntax
_prohibited = (
    "__new__",
    "__init__",
    "__slots__",
    "__getnewargs__",
    "_fields",
    "_field_defaults",
    "_field_types",
    "_make",
    "_replace",
    "_asdict",
    "_source",
)

_special = ("__module__", "__name__", "__qualname__", "__annotations__")


def bool_from_str(val):

    if val is None or val.isspace():
        return False

    if val == "0":
        return False

    if val == "-1":
        return False

    if val == "1":
        return True

    if val.upper() == "FALSE":
        return False

    return True


def parse_if_present(f):
    def p(name, prefix, env, args):
        var = (prefix + name).upper()

        if var not in env:
            return
        val = env[var]
        args[name] = f(val)

    return p


_READERS = {
    int: parse_if_present(int),
    float: parse_if_present(float),
    str: parse_if_present(str),
    bool: parse_if_present(bool_from_str),
}

service_instance = collections.namedtuple("_dozen_service_instance",
                                          "host port")


def service(default_port=None, default_host=None):
    def _(name, prefix, env, args):
        host_var = env.get((name + "_host").upper())
        port_var = env.get((name + "_port").upper())

        args[name] = service_instance(host_var or default_host,
                                      int(port_var or default_port))

    return _


@classmethod
def build(cls, env=None, prefix=""):

    if prefix and not prefix.endswith("_"):
        prefix += "_"

    if env is None:
        env = os.environ

    args = {}

    for name, reader in cls.__fields.items():

        # I really want to be able to say "If this is a nested template"

        if hasattr(reader, "build"):
            val = reader.build(env=env, prefix=(name.upper() + "_" + prefix))

            if val is not None:
                args[name] = val

        else:
            try:
                val = reader(name, prefix, env, args)
            except ValueError as e:
                raise ValueError(
                    f"Error parsing '{name}' property of '{cls.__inner_type.__name__}':\n"
                    + str(e))

    for k in cls.__fields.keys():
        if k not in args:
            if k in cls.__defaults:
                args[k] = cls.__defaults[k]
            else:
                raise KeyError(k)

    return cls.__inner_type(**args)


class TemplateMeta(type):
    def __new__(cls, typename, bases, ns):
        if ns.get("_root", False):
            return super().__new__(cls, typename, bases, ns)
        types = ns.get("__annotations__", {})

        inner_type = _make_nmtuple(typename, types.items())
        defaults_dict = {}

        for field_name in types:
            if field_name in ns:
                default_value = ns[field_name]
                defaults_dict[field_name] = default_value

        ns["build"] = build
        ns["__inner_type"] = inner_type

        ns["__fields"] = dict(
            [(n, _READERS.get(t) or t) for n, t in types.items()])
        ns["__defaults"] = defaults_dict
        result = type(typename, (object, ), ns)

        return result


class _TemplateMeta(type):
    def __new__(cls, typename, bases, ns):
        types = ns.get("__annotations__", {})
        print(types)
        nm_tpl = _make_nmtuple(typename, types.items())
        defaults = []
        defaults_dict = {}

        for field_name in types:
            if field_name in ns:
                default_value = ns[field_name]
                defaults.append(default_value)
                defaults_dict[field_name] = default_value
            elif defaults:
                raise TypeError(
                    "Non-default namedtuple field {field_name} cannot "
                    "follow default field(s) {default_names}".format(
                        field_name=field_name,
                        default_names=", ".join(defaults_dict.keys()),
                    ))
        nm_tpl.__new__.__annotations__ = collections.OrderedDict(types)
        nm_tpl.__new__.__defaults__ = tuple(defaults)
        nm_tpl._field_defaults = defaults_dict
        # update from user namespace without overriding special namedtuple attributes

        for key in ns:
            if key in _prohibited:
                raise AttributeError("Cannot overwrite NamedTuple attribute " +
                                     key)
            elif key not in _special and key not in nm_tpl._fields:
                setattr(nm_tpl, key, ns[key])

        return nm_tpl


class Template(metaclass=TemplateMeta):
    _root = True
