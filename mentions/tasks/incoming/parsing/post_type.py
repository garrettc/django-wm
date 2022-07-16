from typing import Optional

from bs4 import Tag

from mentions.models.mixins.quotable import IncomingMentionType


def parse_post_type(link: Tag) -> Optional[IncomingMentionType]:
    """Return any available type information in the context of the link.

    This may be available as a class on the link itself, or on a parent element
    that is marked with h-cite."""

    def find_mention_type_in_classlist(element: Tag) -> Optional[IncomingMentionType]:
        if element.has_attr("class"):
            classes = set(element["class"])

            for _type in IncomingMentionType.__members__.values():
                if _type.value in classes:
                    return _type

    link_type = find_mention_type_in_classlist(link)
    if link_type is not None:
        return link_type

    hcite = link.find_parent(class_="h-cite")
    if hcite:
        return find_mention_type_in_classlist(hcite)
