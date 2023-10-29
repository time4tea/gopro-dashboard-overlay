import xml.etree.ElementTree as ET
from functools import wraps
from typing import Set

from .exceptions import Defect

common_attributes = {"name", "type"}


# can wrap a method of class Widget(self, element, ...) or a plain function x(element,...)
def allow_attributes(allowed: Set[str]):
    def decorate(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            element: ET.Element

            if type(args[0]) == ET.Element:
                element = args[0]
            elif type(args[1]) == ET.Element:
                element = args[1]
            else:
                raise Defect("allow_attributes maybe on wrong method?")

            attributes = set(element.attrib.keys())

            extra = attributes - (allowed | common_attributes)
            if extra:
                component_type = element.attrib["type"]
                raise IOError(
                    f"Component '{component_type}' - Unknown attributes '{','.join(extra)}', Allowed are: '{','.join(allowed)}'")

            return f(*args, **kwargs)

        return wrapper

    return decorate
