# Copied directly in from python stl
class DynamicClassAttribute:
    """Route attribute access on a class to __getattr__.

    This is a descriptor, used to define attributes that act differently when
    accessed through an instance and through a class.  Instance access remains
    normal, but access to an attribute through a class will be routed to the
    class's __getattr__ method; this is done by raising AttributeError.

    This allows one to have properties active on an instance, and have virtual
    attributes on the class with the same name (see Enum for an example).

    """

    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        # next two lines make DynamicClassAttribute act the same as property
        self.__doc__ = doc or fget.__doc__
        self.overwrite_doc = doc is None
        # support for abstract methods
        self.__isabstractmethod__ = bool(getattr(fget, '__isabstractmethod__', False))

    def __get__(self, instance, ownerclass=None):
        if instance is None:
            if self.__isabstractmethod__:
                return self
            raise AttributeError()
        elif self.fget is None:
            raise AttributeError("unreadable attribute")
        return self.fget(instance)

    def __set__(self, instance, value):
        if self.fset is None:
            raise AttributeError("can't set attribute")
        self.fset(instance, value)

    def __delete__(self, instance):
        if self.fdel is None:
            raise AttributeError("can't delete attribute")
        self.fdel(instance)

    def getter(self, fget):
        fdoc = fget.__doc__ if self.overwrite_doc else None
        result = type(self)(fget, self.fset, self.fdel, fdoc or self.__doc__)
        result.overwrite_doc = self.overwrite_doc
        return result

    def setter(self, fset):
        result = type(self)(self.fget, fset, self.fdel, self.__doc__)
        result.overwrite_doc = self.overwrite_doc
        return result

    def deleter(self, fdel):
        result = type(self)(self.fget, self.fset, fdel, self.__doc__)
        result.overwrite_doc = self.overwrite_doc
        return result


class EnumMeta(type):
    class EnumItem:

        def __init__(self, enum_class_name, name, value):
            self.enum_class_name = enum_class_name
            self._name_ = name
            self._value_ = value

        def __eq__(self, other):
            if isinstance(other, type(self)):
                return self.value == other.value
            if isinstance(other, type(self.value)):
                return self.value == other
            return False

        def __ne__(self, other):
            return not (self == other)

        def __lt__(self, other):
            if isinstance(other, type(self)):
                return self.value < other.value
            if isinstance(other, type(self.value)):
                return self.value < other
            return False

        def __gt__(self, other):
            if isinstance(other, type(self)):
                return self.value > other.value
            if isinstance(other, type(self.value)):
                return self.value > other
            return False

        def __le__(self, other):
            return not (self > other)

        def __ge__(self, other):
            return not (self < other)

        def __and__(self, other):
            if isinstance(other, type(self)):
                return self.value & other.value
            return self.value & other

        def __or__(self, other):
            if isinstance(other, type(self)):
                return self.value | other.value
            return self.value | other

        def __xor__(self, other):
            if isinstance(other, type(self)):
                return self.value ^ other.value
            return self.value ^ other

        def __int__(self):
            return int(self.value)

        def __float__(self):
            return float(self.value)

        def __str__(self):
            return str(self.value)

        def __hash__(self):
            return hash(self._name_)

        def __repr__(self):
            return f'<{self.enum_class_name}.{self.name}: \'{self}\'>'

        @DynamicClassAttribute
        def name(self):
            """The name of the Enum member."""
            return self._name_

        @DynamicClassAttribute
        def value(self):
            """The value of the Enum member."""
            return self._value_

    def __new__(metacls, cls, bases, attributes):

        # Extracts the non dunder methods from attributes list in order
        # to create the enum items
        enum_map = {}
        for name, value in attributes.items():
            if not name.startswith("__"):
                enum_map[name] = value

        for name in enum_map.keys():
            attributes.pop(name)

        # Creates derived enum class
        enum_class = super().__new__(metacls, cls, bases, attributes)

        class EnumClassItem(EnumMeta.EnumItem):
            pass

        setattr(enum_class, "Item", EnumClassItem)

        enum_item_map = {}

        # Adds enum items to derived enum class
        for name, value in enum_map.items():
            enum_item = enum_class.Item(cls, name, value)
            setattr(enum_class, name, enum_item)
            enum_item_map[name] = enum_item

        setattr(enum_class, 'enum_item_map', enum_item_map)

        return enum_class

    def __str__(cls):
        return f'<enum \'{cls.__name__}\'>'

    def __iter__(self):
        self.enum_map_iter = iter(getattr(self, 'enum_item_map', {}).values())
        return self.enum_map_iter

    def __next__(self):
        self.enum_map_iter = next(self.enum_map_iter)
        return self.enum_map_iter


class Enum(metaclass=EnumMeta):

    def __str__(self):
        return "%s.%s" % (self.__class__.__name__, self._name_)

    @classmethod
    def item(cls):
        return

    def __new__(cls, value):
        for enum_item in cls:
            if value == enum_item.value:
                return enum_item
        return None
