import unittest

from schematics.exceptions import DataError
from src.xmltojson.xmltojson import unparse
from xmltojson import parse

from schematics_xmlelem.attributes import XmlAttribute
from schematics_xmlelem.children import XmlChildContent, XmlChildrenContent, XmlNestedChildList, XmlBooleanChild, \
    XmlChildren
from schematics_xmlelem.content import XmlContent
from schematics_xmlelem.model import XmlElementModel
from schematics_xmlelem.types import XmlIntType, XmlStringType


class Foo(XmlElementModel):
    field1 = XmlAttribute(XmlIntType())
    field2 = XmlAttribute(XmlStringType(choices=['A', 'B']))
    bar = XmlChildContent(XmlStringType())
    baz = XmlChildrenContent(XmlStringType())
    content = XmlContent(XmlStringType())
    check = XmlBooleanChild()
    bar_null1 = XmlChildContent(XmlStringType(), null_value=0, default=None)
    bar_null2 = XmlChildContent(XmlStringType(), null_value=0, default=None)


class Bar(XmlElementModel):
    field1 = XmlAttribute(XmlIntType(), default=None)
    content = XmlContent(XmlStringType())


class Foo2(XmlElementModel):
    bars = XmlNestedChildList(Bar)


class Parent(XmlElementModel):
    pass


class Child1(Parent):
    field1 = XmlAttribute(XmlIntType(), default=None)


class Child2(Parent):
    field2 = XmlAttribute(XmlStringType(), default=None)


class Foo3(XmlElementModel):
    children = XmlChildren(Parent, allow_subclasses=True)


class CaseSensitive(XmlElementModel):
    pass


class CaseInsensitive(XmlElementModel):
    tag_case_sensitive = False


class BasicTestCase(unittest.TestCase):
    def test_model(self):
        input_json = parse(
            '<Foo field1="23" field2="B">'
            '   Some content'
            '   <Bar>Hello!</Bar>'
            '   <Baz>Item1</Baz>'
            '   <Baz>Item2</Baz>'
            '   <Baz>Item3</Baz>'
            '   <Check/>'
            '   <BarNull1/>'
            '</Foo>'
        )

        print(input_json)

        foo = Foo(raw_value=input_json)

        self.assertEqual(foo.field1, 23)
        self.assertEqual(foo.field2, 'B')
        self.assertEqual(foo.bar, 'Hello!')
        self.assertEqual(foo.baz, ['Item1', 'Item2', 'Item3'])
        self.assertEqual(foo.content, 'Some content')
        self.assertEqual(foo.check, True)
        self.assertEqual(foo.bar_null1, 0)
        self.assertIsNone(foo.bar_null2)

    def test_nested_child_list(self):
        input_json = parse(
            '<Foo2>'
            '   <Bars>'
            '       <Bar>Item1</Bar>'
            '       <Bar field1="2">Item2</Bar>'
            '       <Baz>Non-item</Baz>'
            '       <Bar>Item3</Bar>'
            '   </Bars>'
            '</Foo2>'
        )

        print(input_json)

        foo2 = Foo2(raw_value=input_json)

        self.assertEqual(len(foo2.bars), 3)
        self.assertIsNone(foo2.bars[0].field1)
        self.assertEqual(foo2.bars[0].content, 'Item1')
        self.assertEqual(foo2.bars[1].field1, 2)
        self.assertEqual(foo2.bars[1].content, 'Item2')
        self.assertIsNone(foo2.bars[2].field1)
        self.assertEqual(foo2.bars[2].content, 'Item3')

        xml = unparse(foo2.to_primitive())

        self.assertEqual(xml, '<Foo2><Bars><Bar>Item1</Bar><Bar field1="2">Item2</Bar><Bar>Item3</Bar></Bars></Foo2>')

    def test_inheritance(self):
        input_json = parse(
            '<Foo3>'
            '   <Child1 />'
            '   <Child2 field2="hi" />'
            '   <Child1 field1="3" />'
            '   <Parent />'
            '</Foo3>'
        )

        print(input_json)

        foo3 = Foo3(raw_value=input_json)

        self.assertEqual(len(foo3.children), 4)
        self.assertIsInstance(foo3.children[0], Child1)
        self.assertIsInstance(foo3.children[1], Child2)
        self.assertIsInstance(foo3.children[2], Child1)
        self.assertIsInstance(foo3.children[3], Parent)
        self.assertIsNone(foo3.children[0].field1)
        self.assertEqual(foo3.children[1].field2, 'hi')
        self.assertEqual(foo3.children[2].field1, 3)

        xml = unparse(foo3.to_primitive())

        self.assertEqual(xml, '<Foo3><Child1 /><Child2 field2="hi" /><Child1 field1="3" /><Parent /></Foo3>')

    def test_case_sensitive(self):
        input_json_good = parse('<CaseSensitive />')
        input_json_bad = parse('<caSesensiTive />')

        # Should succeed
        case_sensitive_good = CaseSensitive(raw_value=input_json_good)

        with self.assertRaises(DataError):
            CaseInsensitive(raw_value=input_json_bad)

        xml = unparse(case_sensitive_good.to_primitive())

        self.assertEqual(xml, '<CaseSensitive />')

    def test_case_insensitive(self):
        input_json_good = parse('<CaseInsensitive />')
        input_json_bad = parse('<caSeinsensiTive />')

        # Should succeed
        case_insensitive_good = CaseInsensitive(raw_value=input_json_good)

        # Should also succeed
        case_insensitive_bad = CaseInsensitive(raw_value=input_json_bad)

        xml = unparse(case_insensitive_good.to_primitive())
        self.assertEqual(xml, '<CaseInsensitive />')

        xml = unparse(case_insensitive_bad.to_primitive())
        self.assertEqual(xml, '<CaseInsensitive />')
