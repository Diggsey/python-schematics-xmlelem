import unittest

from src.xmltojson.xmltojson import unparse
from xmltojson import parse

from schematics_xmlelem.attributes import XmlAttribute
from schematics_xmlelem.children import XmlChildContent, XmlChildrenContent, XmlNestedChildList, XmlBooleanChild
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


class Bar(XmlElementModel):
    field1 = XmlAttribute(XmlIntType(), default=None)
    content = XmlContent(XmlStringType())


class Foo2(XmlElementModel):
    bars = XmlNestedChildList(Bar)


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
            '</Foo>'
        )

        print(input_json)

        foo = Foo(raw_value=input_json)

        self.assertEqual(foo.field1, 23)
        self.assertEqual(foo.field2, 'B')
        self.assertEqual(foo.bar, 'Hello!')
        self.assertEqual(foo.baz, ['Item1', 'Item2', 'Item3'])
        self.assertEqual(foo.content, '   Some content   ')
        self.assertEqual(foo.check, True)

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
