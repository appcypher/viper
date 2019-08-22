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

    def is_hex_digit(codepoint):
        return 47 < codepoint < 58 or 64 < codepoint < 71 or 96 < codepoint < 103

    def is_bin_digit(codepoint):
        return 47 < codepoint < 50

    def is_oct_digit(codepoint):
        return 47 < codepoint < 56

    def is_dec_digit(codepoint):
        return 47 < codepoint < 58

    def is_Lu(codepoint):
        pass

    def is_horizontal_space(char):
        """
        TODO: Support Unicode horizontal spaces

        https://en.wikipedia.org/wiki/Template:Whitespace_(Unicode)
        """
        return char == " " or char == "\t"

    def is_space(char):
        """
        TODO: Support Unicode spaces

        https://en.wikipedia.org/wiki/Template:Whitespace_(Unicode)
        """
        return char == " " or char == "\t" or char == "\n" or char == "\r"

    def is_newline(codepoint):
        pass

    def is_identifier_start(char):
        """
        TODO: Check if a character is of the following Unicode categories:
            Lu, Ll, Lt, Lm, Lo, Nl, _

        https://unicode.org/reports/tr15/#Introduction
        """
        codepoint = ord(char)
        # Currently [A-Za-z_]
        return (64 < codepoint < 91) or (char == '_') or (96 < codepoint < 123)

    def is_identifier_continuation(char):
        """
        TODO: Check if a character is of the following Unicode categories:
            Lu, Ll, Lt, Lm, Lo, Nl, Mn, Mc, Nd, Pc, _

        https://unicode.org/reports/tr15/#Introduction
        """
        codepoint = ord(char)
        # Currently [A-Za-z0-9_]
        return Valids.is_identifier_start(char) or (47 < codepoint < 58)
