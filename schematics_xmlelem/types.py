from schematics.exceptions import ConversionError


class XmlBaseType(object):
    def __init__(self, choices=None):
        self.choices = choices

    def _validate_choice(self, value):
        if self.choices is not None:
            if value not in self.choices:
                raise ConversionError('Value was not in the set of allowed choices')
        return value

    def to_primitive(self, value):
        raise NotImplementedError()

    def to_native(self, value):
        raise NotImplementedError()


class XmlStringType(XmlBaseType):
    def to_primitive(self, value):
        return value

    def to_native(self, value):
        return self._validate_choice(value)


class XmlIntType(XmlBaseType):
    def to_primitive(self, value):
        return str(value)

    def to_native(self, value):
        return self._validate_choice(int(value))


class XmlFloatType(XmlBaseType):
    def to_primitive(self, value):
        return str(value)

    def to_native(self, value):
        return self._validate_choice(float(value))
