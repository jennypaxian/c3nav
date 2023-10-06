import re
import struct
from abc import ABC, abstractmethod
from dataclasses import Field, dataclass, fields
from typing import Any, Self, Sequence

from c3nav.mesh.utils import indent_c


class BaseFormat(ABC):

    def get_var_num(self):
        return 0

    @abstractmethod
    def encode(self, value):
        pass

    @classmethod
    @abstractmethod
    def decode(cls, data) -> tuple[Any, bytes]:
        pass

    def fromjson(self, data):
        return data

    def tojson(self, data):
        return data

    @abstractmethod
    def get_min_size(self):
        pass

    @abstractmethod
    def get_c_parts(self) -> tuple[str, str]:
        pass

    def get_c_code(self, name) -> str:
        pre, post = self.get_c_parts()
        return "%s %s%s;" % (pre, name, post)


class SimpleFormat(BaseFormat):
    def __init__(self, fmt):
        self.fmt = fmt
        self.size = struct.calcsize(fmt)

        self.c_type = self.c_types[self.fmt[-1]]
        self.num = int(self.fmt[:-1]) if len(self.fmt) > 1 else 1

    def encode(self, value):
        if self.num == 1:
            return struct.pack(self.fmt, value)
        return struct.pack(self.fmt, *value)

    def decode(self, data: bytes) -> tuple[Any, bytes]:
        value = struct.unpack(self.fmt, data[:self.size])
        if len(value) == 1:
            value = value[0]
        return value, data[self.size:]

    def get_min_size(self):
        return self.size

    c_types = {
        "B": "uint8_t",
        "H": "uint16_t",
        "I": "uint32_t",
        "b": "int8_t",
        "h": "int16_t",
        "i": "int32_t",
        "s": "char",
    }

    def get_c_parts(self):
        return self.c_type, ("" if self.num == 1 else ("[%d]" % self.num))


class BoolFormat(SimpleFormat):
    def __init__(self):
        super().__init__('B')

    def encode(self, value):
        return super().encode(int(value))

    def decode(self, data: bytes) -> tuple[bool, bytes]:
        value, data = super().decode(data)
        return bool(value), data


class FixedStrFormat(SimpleFormat):
    def __init__(self, num):
        self.num = num
        super().__init__('%ds' % self.num)

    def encode(self, value: str):
        return value.encode()[:self.num].ljust(self.num, bytes((0,))),

    def decode(self, data: bytes) -> tuple[str, bytes]:
        return data[:self.num].rstrip(bytes((0,))).decode(), data[self.num:]


class FixedHexFormat(SimpleFormat):
    def __init__(self, num, sep=''):
        self.num = num
        self.sep = sep
        super().__init__('%dB' % self.num)

    def encode(self, value: str):
        return super().encode(tuple(bytes.fromhex(value.replace(':', ''))))

    def decode(self, data: bytes) -> tuple[str, bytes]:
        return self.sep.join(('%02x' % i) for i in data[:self.num]), data[self.num:]


@abstractmethod
class BaseVarFormat(BaseFormat, ABC):
    def __init__(self, num_fmt='B'):
        self.num_fmt = num_fmt
        self.num_size = struct.calcsize(self.num_fmt)

    def get_min_size(self):
        return self.num_size

    def get_num_c_code(self):
        return SimpleFormat(self.num_fmt).get_c_code("num")


class VarArrayFormat(BaseVarFormat):
    def __init__(self, child_type, num_fmt='B'):
        super().__init__(num_fmt=num_fmt)
        self.child_type = child_type
        self.child_size = self.child_type.get_min_size()

    def get_var_num(self):
        return self.child_size
        pass

    def encode(self, values: Sequence) -> bytes:
        data = struct.pack(self.num_fmt, len(values))
        for value in values:
            data += self.child_type.encode(value)
        return data

    def decode(self, data: bytes) -> tuple[list[Any], bytes]:
        num = struct.unpack(self.num_fmt, data[:self.num_size])[0]
        data = data[self.num_size:]
        result = []
        for i in range(num):
            item, data = self.child_type.decode(data)
            result.append(item)
        return result, data

    def get_c_parts(self):
        pre, post = self.child_type.get_c_parts()
        return super().get_num_c_code() + "\n" + pre, "[0]" + post


