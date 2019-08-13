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
    INTEGER_DEC = 2
    FLOAT_DEC = 3
    INDENT = 4
    DEDENT = 5
    PREFIXED_STRING = 6
    BYTE_STRING = 14
    STRING = 7
    DEC_INTEGER = 8
    BIN_INTEGER = 9
    OCT_INTEGER = 10
    HEX_INTEGER = 11
    OPERATOR = 12
    DELIMITER = 13


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
        if self.cursor + offset < self.code_length:
            return self.code[self.cursor + offset]

        return None

    def peek_token(self, start, end):
        """ Peeks at the next character in code """
        if (self.cursor + start >= self.cursor) and (
            self.cursor + end <= self.code_length
        ):
            return self.code[self.cursor + start : self.cursor + end]

        return None

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

            elif char == "0":
                """
                ========= INTEGER | FLOAT =========
                """
                token = ""
                token_kind = TokenKind.DEC_INTEGER
                char = self.peek_char()

                if char == "x":
                    # HEXADECIMAL
                    self.eat_char()  # Consume the x
                    token = self.lex_digits(47, 58, is_hex=True)
                    token_kind = TokenKind.HEX_INTEGER

                elif char == "b":
                    # BINARY
                    self.eat_char()  # Consume the b
                    token = self.lex_digits(47, 50)
                    token_kind = TokenKind.BIN_INTEGER

                elif char == "o":
                    # OCTAL
                    self.eat_char()  # Consume the o
                    token = self.lex_digits(47, 56)
                    token_kind = TokenKind.OCT_INTEGER

                else:
                    # DECIMAL
                    token = self.lex_digits(47, 58, raise_if_empty=False)
                    token = "0" + token

                tokens.append(Token(token, token_kind, *self.get_line_info()))

            elif 47 < ord(char) < 58:
                """
                ========= INTEGER | FLOAT =========
                """
                token = self.lex_digits(47, 58)
                token = char + (token if token else "")

                tokens.append(
                    Token(token, TokenKind.DEC_INTEGER, *self.get_line_info())
                )

            elif Valids.is_identifier_start(char):
                """
                ========= IDENTIFIER | BYTE STRING | PREFIXED STRING =========

                TODO: Valids.is_identifier_start must check for ASCII first
                """
                token = char
                one_letter_string_prefix = char
                two_letter_string_prefix = self.peek_token(0, 2)
                is_two_letter_prefix_byte_string = two_letter_string_prefix == "rb"

                if is_two_letter_prefix_byte_string or two_letter_string_prefix == "rf":
                    # TWO LETTER STRING PREFIX
                    peek_triple_quote_delimiter = self.peek_token(2, 5)

                    token, token_kind = self.lex_prefixed_string(
                        two_letter_string_prefix,
                        peek_triple_quote_delimiter,
                        is_two_letter_prefix_byte_string,
                    )

                elif (
                    one_letter_string_prefix == "f"
                    or one_letter_string_prefix == "b"
                    or one_letter_string_prefix == "r"
                    or one_letter_string_prefix == "u"
                ):
                    # ONE LETTER STRING PREFIX
                    peek_triple_quote_delimiter = self.peek_token(1, 4)

                    is_byte_string = one_letter_string_prefix == "b"

                    token, token_kind = self.lex_prefixed_string(
                        one_letter_string_prefix,
                        peek_triple_quote_delimiter,
                        is_byte_string,
                    )

                else:
                    # IDENTIFIER
                    next_char = self.peek_char()

                    while next_char and Valids.is_identifier_remainder(next_char):
                        token += self.eat_char()

                        # Peek at the next character in code.
                        next_char = self.peek_char()

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

        if triple_quote_delimiter == '"""' or triple_quote_delimiter == "'''":
            self.eat_token(prefix[1:] + triple_quote_delimiter)
            token = self.lex_string(
                triple_quote_delimiter, is_byte_string=is_byte_string
            )

        elif triple_quote_delimiter[0] == '"' or triple_quote_delimiter[0] == "'":
            self.eat_token(prefix[1:] + triple_quote_delimiter[0])
            token = self.lex_string(
                triple_quote_delimiter[0], is_byte_string=is_byte_string
            )

        if is_byte_string:
            token_kind = TokenKind.BYTE_STRING

        return token, token_kind

    def lex_string(self, delimiter, is_byte_string=False):
        """
        Using provided delimiter, returns the sequence of UTF8 codepoints between
        those delimiters

        TODO: Make it UTF8 compliant.
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

    def lex_digits(self, ascii_low, ascii_hi, is_hex=False, raise_if_empty=True):
        char = self.peek_char()
        codepoint = ord(char) if char else None
        prev_char = ""
        token = ""

        # Checking if we have a valid digit for a start
        if (
            not char
            or char != "_"
            and not (
                codepoint
                and (
                    ascii_low < codepoint < ascii_hi
                    or (is_hex and (64 < codepoint < 71 or 96 < codepoint < 103))
                )
            )
        ):
            raise LexerError("Unexpected end of integer literal", *self.get_line_info())

        while char == "_" or (
            codepoint
            and (
                ascii_low < codepoint < ascii_hi
                or (is_hex and (64 < codepoint < 71 or 96 < codepoint < 103))
            )
        ):
            self.eat_char()
            token += char
            if prev_char == "_" and char == "_":
                raise LexerError(
                    "Unexpected consecutive underscores in integer literal",
                    *self.get_line_info(),
                )

            prev_char = char
            char = self.peek_char()
            codepoint = ord(char) if char else None

        if prev_char == "_":
            raise LexerError(
                "Unexpected trailing underscore in integer literal",
                *self.get_line_info(),
            )

        if raise_if_empty and not token:
            raise LexerError("Unexpected end of integer literal", *self.get_line_info())

        return token.replace("_", "")

    def lex_digit_part(self):
        pass

    def lex_fraction(self):
        pass

    def lex_exponent(self):
        pass
