class Valids:
    """
    Contains some of the legal characters, tokens and keywords allowed by the
    Lexer
    """

    keywords = [
        "False",
        "None",
        "True",
        "and",
        "as",
        "assert",
        "async",
        "await",
        "break",
        "class",
        "continue",
        "def",
        "del",
        "elif",
        "else",
        "except",
        "finally",
        "for",
        "from",
        "global",
        "if",
        "import",
        "in",
        "is",
        "lambda",
        "nonlocal",
        "not",
        "or",
        "pass",
        "raise",
        "return",
        "try",
        "while",
        "with",
        "yield",
        "const",
        "ref",
        "ptr",
        "val",
        "match",
        "let",
        "var",
        "enum",
        "true",
        "false",
        "interface",
        "where",
        "macro",
        "typealias",
    ]

    def is_Lu(codepoint):
        pass

    def is_identifier_start(codepoint):
        """
        TODO: Check if a character is of the following Unicode categories:
            Lu, Ll, Lt, Lm, Lo, Nl, _

        https://unicode.org/reports/tr15/#Introduction
        """
        num = ord(codepoint)
        # [A-Za-z_]
        return (64 < num < 91) or (96 < num < 123) or (codepoint == "_")

    def is_identifier_remainder(codepoint):
        """
        TODO: Check if a character is of the following Unicode categories:
            Lu, Ll, Lt, Lm, Lo, Nl, Mn, Mc, Nd, Pc, _
            
        https://unicode.org/reports/tr15/#Introduction
        """
        num = ord(codepoint)
        return Valids.is_identifier_start(codepoint) or (47 < num < 58)