class VarStrFormat(BaseVarFormat):

    def get_var_num(self):
        return 1

    def encode(self, value: str) -> bytes:
        return struct.pack(self.num_fmt, len(str)) + value.encode()

    def decode(self, data: bytes) -> tuple[str, bytes]:
        num = struct.unpack(self.num_fmt, data[:self.num_size])[0]
        return data[self.num_size:self.num_size + num].rstrip(bytes((0,))).decode(), data[self.num_size + num:]

    def get_c_parts(self):
        return super().get_num_c_code() + "\n" + "char", "[0]"


@dataclass
class StructType:
    _union_options = {}
    union_type_field = None

    # noinspection PyMethodOverriding
    def __init_subclass__(cls, /, union_type_field=None, no_c_type=False, **kwargs):
        cls.union_type_field = union_type_field
        if union_type_field:
            if union_type_field in cls._union_options:
                raise TypeError('Duplicate union_type_field: %s', union_type_field)
            cls._union_options[union_type_field] = {}
            f = getattr(cls, union_type_field)
            metadata = dict(f.metadata)
            metadata['union_discriminator'] = True
            f.metadata = metadata
            f.repr = False
            f.init = False

        for attr_name in cls.__dict__.keys():
            attr = getattr(cls, attr_name)
            if isinstance(attr, Field):
                metadata = dict(attr.metadata)
                if "defining_class" not in metadata:
                    metadata["defining_class"] = cls
                attr.metadata = metadata

        for key, values in cls._union_options.items():
            value = kwargs.pop(key, None)
            if value is not None:
                if value in values:
                    raise TypeError('Duplicate %s: %s', (key, value))
                values[value] = cls
                setattr(cls, key, value)
        super().__init_subclass__(**kwargs)

    @classmethod
    def get_var_num(cls):
        return sum([f.metadata.get("format", f.type).get_var_num() for f in fields(cls)], start=0)

    @classmethod
    def get_types(cls):
        if not cls.union_type_field:
            raise TypeError('Not a union class')
        return cls._union_options[cls.union_type_field]

    @classmethod
    def get_type(cls, type_id) -> Self:
        if not cls.union_type_field:
            raise TypeError('Not a union class')
        return cls.get_types()[type_id]

    @classmethod
    def encode(cls, instance, ignore_fields=()) -> bytes:
        data = bytes()
        if cls.union_type_field and type(instance) is not cls:
            if not isinstance(instance, cls):
                raise ValueError('expected value of type %r, got %r' % (cls, instance))

            for field_ in fields(cls):
                data += field_.metadata["format"].encode(getattr(instance, field_.name))

            # todo: better
            data += instance.encode(instance, ignore_fields=set(f.name for f in fields(cls)))
            return data

        for field_ in fields(cls):
            if field_.name in ignore_fields:
                continue
            value = getattr(instance, field_.name)
            if "format" in field_.metadata:
                data += field_.metadata["format"].encode(value)
            elif issubclass(field_.type, StructType):
                if not isinstance(value, field_.type):
                    raise ValueError('expected value of type %r for %s.%s, got %r' %
                                     (field_.type, cls.__name__, field_.name, value))
                data += value.encode(value)
            else:
                raise TypeError('field %s.%s has no format and is no StructType' %
                                (cls.__class__.__name__, field_.name))
        return data

    @classmethod
    def decode(cls, data: bytes) -> tuple[Self, bytes]:
        orig_data = data
        kwargs = {}
        no_init_data = {}
        for field_ in fields(cls):
            if "format" in field_.metadata:
                value, data = field_.metadata["format"].decode(data)
            elif issubclass(field_.type, StructType):
                value, data = field_.type.decode(data)
            else:
                raise TypeError('field %s.%s has no format and is no StructType' %
                                (cls.__name__, field_.name))
            if field_.init:
                kwargs[field_.name] = value
            else:
                no_init_data[field_.name] = value

        if cls.union_type_field:
            try:
                type_value = no_init_data[cls.union_type_field]
            except KeyError:
                raise TypeError('union_type_field %s.%s is missing' %
                                (cls.__name__, cls.union_type_field))
            try:
                klass = cls.get_type(type_value)
            except KeyError:
                raise TypeError('union_type_field %s.%s value %r no known' %
                                (cls.__name__, cls.union_type_field, type_value))
            return klass.decode(orig_data)
        return cls(**kwargs), data

    @classmethod
    def tojson(cls, instance) -> dict:
        result = {}

        if cls.union_type_field and type(instance) is not cls:
            if not isinstance(instance, cls):
                raise ValueError('expected value of type %r, got %r' % (cls, instance))

            for field_ in fields(instance):
                if field_.name is cls.union_type_field:
                    result[field_.name] = field_.metadata["format"].tojson(getattr(instance, field_.name))
                    break
            else:
                raise TypeError('couldn\'t find %s value' % cls.union_type_field)

            result.update(instance.tojson(instance))
            return result

        for field_ in fields(cls):
            value = getattr(instance, field_.name)
            if "format" in field_.metadata:
                result[field_.name] = field_.metadata["format"].tojson(value)
            elif issubclass(field_.type, StructType):
                if not isinstance(value, field_.type):
                    raise ValueError('expected value of type %r for %s.%s, got %r' %
                                     (field_.type, cls.__name__, field_.name, value))
                result[field_.name] = value.tojson(value)
            else:
                raise TypeError('field %s.%s has no format and is no StructType' %
                                (cls.__class__.__name__, field_.name))
        return result

    @classmethod
    def upgrade_json(cls, data):
        return data

    @classmethod
    def fromjson(cls, data: dict):
        data = data.copy()

        # todo: upgrade_json
        cls.upgrade_json(data)

        kwargs = {}
        no_init_data = {}
        for field_ in fields(cls):
            raw_value = data.get(field_.name, None)
            if "format" in field_.metadata:
                value = field_.metadata["format"].fromjson(raw_value)
            elif issubclass(field_.type, StructType):
                value = field_.type.fromjson(raw_value)
            else:
                raise TypeError('field %s.%s has no format and is no StructType' %
                                (cls.__name__, field_.name))
            if field_.init:
                kwargs[field_.name] = value
            else:
                no_init_data[field_.name] = value

        if cls.union_type_field:
            try:
                type_value = no_init_data.pop(cls.union_type_field)
            except KeyError:
                raise TypeError('union_type_field %s.%s is missing' %
                                (cls.__name__, cls.union_type_field))
            try:
                klass = cls.get_type(type_value)
            except KeyError:
                raise TypeError('union_type_field %s.%s value 0x%02x no known' %
                                (cls.__name__, cls.union_type_field, type_value))
            return klass.fromjson(data)

        return cls(**kwargs)

    @classmethod
    def get_c_struct_items(cls, ignore_fields=None, no_empty=False, top_level=False, union_only=False, in_union=False):
        ignore_fields = set() if not ignore_fields else set(ignore_fields)

        items = []

        for field_ in fields(cls):
            if field_.name in ignore_fields:
                continue
            if in_union and field_.metadata["defining_class"] != cls:
                continue

            name = field_.metadata.get("c_name", field_.name)
            if "format" in field_.metadata:
                if not field_.metadata.get("union_discriminator") or field_.metadata.get("defining_class") == cls:
                    items.append((
                        field_.metadata["format"].get_c_code(name),
                        field_.metadata.get("doc", None),
                    )),
            elif issubclass(field_.type, StructType):
                if field_.metadata.get("c_embed"):
                    embedded_items = field_.type.get_c_struct_items(ignore_fields, no_empty, top_level, union_only)
                    items.extend(embedded_items)
                else:
                    items.append((
                        field_.type.get_c_code(name, typedef=False),
                        field_.metadata.get("doc", None),
                    ))
            else:
                raise TypeError('field %s.%s has no format and is no StructType' %
                                (cls.__name__, field_.name))

        if cls.union_type_field:
            if not union_only:
                union_code = cls.get_c_union_code(ignore_fields)
                items.append(("union __packed %s;" % union_code, ""))

        return items

    @classmethod
    def get_c_union_size(cls):
        return max(
            (option.get_min_size(no_inherited_fields=True) for option in
             cls._union_options[cls.union_type_field].values()),
            default=0,
        )

    @classmethod
    def get_c_union_code(cls, ignore_fields=None):
        union_items = []
        for key, option in cls._union_options[cls.union_type_field].items():
            base_name = normalize_name(getattr(key, 'name', option.__name__))
            union_items.append(
                option.get_c_code(base_name, ignore_fields=ignore_fields, typedef=False, in_union=True)
            )
        size = cls.get_c_union_size()
        union_items.append(
            "uint8_t bytes[%0d]; " % size
        )
        return "{\n" + indent_c("\n".join(union_items)) + "\n}"

    @classmethod
    def get_c_parts(cls, ignore_fields=None, no_empty=False, top_level=False, union_only=False, in_union=False):
        ignore_fields = set() if not ignore_fields else set(ignore_fields)

        if union_only:
            if cls.union_type_field:
                union_code = cls.get_c_union_code(ignore_fields)
                return "typedef union __packed %s" % union_code, ""
            else:
                return "", ""

        pre = ""

        items = cls.get_c_struct_items(ignore_fields=ignore_fields,
                                       no_empty=no_empty,
                                       top_level=top_level,
                                       union_only=union_only,
                                       in_union=in_union)

        if no_empty and not items:
            return "", ""

        # todo: struct comment
        if top_level:
            comment = cls.__doc__.strip()
            if comment:
                pre += "/** %s */\n" % comment
            pre += "typedef struct __packed "
        else:
            pre += "struct __packed "

        pre += "{\n%(elements)s\n}" % {
            "elements": indent_c(
                "\n".join(
                    code + ("" if not comment else (" /** %s */" % comment))
                    for code, comment in items
                )
            ),
        }
        return pre, ""

    @classmethod
    def get_c_code(cls, name=None, ignore_fields=None, no_empty=False, typedef=True, union_only=False,
                   in_union=False) -> str:
        pre, post = cls.get_c_parts(ignore_fields=ignore_fields,
                                    no_empty=no_empty,
                                    top_level=typedef,
                                    union_only=union_only,
                                    in_union=in_union)
        if no_empty and not pre and not post:
            return ""
        return "%s %s%s;" % (pre, name, post)

    @classmethod
    def get_variable_name(cls, base_name):
        return base_name

    @classmethod
    def get_struct_name(cls, base_name):
        return "%s_t" % base_name

    @classmethod
    def get_min_size(cls, no_inherited_fields=False) -> int:
        if cls.union_type_field:
            own_size = sum([f.metadata.get("format", f.type).get_min_size() for f in fields(cls)])
            union_size = max(
                [0] + [option.get_min_size(True) for option in cls._union_options[cls.union_type_field].values()])
            return own_size + union_size
        if no_inherited_fields:
            relevant_fields = [f for f in fields(cls) if f.metadata["defining_class"] == cls]
        else:
            relevant_fields = [f for f in fields(cls) if not f.metadata.get("union_discriminator")]
        return sum((f.metadata.get("format", f.type).get_min_size() for f in relevant_fields), start=0)


def normalize_name(name):
    if '_' in name:
        return name.lower()
    return re.sub(
        r"([a-z])([A-Z])",
        r"\1_\2",
        name
    ).lower()