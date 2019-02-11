from typing import TYPE_CHECKING
from schematics.types import BaseType

if TYPE_CHECKING:
    from schematics_xmlelem.model import XmlElementModelMeta


class XmlModelType(BaseType):
    def __init__(self, model: 'XmlElementModelMeta'):
        self.model = model

    def to_primitive(self, value, context=None):
        """Convert internal data to a value safe to serialize.
        """
        return value.to_primitive()

    def to_native(self, value, context=None):
        """
        Convert untrusted data to a richer Python construct.
        """
        return self.model(raw_value=value)
