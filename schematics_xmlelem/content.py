from schematics.undefined import Undefined

from schematics_xmlelem.types import XmlBaseType


class XmlContent(object):
    def __init__(self, type_: XmlBaseType, default=Undefined):
        self.type_ = type_
        self.default = default

    def from_content(self, value):
        return self.type_.to_native(value)

    def to_content(self, value):
        return self.type_.to_primitive(value)

    def from_default(self):
        if callable(self.default):
            return self.default()
        else:
            return self.default
