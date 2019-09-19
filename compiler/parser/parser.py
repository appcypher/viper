"""
A packrat parser for parsing Viper's syntax.
"""
from ..lexer.lexer import TokenKind


class ParserError(Exception):
    """ Represents the error the parser can raise """

    def __init__(self, message, row, column):
        super().__init__(f"(line: {row}, col: {column}) {message}")
        self.message = message  # Added because it is missing after super init
        self.row = row
        self.column = column

    def __repr__(self):
        return (
            f'ParserError(message="{self.message}", row={self.row}'
            f", column={self.column})"
        )


class Parser:
    """
    A recursive descent parser with memoizing feature basically making it a packrat parser.

    It is designed to have the follwing properties:
    - Results of all paths taken are memoized.
    - A parser function result should often be an AST. Avoid returning parse trees as much as
        possible.
    - A parser function result should not hold values, but references to token elements.
    """

    def __init__(self, tokens):
        self.tokens = tokens
        self.tokens_length = len(tokens)
        self.cursor = -1
        self.row = 0
        self.column = -1
        self.cache = {}

    def from_code(code):
        """
        Creates a parser from code.
        """
        from ..lexer.lexer import Lexer

        tokens = Lexer(code).lex()

        return Parser(tokens)

    def get_line_info(self):
        return self.row, self.column

    def backtrackable(parser):
        """
        A decorator that changes the parser state to it's original state before a parser function
        is called and failed (i.e. returns None).
        """

        def wrapper(self, *args):
            # Get important parser state before parsing.
            cursor, row, column = self.cursor, *self.get_line_info()

            parser_result = parser(self, *args)

            # Revert parser state
            if parser_result is None:
                self.cursor = cursor
                self.row = row
                self.column = column

            return parser_result

        return wrapper

    def memoize(parser):
        """
        A decorator that memoizes the result of a recursive decent parser.
        It also reuses cache if available before running the parser.
        """

        def wrapper(self, *args):
            # Get info about parser function.
            cursor = self.cursor
            parser_name = parser.__name__

            # Check cache if parser function result is already saved
            cursor_key = self.cache.get(cursor)

            if cursor_key:
                try:
                    result = cursor_key[parser_name]
                    self.cursor = result[1]
                    return result[0]
                except KeyError:
                    pass

            # Otherwise go ahead and parse, then cache result
            parser_result = parser(self, *args)
            skip = self.cursor

            if not cursor_key:
                self.cache[cursor] = {parser_name: (parser_result, skip)}
            else:
                try:
                    cursor_key[parser_name]
                except KeyError:
                    self.cache[cursor][parser_name] = (parser_result, skip)

            return parser_result

        return wrapper

    def eat_token(self):
        """
        Returns the next token and its index then advances the cursor position
        """
        if self.cursor + 1 < self.tokens_length:
            self.cursor += 1
            token = self.tokens[self.cursor]

            # Update row and column
            self.column = token.column
            self.row = token.row

            return (self.cursor, token)

        return None

    def consume_string(self, string):
        """
        Consumes and checks if the next token index if it matches the string argument.
        """
        if self.cursor + 1 < self.tokens_length:
            token = self.tokens[self.cursor + 1]

            if token.data == string:
                self.cursor += 1
                self.column = token.column
                self.row = token.row

                return self.cursor

        return None

    @backtrackable
    def parse_all(self, *args, ignores=()):
        """
        Takes an arguments of parser and strings (which it calls `consume_string` on) and
        calls them. It fails if any of the parser fails.
        `ignores` referes to the results of args to ingnore
        """

        result = []

        for arg in args:
            # Check if argument is a string or a parser function
            if type(arg) == str:
                parser_result = self.consume_string(arg)
            else:
                parser_result = arg()

            # If parser result isn't okay, break out of loop
            if parser_result is None:
                result = None
                break

            # Skip the results of arguments that are in the `ignores` list
            if arg not in ignores:
                result.append(parser_result)

        return result

    @backtrackable
    def opt_more(self, *args, ignores=()):
        """
        A helper function for (greedily) consuming zero or more tokens based on pattern the
        parsers expect.
        This function corresponds with PEG's `*`.
        """
        result = []

        while True:
            parser_result = self.parse_all(*args, ignores)

            if parser_result is None:
                break

            result.append(parser_result)

        return parser_result

    @backtrackable
    def more(self, *args, ignores=()):
        """
        A helper function for (greedily) consuming one or more tokens based on pattern the
        parsers expect.
        This function corresponds with PEG's `+`.
        """
        result = []

        while True:
            parser_result = self.parse_all(*args, ignores)

            if parser_result is None:
                result = None
                break

            result.append(parser_result)

        return result

    @backtrackable
    def alt(self, *args, ignores=()):
        """
        A helper function for trying alternative patterns. It short cricuits.
        This function corresponds with PEG's `|`.

        TODO: return a tuple of parser_result and choice index.
        """

        result = None

        for arg in args:
            # Check if argument is a string or a parser function
            if type(arg) == str:
                parser_result = self.consume_string(arg)
            else:
                parser_result = arg()

            # If parser result is okay, break out of loop
            if parser_result is not None:
                # Skip the results of arguments that are in the `ignores` list
                if arg not in ignores:
                    result = parser_result

                break

        return result

    def and_(self, *args, ignores=()):
        """
        A helper function checks if a pattern comes next. It is meant to peek not consume.
        This function corresponds with PEG's `&`.
        """

        # Get important parser state before parsing
        cursor, row, column = self.cursor, *self.get_line_info()

        parser_result = self.parse_all(self, *args, ignores)

        # Revert parser state
        self.cursor = cursor
        self.row = row
        self.column = column

        return parser_result

    def not_(self, *args, ignores=()):
        """
        A helper function checks if a pattern does not come next. It is meant to peek not consume.
        This function corresponds with PEG's `!`.
        """

        # Get important parser state before parsing
        cursor, row, column = self.cursor, *self.get_line_info()

        parser_result = self.parse_all(self, *args, ignores)

        # Revert parser state
        self.cursor = cursor
        self.row = row
        self.column = column

        return None if parser_result is not None else True

    def consume(self, *args):
        """
        Checks and consumes the next token if it is of the TokenKinds passed to the function
        """
        payload = self.eat_token()

        if payload and payload[1].kind in args:
            return payload[0]

        return None

    @backtrackable
    @memoize
    def parse_identifier(self):
        """
        Parses identifiers
        """
        return self.consume(TokenKind.IDENTIFIER)

    @backtrackable
    @memoize
    def parse_integer(self):
        """
        Parses integer literals
        """
        return self.consume(
            TokenKind.DEC_INTEGER,
            TokenKind.HEX_INTEGER,
            TokenKind.BIN_INTEGER,
            TokenKind.OCT_INTEGER,
        )

    @backtrackable
    @memoize
    def parse_float(self):
        """
        Parses floating point literals
        """
        return self.consume(TokenKind.DEC_FLOAT)

    @backtrackable
    @memoize
    def parse_imag_integer(self):
        """
        Parses imaginary integer literals
        """
        return self.consume(TokenKind.DEC_INTEGER_IMAG)

    @backtrackable
    @memoize
    def parse_imag_float(self):
        """
        Parses imaginary float literals
        """
        return self.consume(TokenKind.DEC_FLOAT_IMAG)

    @backtrackable
    @memoize
    def parse_string(self):
        """
        Parses normal string literals
        """
        return self.consume(TokenKind.STRING)

    @backtrackable
    @memoize
    def parse_byte_string(self):
        """
        Parses byte string literals
        """
        return self.consume(TokenKind.BYTE_STRING)

    @backtrackable
    @memoize
    def parse_prefixed_string(self):
        """
        Parses prefixed string literals
        """
        return self.consume(TokenKind.PREFIXED_STRING)

    @backtrackable
    @memoize
    def parse_(self):
        pass
