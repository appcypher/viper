""" Contains Viper's lexer implementation """

from enum import Enum
from valid import ValidTokens


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
    """ The different kinds of token """

    IDENTIFIER = 0
    NEWLINE = 1
    INTEGER_DEC = 2
    FLOAT_DEC = 3
    INDENT = 4
    DEDENT = 5
    PREFIXED_STRING = 6
    STRING = 7


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
    """ Contains the lexer implementation """

    def __init__(self, code):
        self.code = code
        self.code_length = len(code)
        self.cursor = -1
        self.row = 0
        self.column = -1
        self.indentation = Indentation()
        self.valid_tokens = ValidTokens

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

    def get_row_column(self):
        return self.row, self.column

    def is_identifier_start(char):
        """
        TODO: Check if a character is of the following Unicode categories:
            Lu, Ll, Lt, Lm, Lo, Nl, _

        TODO: Normalize (using NFKC normalization form)
        the codepoints

        https://unicode.org/reports/tr15/#Introduction
        """
        num = ord(char)
        # [A-Za-z_]
        return (64 < num < 91) or (96 < num < 123) or (char == "_")

    def is_identifier_remainder(char):
        """
        TODO: Check if a character is of the following Unicode categories:
            Lu, Ll, Lt, Lm, Lo, Nl, Mn, Mc, Nd, Pc, _

        TODO: Normalize (using NFKC normalization form)
        the codepoints

        https://unicode.org/reports/tr15/#Introduction
        """
        num = ord(char)
        return Lexer.is_identifier_start(char) or (47 < num < 58)

    def is_string_prefix_next(
        self, char, one_letter_prefixes=[], two_letter_prefixes=[]
    ):
        """
        Checks and next set of bytes starts a prefixed string
        """
        next_char = self.peek_char()
        next_char2 = self.peek_char(2)
        prefix_data = None
        delimiter_token = None

        one_letter_prefix = char
        two_letter_prefix = (
            char + next_char if char is not None and next_char is not None else None
        )

        if one_letter_prefix in one_letter_prefixes and (
            next_char == '"' or next_char == "'"
        ):
            prefix_data = {"prefix": one_letter_prefix}
            delimiter_token = self.peek_token(1, 4)

        elif two_letter_prefix in two_letter_prefixes and (
            next_char2 == '"' or next_char2 == "'"
        ):
            prefix_data = {"prefix": two_letter_prefix}
            delimiter_token = self.peek_token(2, 5)

        if delimiter_token:
            prefix_data["delim"] = (
                delimiter_token
                if (delimiter_token == '"""') or (delimiter_token == "'''")
                else delimiter_token[0]
            )

        return prefix_data

    def lex(self):
        """ Breaks code string into tokens that the parser can digest """
        char = self.eat_char()
        tokens = []

        # Loops through each character in the code.
        while char:
            prefixed_string = self.is_string_prefix_next(
                char,
                one_letter_prefixes=["r", "u", "R", "U", "f", "F"],
                two_letter_prefixes=["fr", "Fr", "fR", "FR", "rf", "rF", "Rf", "RF"],
            )

            prefixed_byte_string = self.is_string_prefix_next(
                char,
                one_letter_prefixes=["b", "B"],
                two_letter_prefixes=["br", "Br", "bR", "BR", "rb", "rB", "Rb", "RB"],
            )

            # We check each character in the code and categorize it
            if char == "\r" or char == "\n":
                """
                ========= NEWLINE =========

                NOTE: \r\n is handled by eat_char method.
                """
                tokens.append(Token("", TokenKind.NEWLINE, *self.get_row_column()))

            elif prefixed_string:
                """
                ========= PREFIXED STRING =========
                """
                prefix, delimiter = prefixed_string["prefix"], prefixed_string["delim"]

                # Consume delimiter
                self.eat_token((prefix[1:] if len(prefix) > 1 else "") + delimiter)

                # Get the stingf content
                string = self.lex_string(delimiter)

                tokens.append(
                    Token(string, TokenKind.PREFIXED_STRING, *self.get_row_column())
                )

            elif prefixed_byte_string:
                """
                ========= PREFIXED BYTE STRING =========
                """
                prefix, delimiter = (
                    prefixed_byte_string["prefix"],
                    prefixed_byte_string["delim"],
                )

                # Consume delimiter
                self.eat_token((prefix[1:] if len(prefix) > 1 else "") + delimiter)

                # Get the stingf content
                string = self.lex_string(delimiter, is_byte_string=True)

                tokens.append(
                    Token(string, TokenKind.PREFIXED_STRING, *self.get_row_column())
                )

            elif (char == "'" and self.peek_token(1, 3) == "''") or (
                char == '"' and self.peek_token(1, 3) == '""'
            ):
                """
                ========= LONG STRING =========
                """
                string = self.lex_string(char + self.eat_token(char * 2))

                tokens.append(Token(string, TokenKind.STRING, *self.get_row_column()))

            elif char == "'" or char == '"':
                """
                ========= SHORT STRING =========
                """
                string = self.lex_string(char)

                tokens.append(Token(string, TokenKind.STRING, *self.get_row_column()))

            elif Lexer.is_identifier_start(char):
                """
                ========= IDENTIFIER =========
                """
                token = char
                next_char = self.peek_char()

                while next_char and Lexer.is_identifier_remainder(next_char):
                    token += self.eat_char()

                    # Peek at the next character in code.
                    next_char = self.peek_char()

                tokens.append(
                    Token(token, TokenKind.IDENTIFIER, *self.get_row_column())
                )

            else:
                raise LexerError(
                    f"Encountered unexpected character: {repr(char)}",
                    *self.get_row_column(),
                )

            # Consume the next character in code.
            char = self.eat_char()

        return tokens

    def lex_string(self, delimiter, is_byte_string=False):
        """
        Using provided delimiter, returns the sequence of UTF8 codepoints between
        those delimiters

        TODO: Make it UTF8 compliant.
        TODO: Handle escape sequence.
        """
        is_long_string = delimiter == "'''" or delimiter == '"""'
        token = ""

        while True:
            row, column = self.row, self.column
            char = self.eat_char()

            # Make some necessary sanity checks on character
            if char is None:
                raise LexerError(
                    "Unexpected end of string. Closing delimiter not found", row, column
                )
            elif is_byte_string and not (-1 < ord(char) < 128):
                raise LexerError(
                    f"Encountered unexpected non-ASCII character: {repr(char)}", row, column
                )
            elif not is_long_string and (char == "\n" or char == "\r"):
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
