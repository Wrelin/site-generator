from htmlnode import HTMLNode


class ParentNode(HTMLNode):
    def __init__(self, tag, children, props=None):
        super().__init__(tag, None, children, props)

    def to_html(self):
        if not self.tag:
            raise ValueError("parent must have tag")

        if not self.children:
            raise ValueError("parent must have children")

        html_children = ''.join(map(lambda child: child.to_html(), self.children))
        html_props = self.props_to_html()

        return f"<{self.tag}{html_props}>{html_children}</{self.tag}>"
