"""
A packrat parser for parsing Viper's syntax.

Check `compiler/parser/parser.grammar` for the language's parser grammar specification.
"""
from ..lexer.lexer import TokenKind
from .ast import (
    Newline,
    Indent,
    Dedent,
    Identifier,
    Integer,
    Float,
    ImagInteger,
    ImagFloat,
    String,
    ByteString,
    PrefixedString,
    Operator,
    UnaryExpr,
    BinaryExpr,
)


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
    - A parser function result should not hold values, but references to token elements.
    """

    def __init__(self, tokens):
        self.tokens = tokens
        self.tokens_length = len(tokens)
        self.cursor = -1
        self.row = 0
        self.column = -1
        self.cache = {}

    def __repr__(self):
        return f"Parser(tokens={self.tokens})"

    @staticmethod
    def from_code(code):
        """
        Creates a parser from code.
        """
        from ..lexer.lexer import Lexer

        tokens = Lexer(code).lex()

        return Parser(tokens)

    def get_line_info(self):
        return self.row, self.column

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
        Consumes and checks if next token holds the same date as `string`.
        """
        if self.cursor + 1 < self.tokens_length:
            token = self.tokens[self.cursor + 1]

            if token.data == string:
                self.cursor += 1
                self.column = token.column
                self.row = token.row

                return self.cursor

        return None

    def backtrackable(parser):
        """
        A decorator that changes the parser state to it's original state just before a parser
        function failed (i.e. returns None).
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

    # @backtrackable
    # def parse_all(self, *args):
    #     """
    #     Takes an arguments of parser and strings (which it calls `consume_string` on) and
    #     calls them. It fails if any of the parser fails.
    #     `ignores` referes to the results of args to ingnore
    #     """

    #     result = []

    #     for arg in args:
    #         # Check if argument is a string or a parser function
    #         if type(arg) == str:
    #             parser_result = self.consume_string(arg)
    #         else:
    #             parser_result = arg()

    #         print('*****', parser_result)

    #         # If parser result isn't okay, break out of loop
    #         if parser_result is None:
    #             result = None
    #             break

    #         result.append(parser_result)

    #     return result

    # @backtrackable
    # def opt(self, *args):
    #     """
    #     A helper function for consuming tokens based on pattern the parsers expect.
    #     The pattern is optional, so the parser passes even if the pattern fails.
    #     This function corresponds with PEG's `?`.
    #     """

    #     result = self.parse_all(*args)

    #     if result is None:
    #         return []

    #     return result

    # @backtrackable
    # def opt_more(self, *args):
    #     """
    #     A helper function for (greedily) consuming zero or more tokens based on pattern the
    #     parsers expect.
    #     This function corresponds with PEG's `*`.
    #     """
    #     result = []

    #     while True:
    #         parser_result = self.parse_all(*args)

    #         if parser_result is None:
    #             break

    #         result.append(parser_result)

    #     return result

    # @backtrackable
    # def more(self, *args):
    #     """
    #     A helper function for (greedily) consuming one or more tokens based on pattern the
    #     parsers expect.
    #     This function corresponds with PEG's `+`.
    #     """
    #     result = []
    #     count = 0

    #     while True:
    #         parser_result = self.parse_all(*args)

    #         if parser_result is None:
    #             break

    #         result.append(parser_result)
    #         count += 1

    #     if count < 1:
    #         result = None

    #     return result

    # @backtrackable
    # def alt(self, *args):
    #     """
    #     A helper function for trying alternative patterns. It short cricuits.
    #     This function corresponds with PEG's `|`.
    #     """

    #     result = None

    #     for index, arg in enumerate(args):
    #         # Check if argument is a string or a parser function
    #         if type(arg) == str:
    #             parser_result = self.consume_string(arg)
    #         else:
    #             parser_result = arg()

    #         # If parser result is okay, break out of loop
    #         if parser_result is not None:
    #             result = (index, parser_result)
    #             break

    #     return result

    # def and_(self, *args):
    #     """
    #     A helper function checks if a pattern comes next. It is meant to peek not consume.
    #     This function corresponds with PEG's `&`.

    #     TODO: Not used. Remove.
    #     """

    #     # Get important parser state before parsing
    #     cursor, row, column = self.cursor, *self.get_line_info()

    #     parser_result = self.parse_all(self, *args)

    #     # Revert parser state
    #     self.cursor = cursor
    #     self.row = row
    #     self.column = column

    #     return parser_result

    # def not_(self, *args):
    #     """
    #     A helper function checks if a pattern does not come next. It is meant to peek not consume.
    #     This function corresponds with PEG's `!`.

    #     TODO: Not used. Remove.
    #     """

    #     # Get important parser state before parsing
    #     cursor, row, column = self.cursor, *self.get_line_info()

    #     parser_result = self.parse_all(self, *args)

    #     # Revert parser state
    #     self.cursor = cursor
    #     self.row = row
    #     self.column = column

    #     return None if parser_result is not None else True

    def consume(self, *args, result_type):
        """
        Checks and consumes the next token if it is of the TokenKinds passed to the function
        """
        payload = self.eat_token()

        if payload and payload[1].kind in args:
            return result_type(payload[0])

        return None

    @backtrackable
    @memoize
    def parse_newline(self):
        """
        Parses normal string literals
        """
        return self.consume(TokenKind.NEWLINE, result_type=Newline)

    @backtrackable
    @memoize
    def parse_indent(self):
        """
        Parses byte string literals
        """
        return self.consume(TokenKind.INDENT, result_type=Indent)

    @backtrackable
    @memoize
    def parse_dedent(self):
        """
        Parses prefixed string literals
        """
        return self.consume(TokenKind.DEDENT, result_type=Dedent)

    @backtrackable
    @memoize
    def parse_identifier(self):
        """
        Parses identifiers
        """
        return self.consume(TokenKind.IDENTIFIER, result_type=Identifier)

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
            result_type=Integer,
        )

    @backtrackable
    @memoize
    def parse_float(self):
        """
        Parses floating point literals
        """
        return self.consume(TokenKind.DEC_FLOAT, result_type=Float)

    @backtrackable
    @memoize
    def parse_imag_integer(self):
        """
        Parses imaginary integer literals
        """
        return self.consume(TokenKind.DEC_INTEGER_IMAG, result_type=ImagInteger)

    @backtrackable
    @memoize
    def parse_imag_float(self):
        """
        Parses imaginary float literals
        """
        return self.consume(TokenKind.DEC_FLOAT_IMAG, result_type=ImagFloat)

    @backtrackable
    @memoize
    def parse_string(self):
        """
        Parses normal string literals
        """
        return self.consume(TokenKind.STRING, result_type=String)

    @backtrackable
    @memoize
    def parse_byte_string(self):
        """
        Parses byte string literals
        """
        return self.consume(TokenKind.BYTE_STRING, result_type=ByteString)

    @backtrackable
    @memoize
    def parse_prefixed_string(self):
        """
        Parses prefixed string literals
        """
        return self.consume(TokenKind.PREFIXED_STRING, result_type=PrefixedString)

    # @backtrackable
    # @memoize
    # def parse_power_expr(self):
    #     """
    #     """
    #     parse_result = self.parse_all(
    #         lambda: self.opt("√"),
    #         self.parse_integer,  # TODO
    #         lambda: self.opt(
    #             lambda: self.alt(
    #                 lambda: self.parse_all("^", self.parse_integer), "²"  # TODO
    #             )
    #         ),
    #     )

    #     if parse_result is None:
    #         return None

    #     opt_unary_root_op = parse_result[0]
    #     result = parse_result[1]
    #     opt_alt_power = parse_result[2]

    #     if opt_alt_power != []:
    #         if opt_alt_power[0][0] == 0:
    #             binary_power_op = Operator(opt_alt_power[0][1][0])
    #             binary_power_unary_expr = opt_alt_power[0][1][1]
    #             result = BinaryExpr(result, binary_power_op, binary_power_unary_expr)

    #         elif opt_alt_power[0][0] == 1:
    #             unary_square_op = Operator(opt_alt_power[0][1])
    #             result = UnaryExpr(result, unary_square_op)

    #     if opt_unary_root_op != []:
    #         result = UnaryExpr(result, Operator(opt_unary_root_op[0]))

    #     return result

    @backtrackable
    @memoize
    def parse_power_expr(self):
        """
        rule = '√'? atom_expr ('^' unary_expr | '²')? [right associative]
        """

        root = self.consume_string('√')
        result = self.parse_integer()

        if result is None:
            return None

        power = self.consume_string('^')
        integer2 = self.parse_integer()

        if power is not None or integer2 is not None:
            result = BinaryExpr(result, Operator(power), integer2)
        else:
            square = self.consume_string('²')
            if square is not None:
                result = UnaryExpr(result, Operator(square))

        if root is not None:
            result = UnaryExpr(result, Operator(root))

        print(f'\n>>>> {result}')

        return result

    @backtrackable
    @memoize
    def parse_unary_expr(self):
        """
        rule = ('+' | '-' | '~')* power_expr [right associative]
        """
        unary_ops = []
        while True:
            unary_op = self.consume_string('+')
            if unary_op is None:
                unary_op = self.consume_string('-')
                if unary_op is None:
                    unary_op = self.consume_string('~')
                    if unary_op is None:
                        break
            unary_ops.append(Operator(unary_op))

        result = self.parse_power_expr()

        if result is None:
            return None

        for unary_op in reversed(unary_ops):
            result = UnaryExpr(result, unary_op)

        print(f'\n>>>> {result}')

        return result

    @backtrackable
    @memoize
    def parse_mul_expr(self):
        """
        rule = unary_expr (('*' | '@' | '/' | '%' | '//') unary_expr)* [left associative]
        """
        result = self.parse_unary_expr()
        while True:
            mul_op = self.consume_string('*')
            if mul_op is None:
                mul_op = self.consume_string('@')
                if mul_op is None:
                    mul_op = self.consume_string('/')
                    if mul_op is None:
                        mul_op = self.consume_string('%')
                        if mul_op is None:
                            mul_op = self.consume_string('//')
                            if mul_op is None:
                                break
            unary_expr = self.parse_unary_expr()

            if unary_expr is None:
                break

            result = BinaryExpr(result, Operator(mul_op), unary_expr)

        print(f'\n>>>> {result}')

        return result

