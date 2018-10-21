from enum import Enum, EnumMeta


class DugaEnumMeta(EnumMeta):
    """
    So that we can alter __getitem__
    https://stackoverflow.com/a/24717640/2805700
    """
    def __getitem__(self, name):
        if isinstance(name, str):
            return super().__getitem__(name.upper())
        else:
            return super().__getitem__(name)


class DugaEnum(Enum, metaclass=DugaEnumMeta):

    def __eq__(self, other):
        if isinstance(other, str):
            return self.value == other
        try:
            return self.value == other.value
        except AttributeError:
            return False
