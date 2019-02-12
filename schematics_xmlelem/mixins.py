import itertools
from typing import Union, TYPE_CHECKING, Iterable

from schematics.undefined import Undefined

from schematics_xmlelem.casing import to_upper_camelcase, to_camelcase

if TYPE_CHECKING:
    from schematics_xmlelem.model import XmlElementModelMeta

    ModelSpec = Union['XmlElementModelMeta', Iterable['XmlElementModelMeta']]


def _get_all_subclasses(cls):
    all_subclasses = []

    for subclass in cls.__subclasses__():
        all_subclasses.append(subclass)
        all_subclasses.extend(_get_all_subclasses(subclass))

    return all_subclasses


class DefaultValueMixin:
    def __init__(self, default=Undefined, **kwargs):
        super().__init__(**kwargs)
        self.default = default

    def from_default(self):
        if callable(self.default):
            return self.default()
        else:
            return self.default


class OverridableNameMixin:
    def __init__(self, serialized_name=None, case_sensitive=False, **kwargs):
        super().__init__(**kwargs)
        self.serialized_name = serialized_name
        self.case_sensitive = case_sensitive

    def _convert_name(self, field_name):
        raise NotImplementedError()

    def _get_name(self, field_name):
        if self.serialized_name is not None:
            return self.serialized_name
        else:
            return self._convert_name(field_name)

    def _compare_name(self, field_name, other_name):
        name = self._get_name(field_name)
        if not self.case_sensitive:
            name = name.lower()
            other_name = other_name.lower()
        return name == other_name


class OverridableTagNameMixin(OverridableNameMixin):
    def _convert_name(self, field_name):
        return to_upper_camelcase(field_name)


class OverridableAttribNameMixin(OverridableNameMixin):
    def _convert_name(self, field_name):
        return to_camelcase(field_name)


class ModelSpecMixin:
    def __init__(self, candidates: 'ModelSpec', allow_subclasses=False, **kwargs):
        super().__init__(**kwargs)

        if not isinstance(candidates, Iterable):
            candidates = [candidates]
        self.candidates = candidates
        self.allow_subclasses = allow_subclasses

    def _get_all_candidates(self) -> Iterable['XmlElementModelMeta']:
        if self.allow_subclasses:
            return itertools.chain.from_iterable(
                ([m] + _get_all_subclasses(m) for m in self.candidates)
            )
        else:
            return self.candidates

    def _find_candidate(self, tag_name):
        for candidate in self._get_all_candidates():
            if candidate._schema.compare_tag_name(tag_name):
                return candidate
        return None
