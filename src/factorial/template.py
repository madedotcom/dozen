import inspect
import collections
import sys


def _make_nmtuple(name, types):
    msg = "NamedTuple('Name', [(f0, t0), (f1, t1), ...]); each t must be a type"
    nm_tpl = collections.namedtuple(name, [n for n, t in types])
    # Prior to PEP 526, only _field_types attribute was assigned.
    # Now, both __annotations__ and _field_types are used to maintain compatibility.
    nm_tpl.__annotations__ = nm_tpl._field_types = collections.OrderedDict(types)
    try:
        nm_tpl.__module__ = sys._getframe(2).f_globals.get('__name__', '__main__')
    except (AttributeError, ValueError):
        pass

    return nm_tpl


# attributes prohibited to set in NamedTuple class syntax
_prohibited = ('__new__', '__init__', '__slots__', '__getnewargs__',
               '_fields', '_field_defaults', '_field_types',
               '_make', '_replace', '_asdict', '_source')

_special = ('__module__', '__name__', '__qualname__', '__annotations__')

def parse_bool(name, prefix, env):

    var = (prefix + name).upper()
    val = env.get(var)

    if val is None or val.isspace():
        return False

    if val == '0':
        return False

    if val == '-1':
        return False

    if val == '1':
        return True

    if val.upper() == 'FALSE':
        return False

    return True


def parse_int(name, prefix, env):
    var = (prefix + name).upper()
    val = env.get(var)
    return int(val)


def parse_str(name, prefix, env):
    var = (prefix + name).upper()
    return env.get(var)


def parse_float(name, prefix, env):
    var = (prefix + name).upper()
    val = env.get(var)
    return float(val)


_READERS = {
    int: parse_int,
    float: parse_float,
    str: parse_str,
    bool: parse_bool
}

@classmethod
def build(cls, env=None, prefix=''):

    if prefix and not prefix.endswith('_'):
        prefix += '_'

    args = {}
    for name, reader in cls.__fields.items():
        if inspect.isclass(reader):
            if hasattr(reader, 'build'):
                args[name] = reader.build(env=env, prefix=(name.upper()+'_'+prefix))
                continue
        try:
            args[name] = reader(name, prefix, env)
        except ValueError as e:
            raise ValueError(f"Error parsing '{name}' property of '{cls.__inner_type.__name__}':\n" +
                    str(e))


    return cls.__inner_type(**args)

class TemplateMeta(type):

    def __new__(cls, typename, bases, ns):
        if ns.get('_root', False):
            return super().__new__(cls, typename, bases, ns)
        types = ns.get('__annotations__', {})

        inner_type = _make_nmtuple(typename, types.items())

        ns['build'] = build
        ns['__inner_type'] = inner_type

        fields = {}
        ns['__fields'] = dict([(n, _READERS.get(t) or t) for n, t in types.items()])
        result = type(typename, (object,), ns)

        return result


class _TemplateMeta(type):

    def __new__(cls, typename, bases, ns):
        types = ns.get('__annotations__', {})
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
                raise TypeError("Non-default namedtuple field {field_name} cannot "
                                "follow default field(s) {default_names}"
                                .format(field_name=field_name,
                                        default_names=', '.join(defaults_dict.keys())))
        nm_tpl.__new__.__annotations__ = collections.OrderedDict(types)
        nm_tpl.__new__.__defaults__ = tuple(defaults)
        nm_tpl._field_defaults = defaults_dict
        # update from user namespace without overriding special namedtuple attributes

        for key in ns:
            if key in _prohibited:
                raise AttributeError("Cannot overwrite NamedTuple attribute " + key)
            elif key not in _special and key not in nm_tpl._fields:
                setattr(nm_tpl, key, ns[key])

        return nm_tpl

class NamedTuple():
    """Typed version of namedtuple.
    Usage in Python versions >= 3.6::
        class Employee(NamedTuple):
            name: str
            id: int
    This is equivalent to::
        Employee = collections.namedtuple('Employee', ['name', 'id'])
    The resulting class has extra __annotations__ and _field_types
    attributes, giving an ordered dict mapping field names to types.
    __annotations__ should be preferred, while _field_types
    is kept to maintain pre PEP 526 compatibility. (The field names
    are in the _fields attribute, which is part of the namedtuple
    API.) Alternative equivalent keyword syntax is also accepted::
        Employee = NamedTuple('Employee', name=str, id=int)
    In Python versions <= 3.5 use::
        Employee = NamedTuple('Employee', [('name', str), ('id', int)])
    """
    _root = True

    def __new__(self, typename, fields=None, **kwargs):
        if fields is None:
            fields = kwargs.items()
        elif kwargs:
            raise TypeError("Either list of fields or keywords"
                            " can be provided to NamedTuple, not both")

        return _make_nmtuple(typename, fields)

class Template(metaclass=TemplateMeta):
    _root = True
