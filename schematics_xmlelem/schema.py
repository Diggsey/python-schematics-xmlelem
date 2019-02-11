
class Schema(object):

    def __init__(self, name, tag_name, model, validators, attributes, children, content):
        self.name = name
        self.tag_name = tag_name
        self.model = model
        self.validators = validators
        self.attributes = attributes
        self.children = children
        self.content = content
