""" Contains Viper's lexer implementation """

from enum import Enum
from valids import Valids


class Indentation:
    """ Contains a lexer's indentation information """

    def __init__(self):
        self.indent_count = 0
        self.is_space = True
        self.indent_factor = 4


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
    DEC_FLOAT = 3
    INDENT = 4
    DEDENT = 5
    PREFIXED_STRING = 6
    BYTE_STRING = 7
    STRING = 8
    DEC_INTEGER = 9
    BIN_INTEGER = 10
    OCT_INTEGER = 11
    HEX_INTEGER = 12
    OPERATOR = 13
    DELIMITER = 14
    DOT = 15


class LexerError(Exception):
    """ Represents the error the lexer can raise """

    def __init__(self, message, row, column):
        super().__init__(message)
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
        self.indentation = Indentation()

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
                ========= NEWLINE =========

                NOTE: \r\n is handled by eat_char method.
                """
                tokens.append(Token("", TokenKind.NEWLINE, *self.get_line_info()))

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
                ========= DOT | FLOAT =========
                """
                char = self.peek_char()
                codepoint = ord(char) if char else -1
                token = "."
                token_kind = TokenKind.DOT

                # TODO: Abstract out (fraction exponent)
                # "." digits exponent?
                if Valids.is_dec_digit(codepoint):
                    token_kind = TokenKind.DEC_FLOAT

                    token = "0." + self.lex_digit_part(
                        Valids.is_dec_digit, "floating point"
                    )

                    # Check for exponent section
                    peek_token = self.peek_slice(1, 3)
                    peek_e = peek_token[0:1]
                    peek_sign_or_digit = peek_token[1:2]
                    codepoint = ord(peek_sign_or_digit) if peek_sign_or_digit else -1

                    if peek_e == "e" and (
                        Valids.is_dec_digit(codepoint)
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
                    token = self.lex_digit_part(Valids.is_hex_digit)
                    token_kind = TokenKind.HEX_INTEGER

                elif char == "b":
                    # BINARY
                    self.eat_char()  # Consume the b
                    token = self.lex_digit_part(Valids.is_bin_digit)
                    token_kind = TokenKind.BIN_INTEGER

                elif char == "o":
                    # OCTAL
                    self.eat_char()  # Consume the o
                    token = self.lex_digit_part(Valids.is_oct_digit)
                    token_kind = TokenKind.OCT_INTEGER

                else:
                    # DECIMAL
                    token = self.lex_digit_part(
                        Valids.is_dec_digit, raise_if_empty=False
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
                        Valids.is_dec_digit(codepoint0)
                        or (
                            peek1 == "e"
                            and (
                                Valids.is_dec_digit(codepoint1)
                                or peek2 == "+"
                                or peek2 == "-"
                            )
                        )
                    ):
                        token += self.lex_fraction_exponent_part()
                        token_kind = TokenKind.DEC_FLOAT

                    elif peek0 == "e" and (
                        Valids.is_dec_digit(codepoint0) or peek1 == "+" or peek1 == "-"
                    ):
                        token += self.lex_exponent_part()
                        token_kind = TokenKind.DEC_FLOAT

                tokens.append(Token(token, token_kind, *self.get_line_info()))

            elif 47 < ord(char) < 58:
                """
                ========= INTEGER | FLOAT =========

                TODO: Validate representable integer and float
                """
                token = self.lex_digit_part(Valids.is_dec_digit)
                token = char + (token if token else "")
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
                    Valids.is_dec_digit(codepoint0)
                    or (Valids.is_space(peek1) or peek1 == "")
                    or (
                        peek1 == "e"
                        and (
                            Valids.is_dec_digit(codepoint1)
                            or peek2 == "+"
                            or peek2 == "-"
                        )
                    )
                ):
                    token += self.lex_fraction_exponent_part()
                    token_kind = TokenKind.DEC_FLOAT

                elif peek0 == "e" and (
                    Valids.is_dec_digit(codepoint0) or peek1 == "+" or peek1 == "-"
                ):
                    token += self.lex_exponent_part()
                    token_kind = TokenKind.DEC_FLOAT

                tokens.append(Token(token, token_kind, *self.get_line_info()))

            elif Valids.is_identifier_start(char):
                """
                ========= IDENTIFIER | OPERATOR | BYTE STRING | PREFIXED STRING =========

                TODO: Valids.is_identifier_start must check for ASCII first
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

                    while next_char and Valids.is_identifier_continuation(next_char):
                        token += self.eat_char()

                        # Peek at the next character in code.
                        next_char = self.peek_char()

                    # OPERATOR
                    # If this is a coefficient expression like 2_000fahr or (0b100)num,
                    # insert a `*` operator between the operands.
                    if (
                        prev_char
                        and not Valids.is_space(prev_char)
                        and (Valids.is_dec_digit(prev_codepoint) or prev_char == ")")
                    ):
                        tokens.append(
                            Token(
                                "*",
                                TokenKind.OPERATOR,
                                *line_info_before_identifier_lexing,
                            )
                        )

                    token_kind = TokenKind.IDENTIFIER

                tokens.append(Token(token, token_kind, *self.get_line_info()))

            else:
                raise LexerError(
                    f"Encountered unexpected character: {repr(char)}",
                    *self.get_line_info(),
                )

            # Consume the next character in code.
            char = self.eat_char()

        return tokens

    def lex_prefixed_string(self, prefix, triple_quote_delimiter, is_byte_string):
        """
        Checks if the next set of bytes starts a prefixed string
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
        TODO: Handle string formatting.
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

        # Checking if we have a valid digit for a start
        if not char or char != "_" and not digit_check(codepoint):
            raise LexerError(
                f"Unexpected end of {number_type} literal", *self.get_line_info()
            )

        # Iterate over remaining digits
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

            if not char or not Valids.is_dec_digit(codepoint):
                raise LexerError(
                    "Unexpected character in floating point literal",
                    *self.get_line_info(),
                )

            token += self.eat_char()  # Consume + | -

        token += self.lex_digit_part(Valids.is_dec_digit, "floating point")

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
        if Valids.is_dec_digit(codepoint):
            token += self.lex_digit_part(Valids.is_dec_digit, "floating point")
        else:
            token += "0"

        # Check for exponent part
        peek_token = self.peek_slice(1, 3)
        peek_e = peek_token[0:1]
        peek_sign_or_digit = peek_token[1:2]
        codepoint = ord(peek_sign_or_digit) if peek_sign_or_digit else -1

        if peek_e == "e" and (
            Valids.is_dec_digit(codepoint)
            or peek_sign_or_digit == "+"
            or peek_sign_or_digit == "-"
        ):
            token += self.lex_exponent_part()

        return token
