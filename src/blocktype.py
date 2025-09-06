from enum import Enum
import re


class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"


def block_to_block_type(block):
    heading_pattern = r"^#{1,6} .+$"
    if re.match(heading_pattern, block):
        return BlockType.HEADING

    parts = block.split("\n")
    if len(parts) > 1 and parts[0].startswith("```") and parts[-1].startswith("```"):
        return BlockType.CODE

    if block.startswith(">"):
        for part in parts:
            if not part.startswith(">"):
                return BlockType.PARAGRAPH
        return BlockType.QUOTE

    if block.startswith("- "):
        for part in parts:
            if not part.startswith("- "):
                return BlockType.PARAGRAPH
        return BlockType.UNORDERED_LIST

    for i in range(0, len(parts)):
        if not parts[i].startswith(f"{i + 1}. "):
            return BlockType.PARAGRAPH

    return BlockType.ORDERED_LIST
