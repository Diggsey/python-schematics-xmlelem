from typing import TYPE_CHECKING

from schematics_xmlelem.mixins import DefaultValueMixin, ModelSpecMixin, OverridableTagNameMixin

if TYPE_CHECKING:
    from schematics_xmlelem.types import XmlBaseType
    from schematics_xmlelem.mixins import ModelSpec


class XmlChildBase(DefaultValueMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def matches(self, field_name, elem):
        raise NotImplementedError()

    def incorporate_child(self, match_result, old_value, child):
        raise NotImplementedError()

    def to_children(self, field_name, value):
        raise NotImplementedError()


class XmlChild(XmlChildBase, ModelSpecMixin):
    def __init__(self, candidates: 'ModelSpec', **kwargs):
        super().__init__(candidates=candidates, **kwargs)

    def matches(self, field_name, elem):
        return self._find_candidate(elem['tag'])

    def incorporate_child(self, match_result, old_value, child):
        return match_result(raw_value=child)

    def to_children(self, field_name, value):
        if value is None:
            return []
        else:
            return [value.to_primitive()]


class XmlChildren(XmlChildBase, ModelSpecMixin):
    def __init__(self, candidates: 'ModelSpec', **kwargs):
        super().__init__(default=list, candidates=candidates, **kwargs)

    def matches(self, field_name, elem):
        return self._find_candidate(elem['tag'])

    def incorporate_child(self, match_result, old_value, child):
        return old_value + [match_result(raw_value=child)]

    def to_children(self, field_name, value):
        return [child.to_primitive() for child in value]


class XmlChildContent(XmlChildBase, OverridableTagNameMixin):
    def __init__(self, type_: 'XmlBaseType', **kwargs):
        super().__init__(**kwargs)
        self.type_ = type_

    def matches(self, field_name, elem):
        return self._compare_name(field_name, elem['tag'])

    def incorporate_child(self, match_result, old_value, child):
        if child['text'] is None:
            return None
        else:
            return self.type_.to_native(child['text'])

    def to_children(self, field_name, value):
        if value is None:
            return []
        else:
            return [{
                'tag': self._get_name(field_name),
                'attrib': {},
                'children': [],
                'text': self.type_.to_primitive(value)
            }]


class XmlBooleanChild(XmlChildBase, OverridableTagNameMixin):
    def __init__(self, **kwargs):
        super().__init__(default=False, **kwargs)

    def matches(self, field_name, elem):
        return self._compare_name(field_name, elem['tag'])

    def incorporate_child(self, match_result, old_value, child):
        return True

    def to_children(self, field_name, value):
        if value:
            return [{
                'tag': self._get_name(field_name),
                'attrib': {},
                'children': [],
                'text': None
            }]
        else:
            return []


class XmlChildrenContent(XmlChildBase, OverridableTagNameMixin):
    def __init__(self, type_: 'XmlBaseType', **kwargs):
        super().__init__(default=list, **kwargs)
        self.type_ = type_

    def matches(self, field_name, elem):
        return self._compare_name(field_name, elem['tag'])

    def incorporate_child(self, match_result, old_value, child):
        if child['text'] is None:
            return old_value + [None]
        else:
            return old_value + [self.type_.to_native(child['text'])]

    def to_children(self, field_name, value):
        tag = self._get_name(field_name)
        return [{
            'tag': tag,
            'attrib': {},
            'children': [],
            'text': self.type_.to_primitive(child)
        } for child in value]


class XmlNestedChildList(XmlChildBase, OverridableTagNameMixin, ModelSpecMixin):
    def __init__(self, candidates: 'ModelSpec', **kwargs):
        super().__init__(default=list, candidates=candidates, **kwargs)

    def matches(self, field_name, elem):
        return self._compare_name(field_name, elem['tag'])

    def incorporate_child(self, match_result, old_value, child):
        grand_children = child.get('children', [])
        result = []
        for grand_child in grand_children:
            grand_child_match = self._find_candidate(grand_child['tag'])
            if grand_child_match is not None:
                result.append(grand_child_match(raw_value=grand_child))
        return result

    def to_children(self, field_name, value):
        return [{
            'tag': self._get_name(field_name),
            'attrib': {},
            'children': [child.to_primitive() for child in value],
            'text': None
        }]
