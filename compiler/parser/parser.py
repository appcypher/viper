"""
A packrat parser for parsing Viper's grammar.
"""


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
    - A parse function result should always be an AST. Avoid returning a parse tree.
    - A parse function result should not hold values, but references to token elements.
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

    def backtrackable(f):
        """
        Changes the parser state to it's original state before if a parser function
        fails (returns None).
        """

        def wrapper(self, *args):
            # Get important parser state before parsing
            cursor, row, column = self.cursor, *self.get_line_info()

            parser_result = f(self, *args)

            # Revert parser state
            if not parser_result:
                self.cursor = cursor
                self.row = row
                self.column = column

            return parser_result

        return wrapper

    @backtrackable
    def memoize(f):
        """
        Memoizes the result of a recursive decent parser.

        NOTE: because this memoize function wraps and resturns a parser
            the bactrackable decorator affects the parser, not the memoization.
        """

        def wrapper(self, *args):
            # Get info about parser function.
            cursor = self.cursor
            func_name = f.__name__

            # Check cache if parser function result is already saved
            cursor_key = self.cache.get(cursor)

            if cursor_key:
                try:
                    return cursor_key[func_name]
                except KeyError:
                    pass

            # Otherwise go ahead and parse then cache result
            parser_result = f(self, *args)

            if not cursor_key:
                self.cache[cursor] = {func_name: parser_result}
            else:
                try:
                    cursor_key[func_name]
                except KeyError:
                    self.cache[cursor][func_name] = parser_result

            return parser_result

        return wrapper

    def eat_token(self):
        pass

    def peek_token(self):
        pass

    def opt(self):
        pass

    @memoize
    def parse_name(self):
        pass

