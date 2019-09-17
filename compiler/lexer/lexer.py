"""
An implementation of Viper's tokenizer

NOTE:
    May turn lex function into a generator in the future to support generating tokens on demand.

    As noted¹ by some, certain lexer errors may be caused by invalid syntax, but the lexer error
    shows first because it comes before the parser.

    In addition to lex function becoming a generator, may also change Parser.code to an generator
    to be gotten on demand.

    This has the benefit of not keeping everything in memory in case of lex / parse becomes
    unsuccessful.

    1. https://medium.com/@gvanrossum_83706/building-a-peg-parser-d4869b5958fb#2a80
"""

from enum import Enum
from .valid import Valid


class Indentation:
    """
    This class holds top-level indentation information as well as indentation information of code in
    brackets
    """

    def __init__(self, open_bracket=None, start_indentation_count=0):
        self.open_bracket = open_bracket
        self.close_bracket = (
            ")"
            if open_bracket == "("
            else (
                "]" if open_bracket == "[" else ("}" if open_bracket == "{" else None)
            )
        )
        self.indentation_count = start_indentation_count
        self.block = None

    def __repr__(self):
        return (
            f'Indentation(open_bracket="{self.open_bracket}", close_bracket="{self.close_bracket}"'
            f", indentation_count={self.indentation_count}, block={self.block})"
        )


class Block:
    """
    This represents a block of code introduced by a colon and an indent within brackets.
    A block can be the body content of a lambda or a match expression.
    """

    def __init__(self, start_indentation_count):
        self.start_indentation_count = start_indentation_count

    def __repr__(self):
        return (
            f'Block(start_indentation_count={self.start_indentation_count})'
        )


class Token:
    """ Token is a unit extracted """

    def __init__(self, data, kind, row, column):
        self.data = data
        self.kind = kind
        self.row = row
        self.column = column

    def __repr__(self):
        return (
            f'Token(data="{self.data}", kind={self.kind}, row={self.row}'
            f", column={self.column})"
        )

    def __eq__(self, other):
        return (
            self.data == other.data
            and self.kind == other.kind
            and self.row == other.row
            and self.column == other.column
        )


class TokenKind(Enum):
    """
    The different kinds of token
    """

    IDENTIFIER = 0
    NEWLINE = 1
    DEC_FLOAT = 2
    DEC_FLOAT_IMAG = 3
    INDENT = 4
    DEDENT = 5
    PREFIXED_STRING = 6
    BYTE_STRING = 7
    STRING = 8
    DEC_INTEGER = 9
    DEC_INTEGER_IMAG = 10
    BIN_INTEGER = 11
    OCT_INTEGER = 12
    HEX_INTEGER = 13
    OPERATOR = 14
    DELIMITER = 15
    KEYWORD = 16


class IndentSpaceKind(Enum):
    """ The kind of space of a code's indentation """

    UNKNOWN = 0
    SPACE = 1
    TAB = 2


class LexerError(Exception):
    """ Represents the error the lexer can raise """

    def __init__(self, message, row, column):
        super().__init__(f"(line: {row}, col: {column}) {message}")
        self.message = message  # Added because it is missing after super init
        self.row = row
        self.column = column

    def __repr__(self):
        return (
            f'LexerError(message="{self.message}", row={self.row}'
            f", column={self.column})"
        )


