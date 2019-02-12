from schematics.undefined import Undefined

from schematics_xmlelem.mixins import DefaultValueMixin
from schematics_xmlelem.types import XmlBaseType


class XmlContentBase(DefaultValueMixin):
    def from_content(self, value):
        raise NotImplementedError()

    def to_content(self, value):
        raise NotImplementedError()


class XmlContent(XmlContentBase):
    def __init__(self, type_: XmlBaseType, strip=True, **kwargs):
        super().__init__(**kwargs)
        self.type_ = type_
        self.strip = strip

    def from_content(self, value):
        if self.strip:
            value = value.strip()
        return self.type_.to_native(value)

    def to_content(self, value):
        return self.type_.to_primitive(value)
