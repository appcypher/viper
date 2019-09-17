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
    - A parser function result should often be an AST. Avoid returning parse trees.
    - A parser function result should not hold values, but references to token elements.
    """

    def __init__(self, tokens):
        self.tokens = tokens
        self.tokens_length = len(tokens)
        self.cursor = -1
        self.row = 0
        self.column = -1
        self.cache = {}

    def get_line_info(self):
        return self.row, self.column

    def backtrackable(parser):
        """
        A decorator that changes the parser state to it's original state before a parser function
        is called and failed (i.e. returns None).
        """

        def wrapper(self, *args):
            # Get important parser state before parsing
            cursor, row, column = self.cursor, *self.get_line_info()

            parser_result = parser(self, *args)

            # Revert parser state
            if parser_result is None:
                self.cursor = cursor
                self.row = row
                self.column = column

            return parser_result

        return wrapper

    @backtrackable
    def memoize(parser):
        """
        A decorator that memoizes the result of a recursive decent parser.

        NOTE:
            Since this memoize function wraps and returns a parser the bactrackable decorator
            affects the output parser, not the memoization process. This gives any parser
            memoize wraps the ability to backtrack on fail.
        """

        def wrapper(self, *args):
            # Get info about parser function.
            cursor = self.cursor
            parser_name = parser.__name__

            # Check cache if parser function result is already saved
            cursor_key = self.cache.get(cursor)

            if cursor_key:
                try:
                    return cursor_key[parser_name]
                except KeyError:
                    pass

            # Otherwise go ahead and parse, then cache result
            parser_result = parser(self, *args)

            if not cursor_key:
                self.cache[cursor] = {parser_name: parser_result}
            else:
                try:
                    cursor_key[parser_name]
                except KeyError:
                    self.cache[cursor][parser_name] = parser_result

            return parser_result

        return wrapper

    def eat_token(self):
        """
        Returns the next token and advances the cursor position
        """
        if self.cursor + 1 < self.tokens_length:
            self.cursor += 1

            token = self.code[self.cursor]

            self.column = token.column
            self.row = token.row

            return token

        return None

    def consume_string(string):
        """
        Consumes and check if the next token matches the string argument.

        NOTE:
            Not bactrackable, because it is going to be called by backtrackable function
            like parse_all anyway.
        """
        token = self.eat_token()

        if token and token.data == string:
            return token

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
    def opt_more(*args, ignores=()):
        """
        A helper function for (greedily) consuming zero or more tokens using parsers passed to it.
        This function is corresponds with PEG's `+`.
        """
        result = []

        while True:
            parser_result = self.parse_all(*args, ignores)

            if parser_result is None:
                break

            result.append(parser_result)

        return parser_result

    @backtrackable
    def more(*args, ignores=()):
        """
        A helper function for (greedily) consuming one or more tokens using parsers passed to it.
        This function is corresponds with PEG's `+`.
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
    def alt(*args, ignores=()):
        result = None

        for arg in args:
            # Check if argument is a string or a parser function
            if type(arg) == str:
                parser_result = self.consume_string(arg)
            else:
                parser_result = arg()

            # If parser result isn't okay, break out of loop
            if parser_result:
                # Skip the results of arguments that are in the `ignores` list
                if arg not in ignores:
                    result = parser_result

                break

        return result


    # and not alt

    @memoize
    def parse_name(self):
        token = self.eat_token()

        if token and token.kind != TokenKind.IDENTIFIER:
            return token

        return None

