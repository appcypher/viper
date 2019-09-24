from compiler.parser.parser import Parser
from compiler.parser.ast import (
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
    UnaryExpr,
    BinaryExpr,
)


def test_parser_memoizes_called_parser_functions_successfully():
    # Memoize if parser successful
    parser0 = Parser.from_code("identifier")
    result0 = parser0.parse_identifier()

    # TODO: Memoize if parser fails
    # TODO: Use memoized result
    assert result0 == Identifier(0)
    assert parser0.cache == {-1: {'parse_identifier': (Identifier(0), 0)}}


def test_parser_skips_properly_when_cache_is_resused():
    """
    TODO
    """


def test_parser_backtracks_on_fail_successfully():
    parser0 = Parser.from_code("1hello")
    result0 = parser0.parse_identifier()

    # TODO: Try more complex parser functions

    assert parser0.cursor == -1
    assert result0 is None


def test_parse_newline_parses_newlines_successfully():
    result0 = Parser.from_code("\n").parse_newline()
    result1 = Parser.from_code("\r\n").parse_newline()
    result2 = Parser.from_code("\r").parse_newline()

    assert result0 == Newline(0)
    assert result1 == Newline(0)
    assert result2 == Newline(0)


def test_parse_identifier_parses_identifiers_successfully():
    result = Parser.from_code("_HEoDagu123").parse_identifier()

    assert result == Identifier(0)


def test_parse_integer_parses_integer_literals_successfully():
    result0 = Parser.from_code("5_000").parse_integer()
    result1 = Parser.from_code("0001").parse_integer()
    result2 = Parser.from_code("0b11_00").parse_integer()
    result3 = Parser.from_code("0o217").parse_integer()
    result4 = Parser.from_code("0xffEE_210").parse_integer()

    assert result0 == Integer(0)
    assert result1 == Integer(0)
    assert result2 == Integer(0)
    assert result3 == Integer(0)
    assert result4 == Integer(0)


def test_parse_float_parses_float_literals_successfully():
    result0 = Parser.from_code(".05").parse_float()
    result1 = Parser.from_code("0.0_55").parse_float()
    result2 = Parser.from_code("1_00.00_50").parse_float()
    result3 = Parser.from_code("1.e-5_00").parse_float()
    result4 = Parser.from_code("1.").parse_float()
    result5 = Parser.from_code("1_00.1_00e-1_00").parse_float()

    assert result0 == Float(0)
    assert result1 == Float(0)
    assert result2 == Float(0)
    assert result3 == Float(0)
    assert result4 == Float(0)
    assert result5 == Float(0)


def test_parse_imag_integer_parses_imaginary_integer_literals_successfully():
    result0 = Parser.from_code("5_000im").parse_imag_integer()
    result1 = Parser.from_code("0001im").parse_imag_integer()

    assert result0 == ImagInteger(0)
    assert result1 == ImagInteger(0)


def test_parse_imag_float_parses_imaginary_float_literals_successfully():
    result0 = Parser.from_code(".05im").parse_imag_float()
    result1 = Parser.from_code("0.0_55im").parse_imag_float()
    result2 = Parser.from_code("1_00.00_50im").parse_imag_float()
    result3 = Parser.from_code("1.e-5_00im").parse_imag_float()
    result4 = Parser.from_code("1_00.1_00e-1_00im").parse_imag_float()

    assert result0 == ImagFloat(0)
    assert result1 == ImagFloat(0)
    assert result2 == ImagFloat(0)
    assert result3 == ImagFloat(0)
    assert result4 == ImagFloat(0)


def test_parse_string_parses_string_literals_successfully():
    result0 = Parser.from_code("'hello\t there'").parse_string()
    result1 = Parser.from_code('" This is a new world"').parse_string()
    result2 = Parser.from_code("'''\n This is a new world\n'''").parse_string()
    result3 = Parser.from_code('"""\n This is a new world\n"""').parse_string()

    assert result0 == String(0)
    assert result1 == String(0)
    assert result2 == String(0)
    assert result3 == String(0)


def test_parse_byte_string_parses_byte_string_literals_successfully():
    result0 = Parser.from_code("b'hello\t there'").parse_byte_string()
    result1 = Parser.from_code('rb" This is a new world"').parse_byte_string()
    result2 = Parser.from_code("b'''\n This is a new world\n'''").parse_byte_string()
    result3 = Parser.from_code('rb"""\n This is a new world\n"""').parse_byte_string()

    assert result0 == ByteString(0)
    assert result1 == ByteString(0)
    assert result2 == ByteString(0)
    assert result3 == ByteString(0)


def test_parse_prefixed_string_parses_prefixed_string_literals_successfully():
    result0 = Parser.from_code("u'hello\t there'").parse_prefixed_string()
    result1 = Parser.from_code('rf" This is a new world"').parse_prefixed_string()
    result2 = Parser.from_code("r'''\n This is a new world\n'''").parse_prefixed_string()
    result3 = Parser.from_code('rf"""\n This is a new world\n"""').parse_prefixed_string()

    assert result0 == PrefixedString(0)
    assert result1 == PrefixedString(0)
    assert result2 == PrefixedString(0)
    assert result3 == PrefixedString(0)

# WIP

def test_parse_power_expr_():
    # TODO: More complex examples
    result0 = Parser.from_code("5^6").parse_power_expr()
    result1 = Parser.from_code("5²").parse_power_expr()
    result1 = Parser.from_code("5").parse_power_expr()
    result2 = Parser.from_code("√5²").parse_power_expr()
    result3 = Parser.from_code("√5^5").parse_power_expr()

    # print('\n', result0, '\n', result1, '\n', result2)

def test_parse_unary_expr_():
    # TODO: More complex examples
    result0 = Parser.from_code("5^-6").parse_unary_expr()
    result1 = Parser.from_code("-5²").parse_unary_expr()
    result2 = Parser.from_code("√~5²").parse_unary_expr()
    result3 = Parser.from_code("-√5^5").parse_unary_expr()
    result3 = Parser.from_code("-~+5_00").parse_unary_expr()

    # print('\n', result0, '\n', result1, '\n', result2)

def test_parse_mul_expr_():
    # TODO: More complex examples
    result0 = Parser.from_code("-5.0f").parse_mul_expr()
    result1 = Parser.from_code("0xff*3//4").parse_mul_expr()
    result2 = Parser.from_code("√~5f²").parse_mul_expr()
    result3 = Parser.from_code("5^5*3").parse_mul_expr()
    result3 = Parser.from_code("-5/-4*+3").parse_mul_expr()

    # print('\n', result0, '\n', result1, '\n', result2)
