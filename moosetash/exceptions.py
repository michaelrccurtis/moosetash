"""Moosetash Exceptions"""


class MustacheSyntaxError(Exception):
    """Error during parsing template"""

    @classmethod
    def from_template_pointer(cls, msg: str, template: str, pointer: int):
        """Create syntax error with positional information"""

        line_number = template[:pointer].count('\n') + 1
        return cls(msg.format(line_number=line_number))


class ContextAccessError(Exception):
    """Error getting a variable from context"""


class MissingVariable(Exception):
    """Variable is missing from context"""


class MissingPartial(Exception):
    """Partial is missing from partials dictionary"""