class Lexer:
    """
    Takes a UTF-8 encoded file and tries to tokenize it following Viper's grammmar.

    TODO: Normalize (using NFKC normalization form) the codepoints
    """

    def __init__(self, code):
        self.code = code
        self.code_length = len(code)
        self.cursor = -1
        self.row = 0
        self.column = -1
        self.indentations = [Indentation()]
        self.indent_factor = -1
        self.is_in_brackets = False
        self.indent_space_type = IndentSpaceKind.UNKNOWN

    def vomit_char(self):
        """
        Uncosumes an already consumed character
        """
        if self.cursor - 1 > 0:
            self.cursor -= 1
            self.column -= 1
            char = self.code[self.cursor]
            return char

        return None

    def eat_char(self):
        """
        Returns the next character in code and advances the cursor
        position
        """
        if self.cursor + 1 < self.code_length:
            self.cursor += 1
            self.column += 1
            char = self.code[self.cursor]

            # Register row if character is a newline
            if char == "\r":
                if self.code[self.cursor + 1 : self.cursor + 2] == "\n":
                    self.cursor += 1
                self.column = -1
                self.row += 1

            elif char == "\n":
                self.column = -1
                self.row += 1

            return char

        return None

    def eat_token(self, test_token):
        """
        Checks if the next sequence of bytes in code is *test_token*
        """
        length = len(test_token)
        start = self.cursor + 1
        end = start + length

        if end <= self.code_length and test_token == self.code[start:end]:
            self.cursor += length
            self.column += length
            return test_token

        return None

    def peek_char(self, offset=1):
        """ Peeks at the next character in code """
        if -1 < self.cursor + offset < self.code_length:
            return self.code[self.cursor + offset]

        return None

    def peek_token(self, start, end):
        """ Peeks at the token in code """
        if (self.cursor + start >= self.cursor) and (
            self.cursor + end <= self.code_length
        ):
            return self.code[self.cursor + start : self.cursor + end]

        return None

    def peek_slice(self, start, end):
        """ Peeks at the token in code """
        return self.code[self.cursor + start : self.cursor + end]

    def get_line_info(self):
        return self.row, self.column

    def get_numeric_prefix(self, token_kind):
        prefix = ""
        if token_kind == TokenKind.BIN_INTEGER:
            prefix = "0b"
        elif token_kind == TokenKind.OCT_INTEGER:
            prefix = "0o"
        elif token_kind == TokenKind.HEX_INTEGER:
            prefix = "0x"
        return prefix

    def lex(self):
        """ Breaks code string into tokens that the parser can digest """
        char = self.eat_char()
        tokens = []

        # Loops through each character in the code.
        # NOTE: An if branch or a lexer function must not consume more than its production, i.e.
        # it must not consume a char meant for the next lexing iteration
        while char:
            # We check each character in the code and categorize it
            if char == "\r" or char == "\n":
                """
                ========= NEWLINE | INDENT | DEDENT =========

                NOTE: '\r\n' is handled by eat_char method.
                """

                # Checking for indentation.
                space_count = 0
                has_mixed_space_types = False
                prev_space = ''

                # Consume all spaces.
                while Valid.is_horizontal_space(self.peek_char()):
                    cur_space = self.eat_char()

                    # Checking if different space types were mixed.
                    if space_count > 0 and (prev_space != cur_space):
                        has_mixed_space_types = True

                    prev_space = cur_space
                    space_count += 1

                peek_char = self.peek_char()

                # If not followed by another newline, then it is a valid indentation.
                if not (peek_char == "\r" or peek_char == "\n"):
                    if has_mixed_space_types:
                        raise LexerError(
                            "Unexpected mix of different types of spaces in indentation",
                            *self.get_line_info()
                        )

                    indent_space_type = self.indent_space_type

                    if prev_space and (
                        (indent_space_type == IndentSpaceKind.SPACE and prev_space != ' ') or
                        (indent_space_type == IndentSpaceKind.TAB and prev_space != '\t')
                    ):
                        raise LexerError(
                            "Unexpected mix of different types of spaces in indentation",
                            *self.get_line_info()
                        )

                    indentation = self.indentations[-1]
                    block = indentation.block

                    # Skip indentations when inside brackets except for blocks.
                    if indentation.block or not self.is_in_brackets:
                        # Get difference in indentation.
                        indent_diff = space_count - indentation.indentation_count

                        if indent_diff > 0:  # If there is an indent.
                            if self.indent_factor < 1:
                                """ First indent in code """
                                self.indent_factor = indent_diff
                                self.indent_space_type = (
                                    IndentSpaceKind.SPACE if prev_space == ' ' else
                                    IndentSpaceKind.TAB
                                )
                            else:
                                # Check if there is a consistent single indent.
                                if indent_diff != self.indent_factor:
                                    raise LexerError(
                                        f"Expected an indent of {self.indent_factor} spaces",
                                        *self.get_line_info()
                                    )

                            tokens.append(Token('', TokenKind.INDENT, *self.get_line_info()))

                        elif indent_diff < 0:  # If there is an dedent.
                            positive_indent_diff = abs(indent_diff)

                            # If we are in a block, check if we have reached the end of block
                            if block and space_count <= indentation.block.start_indentation_count:
                                positive_indent_diff = abs(
                                    indentation.indentation_count
                                    - indentation.block.start_indentation_count
                                )
                                indentation.block = None
                            else:
                                # Ensure dedent is a multiple of the indent_factor.
                                if positive_indent_diff % self.indent_factor:
                                    raise LexerError(
                                        "Unexpected number of spaces in dedent",
                                        *self.get_line_info()
                                    )

                            for i in range(positive_indent_diff // self.indent_factor):
                                tokens.append(Token('', TokenKind.DEDENT, *self.get_line_info()))

                        else:  # Samedent
                            tokens.append(Token("", TokenKind.NEWLINE, *self.get_line_info()))

                    # Update indentation count.
                    self.indentations[-1].indentation_count = space_count

                else:  # Not indentation
                    # Skip indenntations and newlines when inside brackets.
                    if not self.is_in_brackets:
                        tokens.append(Token("", TokenKind.NEWLINE, *self.get_line_info()))

            elif char == "#":
                """
                ========= COMMENT =========
                """
                # Skip comments
                char = self.peek_char()

                while char and not (char == "\r" or char == "\n"):
                    self.eat_char()
                    char = self.peek_char()

            elif Valid.is_horizontal_space(char):
                """
                Ignore spaces that aren't at the start of the line.
                """
                while Valid.is_horizontal_space(self.peek_char()):
                    self.eat_char()

            elif char == "\\":
                """
                ========= EXPLICIT LINE JOIN  =========
                """
                char = self.peek_char()

                # If next character is not a newline, not a valid line continuation
                if not (char == "\r" or char == "\n"):
                    raise LexerError(
                        f"Unexpected character after line continuation character: {repr(char)}",
                        *self.get_line_info(),
                    )

                # Consume newline
                self.eat_char()

            elif char == "'":
                """
                ========= SHORT STRING | LONG STRING =========
                """

                if self.peek_token(1, 3) == "''":
                    string = self.lex_string(char + self.eat_token("''"))
                else:
                    string = self.lex_string(char)

                tokens.append(Token(string, TokenKind.STRING, *self.get_line_info()))

            elif char == '"':
                """
                ========= SHORT STRING | LONG STRING =========
                """

                if self.peek_token(1, 3) == '""':
                    string = self.lex_string(char + self.eat_token('""'))
                else:
                    string = self.lex_string(char)

                tokens.append(Token(string, TokenKind.STRING, *self.get_line_info()))

            elif char == ".":
                """
                ========= DELIMITER | FLOAT =========
                """
                char = self.peek_char()
                codepoint = ord(char) if char else -1
                token = "."
                token_kind = TokenKind.DELIMITER

                # "." digits exponent?
                if Valid.is_dec_digit(codepoint):
                    token_kind = TokenKind.DEC_FLOAT

                    token = "0." + self.lex_digit_part(
                        Valid.is_dec_digit, "floating point"
                    )

                    # Check for exponent section
                    peek_token = self.peek_slice(1, 3)
                    peek_e = peek_token[0:1]
                    peek_sign_or_digit = peek_token[1:2]
                    codepoint = ord(peek_sign_or_digit) if peek_sign_or_digit else -1

                    if peek_e == "e" and (
                        Valid.is_dec_digit(codepoint)
                        or peek_sign_or_digit == "+"
                        or peek_sign_or_digit == "-"
                    ):
                        token += self.lex_exponent_part()

                tokens.append(Token(token, token_kind, *self.get_line_info()))

            elif char == "0":
                """
                ========= INTEGER | FLOAT =========

                TODO: validate representable integer and float
                """
                token = ""
                token_kind = TokenKind.DEC_INTEGER
                char = self.peek_char()

                if char == "x":
                    # HEXADECIMAL
                    self.eat_char()  # Consume the x
                    token = self.lex_digit_part(Valid.is_hex_digit)
                    token_kind = TokenKind.HEX_INTEGER

                elif char == "b":
                    # BINARY
                    self.eat_char()  # Consume the b
                    token = self.lex_digit_part(Valid.is_bin_digit)
                    token_kind = TokenKind.BIN_INTEGER

                elif char == "o":
                    # OCTAL
                    self.eat_char()  # Consume the o
                    token = self.lex_digit_part(Valid.is_oct_digit)
                    token_kind = TokenKind.OCT_INTEGER

                else:
                    # DECIMAL
                    token = self.lex_digit_part(
                        Valid.is_dec_digit, raise_if_empty=False
                    )
                    token = "0" + token

                    # Check for potential floating point value
                    # digits '.' digits? exponent? | digits exponent
                    peek_token = self.peek_slice(1, 4)
                    peek0 = peek_token[0:1]  # . || e
                    peek1 = peek_token[1:2]  # digit or e || + or - or digit
                    peek2 = peek_token[2:3]  # + or - or digit
                    codepoint0 = ord(peek1) if peek1 else -1
                    codepoint1 = ord(peek2) if peek2 else -1

                    if peek0 == "." and (
                        Valid.is_dec_digit(codepoint0)
                        or (
                            peek1 == "e"
                            and (
                                Valid.is_dec_digit(codepoint1)
                                or peek2 == "+"
                                or peek2 == "-"
                            )
                        )
                    ):
                        token += self.lex_fraction_exponent_part()
                        token_kind = TokenKind.DEC_FLOAT

                    elif peek0 == "e" and (
                        Valid.is_dec_digit(codepoint0) or peek1 == "+" or peek1 == "-"
                    ):
                        token += self.lex_exponent_part()
                        token_kind = TokenKind.DEC_FLOAT

                tokens.append(Token(token, token_kind, *self.get_line_info()))

            elif 47 < ord(char) < 58:
                """
                ========= INTEGER | FLOAT =========

                TODO: Validate representable integer and float
                """
                token = char + self.lex_digit_part(Valid.is_dec_digit, raise_if_empty=False)
                token_kind = TokenKind.DEC_INTEGER

                # Check for potential floating point value
                # digits '.' digits? exponent? | digits exponent
                peek_token = self.peek_slice(1, 4)
                peek0 = peek_token[0:1]  # | . |  e
                peek1 = peek_token[1:2]  # | ε | digit | e |  (+ | - | digit)
                peek2 = peek_token[2:3]  # | (+ | - | digit)
                codepoint0 = ord(peek1) if peek1 else -1
                codepoint1 = ord(peek2) if peek2 else -1

                if peek0 == "." and (
                    Valid.is_dec_digit(codepoint0)
                    or (Valid.is_space(peek1) or peek1 == "")
                    or (
                        peek1 == "e"
                        and (
                            Valid.is_dec_digit(codepoint1)
                            or peek2 == "+"
                            or peek2 == "-"
                        )
                    )
                ):
                    token += self.lex_fraction_exponent_part()
                    token_kind = TokenKind.DEC_FLOAT

                elif peek0 == "e" and (
                    Valid.is_dec_digit(codepoint0) or peek1 == "+" or peek1 == "-"
                ):
                    token += self.lex_exponent_part()
                    token_kind = TokenKind.DEC_FLOAT

                tokens.append(Token(token, token_kind, *self.get_line_info()))

            elif char == "!":
                """
                ========= OPERATOR =========
                """
                token = char
                peek_char = self.peek_char()

                if peek_char != "=":
                    raise LexerError(
                        f"Encountered unexpected character: {repr(char)}",
                        *self.get_line_info(),
                    )
                else:
                    token += self.eat_char()

                tokens.append(Token(token, TokenKind.OPERATOR, *self.get_line_info()))

            elif Valid.is_single_char_operator(char):
                """
                ========= OPERATOR | DELIMITER =========
                """
                token = char
                token_kind = TokenKind.OPERATOR
                peek_char0 = self.peek_char()
                peek_char1 = self.peek_char(2)

                if (
                    peek_char0
                    and peek_char1
                    and (
                        (char == "/" and peek_char0 == "/" and peek_char1 == "=")
                        or (char == ">" and peek_char0 == ">" and peek_char1 == "=")
                        or (char == "<" and peek_char0 == "<" and peek_char1 == "=")
                        or (char == "*" and peek_char0 == "*" and peek_char1 == "=")
                    )
                ):
                    token += self.eat_char() + self.eat_char()
                    token_kind = TokenKind.DELIMITER
                elif peek_char0 and (
                    (char == ">" and (peek_char0 == "=" or peek_char0 == ">"))
                    or (char == "<" and (peek_char0 == "=" or peek_char0 == "<"))
                    or (char == "/" and peek_char0 == "/")
                    or (char == "*" and peek_char0 == "*")
                ):
                    token += self.eat_char()
                elif peek_char0 and (
                    (char == "-" and peek_char0 == ">")
                    or (char == "+" and peek_char0 == "=")
                    or (char == "-" and peek_char0 == "=")
                    or (char == "*" and peek_char0 == "=")
                    or (char == "/" and peek_char0 == "=")
                    or (char == "%" and peek_char0 == "=")
                    or (char == "&" and peek_char0 == "=")
                    or (char == "|" and peek_char0 == "=")
                    or (char == "^" and peek_char0 == "=")
                ):
                    token += self.eat_char()
                    token_kind = TokenKind.DELIMITER

                tokens.append(Token(token, token_kind, *self.get_line_info()))

            elif Valid.is_single_char_delimiter(char):
                """
                ========= DELIMITER | OPERATOR | INDENTATION =========
                """
                token = char
                token_kind = TokenKind.DELIMITER
                peek_char = self.peek_char()
                nested_indentation_num = len(self.indentations)
                indentation = self.indentations[-1]

                # Check if there is an open bracket.
                if char == "(" or char == "[" or char == "{":
                    self.indentations.append(
                        Indentation(
                            open_bracket=char,
                            start_indentation_count=indentation.indentation_count
                        )
                    )

                    self.is_in_brackets = True

                # Check if there is an close bracket.
                if char == indentation.close_bracket:
                    if nested_indentation_num == 2:
                        self.is_in_brackets = False

                    if nested_indentation_num > 1:
                        # If we are in a block and block hasn't been dedented
                        if indentation.block and (
                            indentation.indentation_count
                            > indentation.block.start_indentation_count
                        ):
                            positive_indent_diff = abs(
                                indentation.indentation_count
                                - indentation.block.start_indentation_count
                            )

                            for i in range(positive_indent_diff // self.indent_factor):
                                tokens.append(Token('', TokenKind.DEDENT, *self.get_line_info()))

                        self.indentations.pop()

                # Detecting a top-level block in brackets
                if self.is_in_brackets and not indentation.block and char == ':':
                    offset = 0
                    is_block = False

                    # Skip all spaces until we find a newline
                    while True:
                        offset += 1
                        peek_char = self.peek_char(offset)

                        if Valid.is_horizontal_space(peek_char):
                            continue
                        elif peek_char == '\n' or peek_char == '\r':
                            is_block = True
                            break
                        else:
                            break

                    if is_block:
                        indentation.block = Block(indentation.indentation_count)

                if char == "=" and peek_char == "=":
                    token += self.eat_char()
                    token_kind = TokenKind.OPERATOR
                elif char == "@" and peek_char == "=":
                    token += self.eat_char()

                tokens.append(Token(token, token_kind, *self.get_line_info()))

            elif Valid.is_identifier_start(char):
                """
                ========= IDENTIFIER | OPERATOR | BYTE STRING | IMAGINARY =========
                ========= PREFIXED STRING | INDENTATION | KEYWORD =========

                TODO: Valid.is_identifier_start must check for ASCII first
                """
                line_info = self.get_line_info()
                line_info_before_identifier_lexing = (line_info[0], line_info[1] - 1)

                token = char
                peek_token = self.peek_slice(0, 3)
                two_letter_prefix = peek_token[:2]
                two_letter_prefix_delim = peek_token[2:3]
                one_letter_prefix = peek_token[:1]
                one_letter_prefix_delim = peek_token[1:2]

                if (two_letter_prefix == "rb" or two_letter_prefix == "rf") and (
                    two_letter_prefix_delim == '"' or two_letter_prefix_delim == "'"
                ):
                    # TWO LETTER STRING PREFIX
                    peek_triple_quote_delimiter = self.peek_token(2, 5)

                    token, token_kind = self.lex_prefixed_string(
                        two_letter_prefix,
                        peek_triple_quote_delimiter,
                        two_letter_prefix == "rb",
                    )

                elif (
                    one_letter_prefix == "f"
                    or one_letter_prefix == "b"
                    or one_letter_prefix == "r"
                    or one_letter_prefix == "u"
                ) and (
                    one_letter_prefix_delim == "'" or one_letter_prefix_delim == '"'
                ):
                    # ONE LETTER STRING PREFIX
                    peek_triple_quote_delimiter = self.peek_token(1, 4)

                    token, token_kind = self.lex_prefixed_string(
                        one_letter_prefix,
                        peek_triple_quote_delimiter,
                        one_letter_prefix == "b",
                    )

                else:
                    # IDENTIFIER
                    next_char = self.peek_char()
                    prev_char = self.peek_char(-1)
                    prev_codepoint = ord(prev_char) if prev_char else -1
                    while next_char and Valid.is_identifier_continuation(next_char):
                        token += self.eat_char()

                        # Peek at the next character in code.
                        next_char = self.peek_char()

                    token_kind = (
                        TokenKind.KEYWORD
                        if Valid.is_keyword(token)
                        else TokenKind.IDENTIFIER
                    )

                    # OPERATOR
                    # If this is a coefficient expression like 2_000fahr or (0b100)num,
                    # insert a `*` operator between the operands.
                    if (
                        prev_char
                        and not Valid.is_space(prev_char)
                        and (Valid.is_hex_digit(prev_codepoint) or prev_char == ")")
                    ):
                        kind, prev_token = tokens[-1].kind, tokens[-1].data

                        # Bin, Oct and Hex integer literals are not allowed to be used in
                        # coefficient literal
                        if (
                            kind == TokenKind.BIN_INTEGER
                            or kind == TokenKind.OCT_INTEGER
                            or kind == TokenKind.HEX_INTEGER
                        ):
                            raise LexerError(
                                f"Encountered invalid coefficient literal: "
                                f"{repr(self.get_numeric_prefix(kind)+ prev_token + token)}",
                                *self.get_line_info(),
                            )

                        if token == "im":  # Mutate previous token
                            prev_token = tokens.pop()
                            token = prev_token.data
                            token_kind = (
                                TokenKind.DEC_INTEGER_IMAG
                                if prev_token.kind == TokenKind.DEC_INTEGER
                                else TokenKind.DEC_FLOAT_IMAG
                            )

                        else:
                            tokens.append(
                                Token(
                                    "*",
                                    TokenKind.OPERATOR,
                                    *line_info_before_identifier_lexing,
                                )
                            )

                tokens.append(Token(token, token_kind, *self.get_line_info()))

            else:
                raise LexerError(
                    f"Encountered unexpected character: {repr(char)}",
                    *self.get_line_info(),
                )

            # Consume the next character in code.
            char = self.eat_char()

        # Checking possible dedents at the end of code
        prev_indent = self.indentations[-1].indentation_count
        if prev_indent > 0:
            for i in range(prev_indent // self.indent_factor):
                tokens.append(Token('', TokenKind.DEDENT, *self.get_line_info()))

        return tokens

    def lex_prefixed_string(self, prefix, triple_quote_delimiter, is_byte_string):
        """
        Checks if the next set of bytes starts a prefixed string

        TODO: Handle escape sequence.
        TODO: Handle string formatting.
        """
        token = ""
        token_kind = TokenKind.PREFIXED_STRING
        single_quote_delimiter = triple_quote_delimiter[:1]

        if triple_quote_delimiter == '"""' or triple_quote_delimiter == "'''":
            self.eat_token(prefix[1:] + triple_quote_delimiter)
            token = self.lex_string(
                triple_quote_delimiter, is_byte_string=is_byte_string
            )

        elif single_quote_delimiter == '"' or single_quote_delimiter == "'":
            self.eat_token(prefix[1:] + single_quote_delimiter)
            token = self.lex_string(
                single_quote_delimiter, is_byte_string=is_byte_string
            )

        if is_byte_string:
            token_kind = TokenKind.BYTE_STRING

        return token, token_kind

    def lex_string(self, delimiter, is_byte_string=False):
        """
        Using provided delimiter, returns the sequence of UTF8 codepoints between
        those delimiters

        TODO: Handle escape sequence.
        """
        is_long_string = delimiter == "'''" or delimiter == '"""'
        token = ""

        # Iterate over next sequence of codepoints and make sanity checks
        while True:
            row, column = self.row, self.column
            char = self.eat_char()

            # Make some necessary sanity checks on codepoint
            if char is None:
                # Check if code abruptly ends
                raise LexerError(
                    "Unexpected end of string. Closing delimiter not found", row, column
                )
            elif is_byte_string and not (-1 < ord(char) < 128):
                # If string is expected to be a byte string, check if character is ASCII
                raise LexerError(
                    f"Encountered unexpected non-ASCII character: {repr(char)}",
                    row,
                    column,
                )
            elif not is_long_string and (char == "\n" or char == "\r"):
                # If string is a short string, check if character isn't a newline character
                # TODO: Handle all ASCII and UTF-8 characters.
                raise LexerError(
                    "Encountered unexpected newline character", row, column
                )

            # Check for closing long_string delimiter
            if is_long_string and (
                char == delimiter[0] and self.eat_token(delimiter[1:])
            ):
                break

            # Check for closing short_string delimiter
            if not is_long_string and char == delimiter:
                break

            token += char

        return token

    def lex_digit_part(self, digit_check, number_type="integer", raise_if_empty=True):
        """
        Consume digits
        """
        char = self.peek_char()
        codepoint = ord(char) if char else -1
        prev_char = ""
        token = ""

        # Iterate over remaining digits.
        while char == "_" or (codepoint and digit_check(codepoint)):
            self.eat_char()
            if prev_char == "_" and char == "_":
                raise LexerError(
                    f"Unexpected consecutive underscores in {number_type} literal",
                    *self.get_line_info(),
                )

            if char != "_":
                token += char

            prev_char = char
            char = self.peek_char()
            codepoint = ord(char) if char else -1

        if prev_char == "_":
            self.vomit_char()

        if raise_if_empty and not token:
            raise LexerError(
                f"Unexpected end of {number_type} literal", *self.get_line_info()
            )

        return token

    def lex_exponent_part(self):
        """
        Gets the exponent part of a float literal
        """
        # e [-+]? digits
        token = self.eat_char()  # Consume e
        char = self.peek_char()

        if char == "+" or char == "-":
            char = self.peek_char(2)
            codepoint = ord(char) if char else -1

            if not char or not Valid.is_dec_digit(codepoint):
                raise LexerError(
                    "Unexpected character in floating point literal",
                    *self.get_line_info(),
                )

            token += self.eat_char()  # Consume + | -

        token += self.lex_digit_part(Valid.is_dec_digit, "floating point")

        return token

    def lex_fraction_exponent_part(self):
        """
        Lexes the digits after a decimal point or exponent

        NOTE: Has the following grammar: '.' digit_part? exponent?
        """
        token = self.eat_char()  # Consume .
        char = self.peek_char()
        codepoint = ord(char) if char else -1

        # Check for digit part after dot
        if Valid.is_dec_digit(codepoint):
            token += self.lex_digit_part(Valid.is_dec_digit, "floating point")
        else:
            token += "0"

        # Check for exponent part
        peek_token = self.peek_slice(1, 3)
        peek_e = peek_token[0:1]
        peek_sign_or_digit = peek_token[1:2]
        codepoint = ord(peek_sign_or_digit) if peek_sign_or_digit else -1

        if peek_e == "e" and (
            Valid.is_dec_digit(codepoint)
            or peek_sign_or_digit == "+"
            or peek_sign_or_digit == "-"
        ):
            token += self.lex_exponent_part()

        return token
