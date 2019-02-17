from schematics.exceptions import ConversionError


class XmlBaseType(object):
    def __init__(self, choices=None, **kwargs):
        super().__init__(**kwargs)
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


BOOL_ONE_ZERO = ['1', '0']
BOOL_TRUE_FALSE = ['true', 'false']
BOOL_ON_OFF = ['on', 'off']
BOOL_ENABLED_DISABLED = ['enabled', 'disabled']


def _compare_reference_value(reference, value, case_sensitive):
    if isinstance(reference, str):
        if not case_sensitive:
            reference = reference.lower()
            value = value.lower()
    else:
        try:
            value = reference.__class__(value)
        except ValueError:
            return False
    return reference == value


class XmlBoolType(XmlBaseType):
    def __init__(self, bool_values=BOOL_ONE_ZERO, case_sensitive=False, **kwargs):
        super().__init__(**kwargs)
        self.bool_values = bool_values
        self.case_sensitive = case_sensitive

    def to_primitive(self, value):
        if value:
            return str(self.bool_values[0])
        else:
            return str(self.bool_values[1])

    def to_native(self, value):
        if _compare_reference_value(self.bool_values[0], value, self.case_sensitive):
            return True
        elif _compare_reference_value(self.bool_values[1], value, self.case_sensitive):
            return False
        else:
            raise ConversionError('Value not recognised as a boolean')


class XmlEnumType(XmlBaseType):
    def __init__(self, enum_class, case_sensitive=False, **kwargs):
        super().__init__(**kwargs)
        self.enum_class = enum_class
        self.case_sensitive = case_sensitive

    def to_primitive(self, value):
        return str(value.value)

    def to_native(self, value):
        for variant in self.enum_class:
            if _compare_reference_value(variant.value, value, self.case_sensitive):
                return variant
        raise ConversionError('Value not recognised as a variant of enum')
