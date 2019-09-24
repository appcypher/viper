"""
Contains some of the legal characters, tokens and keywords allowed by the
Lexer
"""


def is_keyword(token):
    return (
        token == "False"
        or token == "None"
        or token == "True"
        or token == "and"
        or token == "as"
        or token == "assert"
        or token == "async"
        or token == "await"
        or token == "break"
        or token == "class"
        or token == "continue"
        or token == "def"
        or token == "del"
        or token == "elif"
        or token == "else"
        or token == "except"
        or token == "finally"
        or token == "for"
        or token == "from"
        or token == "global"
        or token == "if"
        or token == "import"
        or token == "in"
        or token == "is"
        or token == "lambda"
        or token == "nonlocal"
        or token == "not"
        or token == "or"
        or token == "pass"
        or token == "raise"
        or token == "return"
        or token == "try"
        or token == "while"
        or token == "with"
        or token == "yield"
        or token == "const"
        or token == "ref"
        or token == "ptr"
        or token == "val"
        or token == "match"
        or token == "let"
        or token == "var"
        or token == "enum"
        or token == "true"
        or token == "false"
        or token == "interface"
        or token == "where"
        or token == "macro"
        or token == "typealias"
    )


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


def is_identifier_start(char):
    """
    TODO: Check if a character is of the following Unicode categories:
        Lu, Ll, Lt, Lm, Lo, Nl, _

    https://unicode.org/reports/tr15/#Introduction
    """
    codepoint = ord(char)
    # Currently [A-Za-z_]
    return (64 < codepoint < 91) or (char == "_") or (96 < codepoint < 123)


def is_identifier_continuation(char):
    """
    TODO: Check if a character is of the following Unicode categories:
        Lu, Ll, Lt, Lm, Lo, Nl, Mn, Mc, Nd, Pc, _

    https://unicode.org/reports/tr15/#Introduction
    """
    codepoint = ord(char)
    # Currently [A-Za-z0-9_]
    return is_identifier_start(char) or (47 < codepoint < 58)


def is_single_char_operator(char):
    return (
        char == "+"
        or char == "-"
        or char == "*"
        # or char == "**"
        or char == "/"
        # or char == "//"
        or char == "%"
        # or char == "@"
        # or char == "<<"
        # or char == ">>"
        or char == "&"
        or char == "|"
        or char == "^"
        or char == "~"
        or char == "<"
        or char == ">"
        # or char == "<="
        # or char == ">="
        # or char == "=="
        # or char == "!="
        or char == "²"
        or char == "√"
    )


def is_single_char_delimiter(char):
    return (
        char == "("
        or char == ")"
        or char == "["
        or char == "]"
        or char == "{"
        or char == "}"
        or char == ","
        or char == ":"
        or char == "."
        or char == ";"
        or char == "@"
        or char == "="
        # or char == "->"
        # or char == "+="
        # or char == "-="
        # or char == "*="
        # or char == "/="
        # or char == "//="
        # or char == "%="
        # or char == "@="
        # or char == "&="
        # or char == "|="
        # or char == "^="
        # or char == ">>="
        # or char == "<<="
        # or char == "**="
    )
