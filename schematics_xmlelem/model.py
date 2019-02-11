from collections import OrderedDict
from copy import deepcopy
from types import FunctionType

from schematics import Model
from schematics.exceptions import UndefinedValueError, DataError
from schematics.undefined import Undefined

from .attributes import XmlAttribute
from .children import XmlChildBase
from .content import XmlContent
from .schema import Schema


class FieldDescriptor(object):
    """
    ``FieldDescriptor`` instances serve as field accessors on models.
    """

    def __init__(self, name, t):
        """
        :param name:
            The field's name
        :param t:
            The field's type
        """
        self.name = name
        self.t = t

    def __get__(self, instance, cls):
        """
        For a model instance, returns the field's current value.
        For a model class, returns the field's type object.
        """
        if instance is None:
            return self.t
        else:
            value = instance._data.get(self.name, Undefined)
            if value is Undefined:
                raise UndefinedValueError(instance, self.name)
            else:
                return value

    def __set__(self, instance, value):
        """
        Sets the field's value.
        """
        instance._data[self.name] = value

    def __delete__(self, instance):
        """
        Deletes the field's value.
        """
        del instance._data[self.name]


class XmlElementModelMeta(type):
    """
    Metaclass for XML Models.
    """

    def __new__(mcs, name, bases, attrs):
        """
        This metaclass parses the declarative Model into a corresponding Schema,
        then adding it as the `_schema` attribute to the host class.
        """

        # Structures used to accumulate meta info
        tag_name = name
        attributes = OrderedDict()
        children = OrderedDict()
        content = OrderedDict()
        validator_functions = {}  # Model level

        # Accumulate metas info from parent classes
        for base in reversed(bases):
            if hasattr(base, '_schema'):
                attributes.update(deepcopy(base._schema.attributes))
                children.update(deepcopy(base._schema.children))
                content.update(deepcopy(base._schema.content))
                validator_functions.update(base._schema.validators)

        # Parse this class's attributes into schema structures
        for key, value in attrs.items():
            if key.startswith('validate_') and isinstance(value, (FunctionType, classmethod)):
                validator_functions[key[9:]] = value
            if isinstance(value, XmlAttribute):
                attributes[key] = value
            elif isinstance(value, XmlChildBase):
                children[key] = value
            elif isinstance(value, XmlContent):
                content[key] = value
            elif key == 'tag_name':
                tag_name = str(value)

        # Convert declared fields into descriptors for new class
        for key, t in attributes.items():
            attrs[key] = FieldDescriptor(key, t)
        for key, t in children.items():
            attrs[key] = FieldDescriptor(key, t)
        for key, t in content.items():
            attrs[key] = FieldDescriptor(key, t)

        if len(content) > 1:
            raise AssertionError('Cannot have more than one content attribute')

        klass = type.__new__(mcs, name, bases, attrs)

        # Parse meta data into new schema
        klass._schema = Schema(
            name, tag_name=tag_name, model=klass, validators=validator_functions,
            attributes=attributes, children=children, content=content
        )

        return klass


class XmlElementModel(object, metaclass=XmlElementModelMeta):
    def __init__(self, raw_value=None, **kwargs):
        self._data = {}
        for k, v in self._schema.attributes.items():
            default = v.from_default()
            if default is not Undefined:
                self._data[k] = default
        for k, v in self._schema.children.items():
            default = v.from_default()
            if default is not Undefined:
                self._data[k] = default
        for k, v in self._schema.content.items():
            default = v.from_default()
            if default is not Undefined:
                self._data[k] = default

        if raw_value is not None:
            self.import_data(raw_value)

        self._data.update(kwargs)

    def _import_attributes(self, attrib, strict=False):
        for attrib_name, attrib_value in attrib.items():
            for field_name, v in self._schema.attributes.items():
                if v.matches(field_name, attrib_name):
                    self._data[field_name] = v.from_attr(field_name, attrib_value)
                    break
            else:
                if strict:
                    raise DataError({attrib_name: 'Rogue attribute'})

    def _import_children(self, children, strict=False):
        for child in children:
            for field_name, v in self._schema.children.items():
                match_result = v.matches(field_name, child)
                if match_result:
                    self._data[field_name] = v.incorporate_child(
                        match_result, self._data.get(field_name, Undefined), child
                    )
                    break
            else:
                if strict:
                    raise DataError({child['tag']: 'Rogue child'})

    def _import_content(self, content, strict=False):
        if content is not None:
            for field_name, v in self._schema.content.items():
                self._data[field_name] = v.from_content(content)
                break
            else:
                if strict:
                    raise DataError({'text': 'Rogue content'})

    def import_data(self, raw_value, strict=False):
        self._import_attributes(raw_value.get('attrib', {}), strict)
        self._import_children(raw_value.get('children', []), strict)
        self._import_content(raw_value.get('text'), strict)

    def _export_attributes(self):
        attrib = {}
        for field_name, v in self._schema.attributes.items():
            value = self._data.get(field_name, Undefined)
            if value is not Undefined:
                attrib.update(v.to_attr(field_name, value))
        return attrib

    def _export_children(self):
        children = []
        for field_name, v in self._schema.children.items():
            value = self._data.get(field_name, Undefined)
            if value is not Undefined:
                children.extend(v.to_children(field_name, value))
        return children

    def _export_content(self):
        for field_name, v in self._schema.content.items():
            value = self._data.get(field_name, Undefined)
            if value is not Undefined:
                return v.to_content(value)
        return None

    def to_primitive(self):
        return {
            'tag': self._schema.tag_name,
            'attrib': self._export_attributes(),
            'children': self._export_children(),
            'text': self._export_content(),
        }
