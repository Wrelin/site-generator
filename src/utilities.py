import re

from textnode import TextType
from textnode import TextNode
from leafnode import LeafNode
from blocktype import BlockType
from blocktype import block_to_block_type
from parentnode import ParentNode
from filework import get_file_content
from filework import get_markdown_paths
from filework import write_file


def text_node_to_html_node(text_node):
    match text_node.text_type:
        case TextType.TEXT:
            return LeafNode(None, text_node.text.replace("  ", " "))
        case TextType.BOLD:
            return LeafNode("b", text_node.text)
        case TextType.ITALIC:
            return LeafNode("i", text_node.text)
        case TextType.CODE:
            return LeafNode("code", text_node.text)
        case TextType.LINK:
            return LeafNode("a", text_node.text, {"href": text_node.url})
        case TextType.IMAGE:
            return LeafNode("img", None, {"src": text_node.url, "alt": text_node.text})

    raise Exception("Undefined text type")


def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type is not TextType.TEXT:
            new_nodes.append(old_node)
            continue

        split_nodes = []
        sections = old_node.text.split(delimiter)

        if len(sections) % 2 == 0:
            raise ValueError("invalid markdown, formatted section not closed")
        for i in range(len(sections)):
            if sections[i] == "":
                continue
            if i % 2 == 0:
                split_nodes.append(TextNode(sections[i], TextType.TEXT))
            else:
                split_nodes.append(TextNode(sections[i], text_type))
        new_nodes.extend(split_nodes)

    return new_nodes


def extract_markdown_images(text):
    pattern = r"!\[([^\[\]]*)\]\(([^\(\)]*)\)"
    matches = re.findall(pattern, text)
    return matches


def extract_markdown_links(text):
    pattern = r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)"
    matches = re.findall(pattern, text)

    return matches


def split_nodes_image(old_nodes):
    return split_nodes_image_or_links(old_nodes, 'image')


def split_nodes_link(old_nodes):
    return split_nodes_image_or_links(old_nodes, 'link')


def split_nodes_image_or_links(old_nodes, mode):
    if mode == 'link':
        extract_fn = extract_markdown_links
        pattern_str = "[{text}]({link})"
        node_type = TextType.LINK
    else:
        extract_fn = extract_markdown_images
        pattern_str = "![{text}]({link})"
        node_type = TextType.IMAGE

    new_nodes = []
    for node in old_nodes:
        pairs = extract_fn(node.text)
        if not pairs:
            new_nodes.append(node)
            continue

        text = node.text
        for pair in pairs:
            sub_pair = text.split(pattern_str.replace("{text}", pair[0]).replace("{link}", pair[1]), 1)

            if len(sub_pair) > 1:
                text = sub_pair[1]
            else:
                text = ""

            if sub_pair[0]:
                new_nodes.append(TextNode(sub_pair[0], node.text_type))

            new_nodes.append(TextNode(pair[0], node_type, pair[1]))

        if text:
            new_nodes.append(TextNode(text, node.text_type))

    return new_nodes


def text_to_textnodes(text):
    nodes = [TextNode(text, TextType.TEXT)]
    nodes = split_nodes_delimiter(nodes, "```", TextType.CODE)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)

    return nodes


def markdown_to_blocks(markdown):
    blocks = markdown.split("\n\n")
    blocks = map(lambda block: block.strip(), blocks)
    return list(filter(lambda block: bool(block), blocks))


def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    children = []
    for block in blocks:
        html_node = block_to_html_node(block)
        children.append(html_node)
    return ParentNode("div", children, None)


def block_to_html_node(block):
    block_type = block_to_block_type(block)
    if block_type == BlockType.PARAGRAPH:
        return paragraph_to_html_node(block)
    if block_type == BlockType.HEADING:
        return heading_to_html_node(block)
    if block_type == BlockType.CODE:
        return code_to_html_node(block)
    if block_type == BlockType.ORDERED_LIST:
        return olist_to_html_node(block)
    if block_type == BlockType.UNORDERED_LIST:
        return ulist_to_html_node(block)
    if block_type == BlockType.QUOTE:
        return quote_to_html_node(block)
    raise ValueError("invalid block type")


def text_to_children(text):
    text_nodes = text_to_textnodes(text)
    children = []
    for text_node in text_nodes:
        html_node = text_node_to_html_node(text_node)
        children.append(html_node)
    return children


def paragraph_to_html_node(block):
    lines = block.split("\n")
    paragraph = " ".join(lines)
    children = text_to_children(paragraph)
    return ParentNode("p", children)


def heading_to_html_node(block):
    level = 0
    for char in block:
        if char == "#":
            level += 1
        else:
            break
    if level + 1 >= len(block):
        raise ValueError(f"invalid heading level: {level}")
    text = block[level + 1 :]
    children = text_to_children(text)
    return ParentNode(f"h{level}", children)


def code_to_html_node(block):
    if not block.startswith("```") or not block.endswith("```"):
        raise ValueError("invalid code block")
    text = block[4:-3]
    raw_text_node = TextNode(text, TextType.TEXT)
    child = text_node_to_html_node(raw_text_node)
    code = ParentNode("code", [child])
    return ParentNode("pre", [code])


def olist_to_html_node(block):
    items = block.split("\n")
    html_items = []
    for item in items:
        text = item[3:]
        children = text_to_children(text)
        html_items.append(ParentNode("li", children))
    return ParentNode("ol", html_items)


def ulist_to_html_node(block):
    items = block.split("\n")
    html_items = []
    for item in items:
        text = item[2:]
        children = text_to_children(text)
        html_items.append(ParentNode("li", children))
    return ParentNode("ul", html_items)


def quote_to_html_node(block):
    lines = block.split("\n")
    new_lines = []
    for line in lines:
        if not line.startswith(">"):
            raise ValueError("invalid quote block")
        new_lines.append(line.lstrip(">").strip())
    content = " ".join(new_lines)
    children = text_to_children(content)
    return ParentNode("blockquote", children)


def extract_title(markdown):
    lines = markdown.split("\n")
    for line in lines:
        line = line.strip()
        if line.startswith("# "):
            return line.lstrip("# ")

    raise Exception("there must be h1 header in markdown")


def generate_page(from_path, template_path, dest_path, basepath):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")

    markdown = get_file_content(from_path)
    template = get_file_content(template_path)

    content = markdown_to_html_node(markdown).to_html()
    title = extract_title(markdown)

    html = template.replace("{{ Title }}", title).replace("{{ Content }}", content)
    html = html.replace('href="/', f'href="{basepath}').replace('src="/', f'src="{basepath}')
    write_file(dest_path, html)

def generate_pages_recursive(dir_path_content, template_path, dest_dir_path, basepath):
    content_paths = get_markdown_paths(dir_path_content)
    dest_paths = [path.replace(dir_path_content, dest_dir_path, 1).replace('.md', '.html') for path in content_paths]

    for i in range(0, len(content_paths)):
        generate_page(content_paths[i], template_path, dest_paths[i], basepath)
