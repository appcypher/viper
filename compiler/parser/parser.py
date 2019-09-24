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
    IfExpr,
    FuncParam,
    FuncParams,
    LambdaExpr,
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

    @backtrackable
    @memoize
    def parse_power_expr(self):
        """
        rule = '√'? atom_expr ('^' unary_expr | '²')? [right associative]
        """

        root = self.consume_string("√")
        result = self.parse_integer()  # TODO

        if result is None:
            return None

        power = self.consume_string("^")
        integer2 = self.parse_integer()  # TODO

        if power is not None or integer2 is not None:
            result = BinaryExpr(result, Operator(power), integer2)
        else:
            square = self.consume_string("²")
            if square is not None:
                result = UnaryExpr(result, Operator(square))

        if root is not None:
            result = UnaryExpr(result, Operator(root))

        print(f"\n>>>> {result}")

        return result

    @backtrackable
    @memoize
    def parse_unary_expr(self):
        """
        rule = ('+' | '-' | '~')* power_expr [right associative]
        """
        unary_ops = []
        while True:
            unary_op = self.consume_string("+")
            if unary_op is None:
                unary_op = self.consume_string("-")
                if unary_op is None:
                    unary_op = self.consume_string("~")
                    if unary_op is None:
                        break
            unary_ops.append(Operator(unary_op))

        result = self.parse_power_expr()

        if result is None:
            return None

        for unary_op in reversed(unary_ops):
            result = UnaryExpr(result, unary_op)

        print(f"\n>>>> {result}")

        return result

    def parse_binary_expr(self, operand_parser, operators):
        """
        Helper function for parsing left-associative binary expressions.
        NOTE:
            Not bactrackable because it is called once by backtrackable functions
        """
        result = operand_parser()

        while True:
            operator = None
            second_token = None

            for i in operators:
                if type(i) == tuple:
                    operator = self.consume_string(i[0])
                    second_token = self.consume_string(i[1])
                    if operator is None or second_token is None:
                        break
                else:
                    operator = self.consume_string(i)
                    if operator is not None:
                        break

            if operator is None:
                break

            rhs = operand_parser()

            if rhs is None:
                break

            result = BinaryExpr(result, Operator(operator, second_token), rhs)

        print(f"\n>>>> {result}")

        return result

    @backtrackable
    @memoize
    def parse_mul_expr(self):
        """
        rule = unary_expr (('*' | '@' | '/' | '%' | '//') unary_expr)* [left associative]
        """

        return self.parse_binary_expr(self.parse_unary_expr, ["*", "@", "/", "%", "//"])

    @backtrackable
    @memoize
    def parse_sum_expr(self):
        """
        rule = mul_expr (('+' | '-') mul_expr)* [left associative]
        """

        return self.parse_binary_expr(self.parse_mul_expr, ["+", "-"])

    @backtrackable
    @memoize
    def parse_shift_expr(self):
        """
        rule = sum_expr (('<<' | '>>') sum_expr)* [left associative]
        """

        return self.parse_binary_expr(self.parse_sum_expr, ["<<", ">>"])

    @backtrackable
    @memoize
    def parse_and_expr(self):
        """
        rule = shift_expr ('&' shift_expr)* [left associative]
        """

        return self.parse_binary_expr(self.parse_shift_expr, ["&"])

    @backtrackable
    @memoize
    def parse_xor_expr(self):
        """
        rule = and_expr ('||' and_expr)* [left associative]
        """

        return self.parse_binary_expr(self.parse_and_expr, ["||"])

    @backtrackable
    @memoize
    def parse_or_expr(self):
        """
        rule = xor_expr ('|' xor_expr)* [left associative]
        """

        return self.parse_binary_expr(self.parse_xor_expr, ["|"])

    @backtrackable
    @memoize
    def parse_comparison_expr(self):
        """
        comparison_op =
            | '<' | '>' | '==' | '>=' | '<=' | '!=' | 'in' | 'not' 'in' | 'is' | 'is' 'not'

        rule = or_expr (comparison_op or_expr)* [left associative]
        """

        return self.parse_binary_expr(
            self.parse_or_expr,
            [
                "<",
                ">",
                "==",
                ">=",
                "<=",
                "!=",
                "in",
                ("not", "in"),
                "is",
                ("is", "not"),
            ],
        )

    @backtrackable
    @memoize
    def parse_not_test(self):
        """
        rule = 'not'* comparison_expr [left associative]
        """

        result = self.parse_comparison_expr()

        while True:
            not_op = self.consume_string("not")
            if not_op is None:
                break

            result = UnaryExpr(result, Operator(not_op))

        print(f"\n>>>> {result}")

        return result

    @backtrackable
    @memoize
    def parse_and_test(self):
        """
        rule = not_test ('and' not_test)* [left associative]
        """

        return self.parse_binary_expr(self.parse_not_test, ["and"])

    @backtrackable
    @memoize
    def parse_or_test(self):
        """
        rule = and_test ('or' and_test)* [left associative]
        """

        return self.parse_binary_expr(self.parse_and_expr, ["or"])

    @backtrackable
    @memoize
    def parse_test(self):
        """
        rule = or_test ('if' expr 'else' expr)? [left associative]
        """

        result = self.parse_or_test()

        if_ = self.consume_string("if")
        or_test = self.parse_or_test()  # TODO
        else_ = self.consume_string("else")
        or_test2 = self.parse_or_test()  # TODO

        if (
            (if_ is not None)
            and (or_test is not None)
            and (else_ is not None)
            and (or_test2 is not None)
        ):
            result = IfExpr(result, or_test, or_test2)

        print(f"\n>>>> {result}")

        return result

    @backtrackable
    @memoize
    def parse_lambda_param(self):
        """
        rule = identifier ('=' expr)?
        """

        identifier = self.parse_identifier()

        if identifier is None:
            return None

        result = FuncParam(identifier)

        assignment_op = self.consume_string("=")
        test = self.parse_test()  # TODO

        if assignment_op is not None and test is not None:
            result.default_value_expr = test

        return result

    @backtrackable
    @memoize
    def parse_lambda_params(self):
        """
        rule =
            | '(' func_params? ')'
            | lambda_param (',' lambda_param)* (',' '*' lambda_param (',' lambda_param)*)?
                (',' '**' lambda_param)? ','?
            | '*' lambda_param (',' lambda_param)* (',' '**' lambda_param)? ','?
            | '**' lambda_param ','?
        """

        # FIRST ALTERNATIVE
        open_brackets = self.consume_string("(")
        func_params = self.parse_lambda_params()  # TODO
        close_brackets = self.consume_string(")")

        if (
            (open_brackets is not None)
            and (func_params is not None)
            and (close_brackets is not None)
        ):
            return func_params

        # SECOND ALTERNATIVE
        params = [self.parse_lambda_param()]
        while True:
            comma = self.consume_string(",")
            param = self.parse_lambda_param()

            if comma is not None and param is not None:
                params.append(param)
            else:
                break

        tuple_rest_param = None
        comma = self.consume_string(",")
        star = self.consume_string("*")
        param = self.parse_lambda_param()

        if comma is not None and star is not None and param is not None:
            tuple_rest_param = param

        named_tuple_params = []
        if tuple_rest_param:
            while True:
                comma = self.consume_string(",")
                param = self.parse_lambda_param()

                if comma is not None and param is not None:
                    named_tuple_params.append(param)
                else:
                    break

        named_tuple_rest_param = None
        comma = self.consume_string(",")
        star = self.consume_string("**")
        param = self.parse_lambda_param()

        if comma is not None and star is not None and param is not None:
            named_tuple_rest_param = param

        if params is not None:
            return FuncParams(
                params, tuple_rest_param, named_tuple_params, named_tuple_rest_param
            )

        # THIRD ALTERNATIVE
        tuple_star = self.consume_string("*")
        tuple_rest_param = self.parse_lambda_param()

        named_tuple_params = []
        if tuple_rest_param:
            while True:
                comma = self.consume_string(",")
                param = self.parse_lambda_param()

                if comma is not None and param is not None:
                    named_tuple_params.append(param)
                else:
                    break

        named_tuple_rest_param = None
        comma = self.consume_string(",")
        star = self.consume_string("**")
        param = self.parse_lambda_param()

        if comma is not None and star is not None and param is not None:
            named_tuple_rest_param = param

        if tuple_star is not None and tuple_rest_param is not None:
            return FuncParams(
                None, tuple_rest_param, named_tuple_params, named_tuple_rest_param
            )

        # FOURTH ALTERNATIVE
        star = self.consume_string("**")
        named_tuple_rest_param = self.parse_lambda_param()

        if star is not None and named_tuple_rest_param is not None:
            return FuncParams(
                None, None, None, named_tuple_rest_param
            )

        return None
