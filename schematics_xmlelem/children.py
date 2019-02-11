import itertools
from typing import List, Union, TYPE_CHECKING

from schematics.undefined import Undefined

from schematics_xmlelem.casing import to_upper_camelcase

if TYPE_CHECKING:
    from schematics_xmlelem.model import XmlElementModelMeta
    from schematics_xmlelem.types import XmlBaseType


def _get_all_subclasses(cls):
    all_subclasses = []

    for subclass in cls.__subclasses__():
        all_subclasses.append(subclass)
        all_subclasses.extend(_get_all_subclasses(subclass))

    return all_subclasses


class XmlChildBase(object):
    def __init__(self, default=Undefined):
        self.default = default

    def matches(self, field_name, elem):
        raise NotImplementedError()

    def incorporate_child(self, match_result, old_value, child):
        raise NotImplementedError()

    def to_children(self, field_name, value):
        raise NotImplementedError()

    def from_default(self):
        if callable(self.default):
            return self.default()
        else:
            return self.default


class XmlChild(XmlChildBase):
    def __init__(
            self,
            candidates: Union['XmlElementModelMeta', List['XmlElementModelMeta']],
            default=Undefined,
            allow_subclasses=False
    ):
        super().__init__(default=default)

        from .model import XmlElementModelMeta

        if isinstance(candidates, XmlElementModelMeta):
            candidates = [candidates]
        self.candidates = candidates
        self.allow_subclasses = allow_subclasses

    def _get_all_candidates(self):
        if self.allow_subclasses:
            return itertools.chain.from_iterable(
                ([m] + _get_all_subclasses(m) for m in self.candidates)
            )
        else:
            return self.candidates

    def matches(self, field_name, elem):
        for candidate in self._get_all_candidates():
            if candidate._schema.tag_name == elem['tag']:
                return candidate
        return None

    def incorporate_child(self, match_result, old_value, child):
        return match_result(raw_value=child)

    def to_children(self, field_name, value):
        if value is None:
            return []
        else:
            return [value.to_primitive()]


class XmlChildren(XmlChildBase):
    def __init__(
            self,
            candidates: Union['XmlElementModelMeta', List['XmlElementModelMeta']],
            allow_subclasses=False
    ):
        super().__init__(default=list)

        from .model import XmlElementModelMeta

        if isinstance(candidates, XmlElementModelMeta):
            candidates = [candidates]
        self.candidates = candidates
        self.allow_subclasses = allow_subclasses

    def _get_all_candidates(self):
        if self.allow_subclasses:
            return itertools.chain.from_iterable(
                ([m] + _get_all_subclasses(m) for m in self.candidates)
            )
        else:
            return self.candidates

    def matches(self, field_name, elem):
        for candidate in self._get_all_candidates():
            if candidate._schema.tag_name == elem['tag']:
                return candidate
        return None

    def incorporate_child(self, match_result, old_value, child):
        return old_value + [match_result(raw_value=child)]

    def to_children(self, field_name, value):
        return [child.to_primitive() for child in value]


class XmlChildContent(XmlChildBase):
    def __init__(
            self,
            type_: 'XmlBaseType',
            serialized_name=None,
            case_sensitive=False,
            default=Undefined
    ):
        super().__init__(default=default)

        self.type_ = type_
        self.serialized_name = serialized_name
        self.case_sensitive = case_sensitive

    def _attrib_name(self, field_name):
        if self.serialized_name is not None:
            return self.serialized_name
        else:
            return to_upper_camelcase(field_name)

    def matches(self, field_name, elem):
        field_name = self._attrib_name(field_name)
        if not self.case_sensitive:
            field_name = field_name.lower()
            tag_name = elem['tag'].lower()
        else:
            tag_name = elem['tag']
        return field_name == tag_name

    def incorporate_child(self, match_result, old_value, child):
        return self.type_.to_native(child['text'])

    def to_children(self, field_name, value):
        if value is None:
            return []
        else:
            return [{
                'tag': self._attrib_name(field_name),
                'attrib': {},
                'children': [],
                'text': self.type_.to_primitive(value)
            }]


