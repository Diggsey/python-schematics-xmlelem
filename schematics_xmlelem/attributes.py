from typing import Optional

from schematics.undefined import Undefined

from schematics_xmlelem.casing import to_camelcase
from schematics_xmlelem.types import XmlBaseType


class XmlAttribute(object):
    def __init__(self, type_: Optional[XmlBaseType], serialized_name=None, case_sensitive=True, default=Undefined):
        self.type_ = type_
        self.serialized_name = serialized_name
        self.case_sensitive = case_sensitive
        self.default = default

    def _attrib_name(self, field_name):
        if self.serialized_name is not None:
            return self.serialized_name
        else:
            return to_camelcase(field_name)

    def matches(self, field_name, attrib_name):
        field_name = self._attrib_name(field_name)
        if not self.case_sensitive:
            field_name = field_name.lower()
            attrib_name = attrib_name.lower()
        return field_name == attrib_name

    def from_attr(self, field_name, value):
        return self.type_.to_native(value)

    def to_attr(self, field_name, value):
        if value is None:
            return {}
        else:
            return {self._attrib_name(field_name): self.type_.to_primitive(value)}

    def from_default(self):
        if callable(self.default):
            return self.default()
        else:
            return self.default


class XmlBooleanAttribute(XmlAttribute):
    def __init__(self, serialized_name=None, case_sensitive=True):
        super().__init__(None, serialized_name=serialized_name, case_sensitive=case_sensitive, default=False)

    def from_attr(self, field_name, value):
        field_name = self._attrib_name(field_name)
        if not self.case_sensitive:
            field_name = field_name.lower()
            value = value.lower()
        return field_name == value

    def to_attr(self, field_name, value):
        if value:
            field_name = self._attrib_name(field_name)
            return {field_name: field_name}
        else:
            return {}
