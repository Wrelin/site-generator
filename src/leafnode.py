from htmlnode import HTMLNode


class LeafNode(HTMLNode):
    def __init__(self, tag, value, props=None):
        super().__init__(tag, value, None, props)

    def to_html(self):
        if not self.value:
            self.value = ''
            # raise ValueError("leaf must have value")

        if not self.tag:
            return self.value

        html_props = self.props_to_html()

        return f"<{self.tag}{html_props}>{self.value}</{self.tag}>"