class XmlBooleanChild(XmlChildBase):
    def __init__(
            self,
            serialized_name=None,
            case_sensitive=False
    ):
        super().__init__(default=False)

        self.serialized_name = serialized_name
        self.case_sensitive = case_sensitive

    def _attrib_name(self, field_name):
        if self.serialized_name is not None:
            return self.serialized_name
        else:
            return to_upper_camelcase(field_name)

    def matches(self, field_name, elem):
        field_name = self._attrib_name(field_name)
        if not self.case_sensitive:
            field_name = field_name.lower()
            tag_name = elem['tag'].lower()
        else:
            tag_name = elem['tag']
        return field_name == tag_name

    def incorporate_child(self, match_result, old_value, child):
        return True

    def to_children(self, field_name, value):
        if value:
            return [{
                'tag': self._attrib_name(field_name),
                'attrib': {},
                'children': [],
                'text': None
            }]
        else:
            return []


class XmlChildrenContent(XmlChildBase):
    def __init__(
            self,
            type_: 'XmlBaseType',
            serialized_name=None,
            case_sensitive=False
    ):
        super().__init__(default=list)

        self.type_ = type_
        self.serialized_name = serialized_name
        self.case_sensitive = case_sensitive

    def _attrib_name(self, field_name):
        if self.serialized_name is not None:
            return self.serialized_name
        else:
            return to_upper_camelcase(field_name)

    def matches(self, field_name, elem):
        field_name = self._attrib_name(field_name)
        if not self.case_sensitive:
            field_name = field_name.lower()
            tag_name = elem['tag'].lower()
        else:
            tag_name = elem['tag']
        return field_name == tag_name

    def incorporate_child(self, match_result, old_value, child):
        return old_value + [self.type_.to_native(child['text'])]

    def to_children(self, field_name, value):
        tag = self._attrib_name(field_name)
        return [{
            'tag': tag,
            'attrib': {},
            'children': [],
            'text': self.type_.to_primitive(child)
        } for child in value]


class XmlNestedChildList(XmlChildBase):
    def __init__(
            self,
            candidates: Union['XmlElementModelMeta', List['XmlElementModelMeta']],
            allow_subclasses=False,
            serialized_name=None,
            case_sensitive=False
    ):
        super().__init__(default=list)

        from .model import XmlElementModelMeta

        if isinstance(candidates, XmlElementModelMeta):
            candidates = [candidates]
        self.candidates = candidates
        self.allow_subclasses = allow_subclasses
        self.serialized_name = serialized_name
        self.case_sensitive = case_sensitive

    def _attrib_name(self, field_name):
        if self.serialized_name is not None:
            return self.serialized_name
        else:
            return to_upper_camelcase(field_name)

    def _get_all_candidates(self):
        if self.allow_subclasses:
            return itertools.chain.from_iterable(
                ([m] + _get_all_subclasses(m) for m in self.candidates)
            )
        else:
            return self.candidates

    def matches(self, field_name, elem):
        field_name = self._attrib_name(field_name)
        if not self.case_sensitive:
            field_name = field_name.lower()
            tag_name = elem['tag'].lower()
        else:
            tag_name = elem['tag']
        return field_name == tag_name

    def _matches_child(self, elem):
        for candidate in self._get_all_candidates():
            if candidate._schema.tag_name == elem['tag']:
                return candidate
        return None

    def incorporate_child(self, match_result, old_value, child):
        children = child.get('children', [])
        result = []
        for c in children:
            child_match = self._matches_child(c)
            if child_match:
                result.append(child_match(raw_value=c))
        return result

    def to_children(self, field_name, value):
        return [{
            'tag': self._attrib_name(field_name),
            'attrib': {},
            'children': [child.to_primitive() for child in value],
            'text': None
        }]
