
class Schema(object):

    def __init__(self, name, tag_name, tag_case_sensitive, model, validators, attributes, children, content):
        self.name = name
        self.tag_name = tag_name
        self.tag_case_sensitive = tag_case_sensitive
        self.model = model
        self.validators = validators
        self.attributes = attributes
        self.children = children
        self.content = content

    def compare_tag_name(self, other_name):
        tag_name = self.tag_name
        if not self.tag_case_sensitive:
            tag_name = tag_name.lower()
            other_name = other_name.lower()
        return tag_name == other_name
