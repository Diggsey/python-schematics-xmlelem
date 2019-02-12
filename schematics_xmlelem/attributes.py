from typing import Optional

from schematics_xmlelem.mixins import DefaultValueMixin, OverridableAttribNameMixin
from schematics_xmlelem.types import XmlBaseType


class XmlAttributeBase(DefaultValueMixin, OverridableAttribNameMixin):
    def matches(self, field_name, attrib_name):
        return self._compare_name(field_name, attrib_name)

    def from_attr(self, field_name, value):
        raise NotImplementedError()

    def to_attr(self, field_name, value):
        raise NotImplementedError()


class XmlAttribute(XmlAttributeBase):
    def __init__(self, type_: Optional[XmlBaseType], **kwargs):
        super().__init__(**kwargs)
        self.type_ = type_

    def from_attr(self, field_name, value):
        return self.type_.to_native(value)

    def to_attr(self, field_name, value):
        if value is None:
            return {}
        else:
            return {self._get_name(field_name): self.type_.to_primitive(value)}


class XmlBooleanAttribute(XmlAttributeBase):
    def __init__(self, **kwargs):
        super().__init__(default=False, **kwargs)

    def from_attr(self, field_name, value):
        return self._compare_name(field_name, value)

    def to_attr(self, field_name, value):
        if value:
            name = self._get_name(field_name)
            return {name: name}
        else:
            return {}
