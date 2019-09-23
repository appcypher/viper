from compiler.lexer.lexer import Lexer, Token, TokenKind, LexerError, IndentSpaceKind
from pytest import raises


def test_lexer_tokenizes_identifier_that_starts_with_underscore_as_identifier():
    result = Lexer(r"_hello").lex()
    assert result == [Token(r"_hello", TokenKind.IDENTIFIER, 0, 5)]


def test_lexer_tokenizes_identifier_that_starts_with_letter_as_identifier():
    result = Lexer("raw").lex()
    assert result == [Token(r"raw", TokenKind.IDENTIFIER, 0, 2)]


def test_lexer_tokenizes_identifier_with_digits_in_middle_as_identifier():
    result = Lexer(r"_hello88_").lex()
    assert result == [Token("_hello88_", TokenKind.IDENTIFIER, 0, 8)]


def test_lexer_tokenizes_single_character_as_identifier():
    result = Lexer("h").lex()
    assert result == [Token(r"h", TokenKind.IDENTIFIER, 0, 0)]


def test_lexer_tokenizes_valid_newline_successfully():
    result = Lexer("\r\n\n").lex()
    assert result == [
        Token("", TokenKind.NEWLINE, 1, -1),
        Token("", TokenKind.NEWLINE, 2, -1),
    ]


def test_lexer_tokenizes_underscore_as_identifier():
    result = Lexer("_").lex()
    assert result == [Token(r"_", TokenKind.IDENTIFIER, 0, 0)]


def test_lexer_tokenizes_valid_prefixed_strings_successfully():
    result0 = Lexer(r"r'hello'").lex()
    result1 = Lexer(r'u"hello"').lex()
    result2 = Lexer(r'f"""hello"""').lex()
    result3 = Lexer(r"rf'hello'").lex()

    assert result0 == [Token(r"hello", TokenKind.PREFIXED_STRING, 0, 7)]
    assert result1 == [Token(r"hello", TokenKind.PREFIXED_STRING, 0, 7)]
    assert result2 == [Token(r"hello", TokenKind.PREFIXED_STRING, 0, 11)]
    assert result3 == [Token(r"hello", TokenKind.PREFIXED_STRING, 0, 8)]


def test_lexer_tokenizes_valid_byte_strings_successfully():
    result0 = Lexer(r"b'hello'").lex()
    result6 = Lexer(r"rb'''hello'''").lex()

    assert result0 == [Token(r"hello", TokenKind.BYTE_STRING, 0, 7)]
    assert result6 == [Token(r"hello", TokenKind.BYTE_STRING, 0, 12)]


def test_lexer_tokenizes_valid_single_quote_short_string_successfully():
    result = Lexer(r"'erCA63y8hbb 54^58* (@$Q#3qDSHHScTw62-+'").lex()
    assert result == [
        Token(r"erCA63y8hbb 54^58* (@$Q#3qDSHHScTw62-+", TokenKind.STRING, 0, 39)
    ]


def test_lexer_tokenizes_valid_double_quote_short_string_successfully():
    result = Lexer(r'"erCA63y8hbb 54^58*(@$Q#3qDSHHScTw62-+"').lex()
    assert result == [
        Token(r"erCA63y8hbb 54^58*(@$Q#3qDSHHScTw62-+", TokenKind.STRING, 0, 38)
    ]


def test_lexer_tokenizes_valid_double_char_prefixed_double_quote_short_string_successfully():
    result = Lexer(r'rf"erCA63y8hbb 54^58*(@$Q#3qDSHHScTw62-+"').lex()
    assert result == [
        Token(
            r"erCA63y8hbb 54^58*(@$Q#3qDSHHScTw62-+", TokenKind.PREFIXED_STRING, 0, 40
        )
    ]


def test_lexer_tokenizes_valid_single_char_prefixed_double_quote_short_string_successfully():
    result = Lexer(r'r"erCA63y8hbb 54^58*(@$Q#3qDSHHScTw62-+"').lex()
    assert result == [
        Token(
            r"erCA63y8hbb 54^58*(@$Q#3qDSHHScTw62-+", TokenKind.PREFIXED_STRING, 0, 39
        )
    ]


def test_lexer_tokenizes_valid_empty_short_string_successfully():
    result = Lexer(r'""').lex()
    assert result == [Token(r"", TokenKind.STRING, 0, 1)]


def test_lexer_fails_with_return_char_in_short_string():
    lexer = Lexer('"\r"')
    with raises(LexerError) as exc_info:
        lexer.lex()

    assert (exc_info.value.row, exc_info.value.column) == (0, 0)


def test_lexer_fails_with_newline_char_in_short_string():
    lexer = Lexer('"\n"')
    with raises(LexerError) as exc_info:
        lexer.lex()

    assert (exc_info.value.message, exc_info.value.row, exc_info.value.column) == (
        "Encountered unexpected newline character",
        0,
        0,
    )


def test_lexer_fails_with_unclosed_delimiter_for_short_string():
    lexer = Lexer('"hello there')
    with raises(LexerError) as exc_info:
        lexer.lex()

    assert (exc_info.value.message, exc_info.value.row, exc_info.value.column) == (
        "Unexpected end of string. Closing delimiter not found",
        0,
        11,
    )


def test_lexer_tokenizes_valid_single_quote_long_string_successfully():
    result = Lexer(r"'''erCA63y8hbb 54^58* (@$Q#3qDSHHScTw62-+'''").lex()
    assert result == [
        Token(r"erCA63y8hbb 54^58* (@$Q#3qDSHHScTw62-+", TokenKind.STRING, 0, 43)
    ]


def test_lexer_tokenizes_valid_double_quote_long_string_successfully():
    result = Lexer(r'"""erCA63y8hbb 54^58*(@$Q#3qDSHHScTw62-+"""').lex()
    assert result == [
        Token(r"erCA63y8hbb 54^58*(@$Q#3qDSHHScTw62-+", TokenKind.STRING, 0, 42)
    ]


def test_lexer_tokenizes_valid_double_char_prefixed_single_quote_long_string_successfully():
    result = Lexer(r"rf'''erCA63y8hbb 54^58* (@$Q#3qDSHHScTw62-+'''").lex()
    assert result == [
        Token(
            r"erCA63y8hbb 54^58* (@$Q#3qDSHHScTw62-+", TokenKind.PREFIXED_STRING, 0, 45
        )
    ]


def test_lexer_tokenizes_valid_single_char_prefixed_double_quote_long_string_successfully():
    result = Lexer(r'r"""erCA63y8hbb 54^58*(@$Q#3qDSHHScTw62-+"""').lex()
    assert result == [
        Token(
            r"erCA63y8hbb 54^58*(@$Q#3qDSHHScTw62-+", TokenKind.PREFIXED_STRING, 0, 43
        )
    ]


def test_lexer_tokenizes_valid_empty_long_string_successfully():
    result = Lexer(r'""""""').lex()
    assert result == [Token(r"", TokenKind.STRING, 0, 5)]


def test_lexer_tokenizes_long_string_with_incomplete_delimiter_successfully():
    result = Lexer(r'"""Mary had a little lamb"" this is ridiculous"""').lex()
    assert result == [
        Token(r'Mary had a little lamb"" this is ridiculous', TokenKind.STRING, 0, 48)
    ]


def test_lexer_tokenizes_long_string_with_valid_return_char_successfully():
    r"""
    TODO: \r has a weird effect on the string on my macOS development environment
    """
    # lexer = Lexer('"""\r this is a doc \r\n#3qDSHHScTw62-+"""')
    # result = lexer.lex()
    # assert result == [
    #     Token("\r this is a doc \r\n#3qDSHHScTw62-+", TokenKind.STRING, 2, 17)
    # ]
    pass


def test_lexer_tokenizes_long_string_with_valid_newline_char_successfully():
    result = Lexer('"""\n this is a \ndoc #3qDSHHScTw62-+"""').lex()
    assert result == [
        Token("\n this is a \ndoc #3qDSHHScTw62-+", TokenKind.STRING, 2, 21)
    ]


def test_lexer_fails_with_unclosed_delimiter_for_long_string():
    lexer = Lexer('"""hello there""')
    with raises(LexerError) as exc_info:
        lexer.lex()

    assert (exc_info.value.message, exc_info.value.row, exc_info.value.column) == (
        "Unexpected end of string. Closing delimiter not found",
        0,
        15,
    )


def test_lexer_tokenizes_with_valid_long_byte_string():
    result = Lexer('b"""This is spartan 0078#*"""').lex()
    assert result == [Token("This is spartan 0078#*", TokenKind.BYTE_STRING, 0, 28)]


def test_lexer_fails_with_non_ascii_char_in_long_byte_string():
    lexer = Lexer('b"""hello thereΣ"""')
    with raises(LexerError) as exc_info:
        lexer.lex()

    assert (exc_info.value.message, exc_info.value.row, exc_info.value.column) == (
        "Encountered unexpected non-ASCII character: 'Σ'",
        0,
        14,
    )


def test_lexer_fails_with_unclosed_delimiter_for_short_byte_string():
    lexer = Lexer('br"hello there')
    with raises(LexerError) as exc_info:
        lexer.lex()

    assert (exc_info.value.message, exc_info.value.row, exc_info.value.column) == (
        "Unexpected end of string. Closing delimiter not found",
        0,
        13,
    )


def test_lexer_fails_with_unclosed_delimiter_for_long_byte_string():
    lexer = Lexer('b"""hello there""')
    with raises(LexerError) as exc_info:
        lexer.lex()

    assert (exc_info.value.message, exc_info.value.row, exc_info.value.column) == (
        "Unexpected end of string. Closing delimiter not found",
        0,
        16,
    )


def test_lexer_tokenizes_valid_dec_integer_successfully():
    result0 = Lexer("0123456789").lex()
    result1 = Lexer("123456789").lex()
    result2 = Lexer("01_33456_789").lex()
    result3 = Lexer("5_37450_99").lex()
    result4 = Lexer("1").lex()
    result5 = Lexer("0").lex()
    assert result0 == [Token("0123456789", TokenKind.DEC_INTEGER, 0, 9)]
    assert result1 == [Token("123456789", TokenKind.DEC_INTEGER, 0, 8)]
    assert result2 == [Token("0133456789", TokenKind.DEC_INTEGER, 0, 11)]
    assert result3 == [Token("53745099", TokenKind.DEC_INTEGER, 0, 9)]
    assert result4 == [Token("1", TokenKind.DEC_INTEGER, 0, 0)]
    assert result5 == [Token("0", TokenKind.DEC_INTEGER, 0, 0)]


def test_lexer_tokenizes_valid_hex_integer_successfully():
    result0 = Lexer("0x1234567890aAbBcCdDeEfF").lex()
    result1 = Lexer("0x_23A_b4_567dD_90aBcCeEfF").lex()
    assert result0 == [Token("1234567890aAbBcCdDeEfF", TokenKind.HEX_INTEGER, 0, 23)]
    assert result1 == [Token("23Ab4567dD90aBcCeEfF", TokenKind.HEX_INTEGER, 0, 25)]


def test_lexer_tokenizes_valid_oct_integer_successfully():
    result0 = Lexer("0o01234567").lex()
    result1 = Lexer("0o12_03_4").lex()
    assert result0 == [Token("01234567", TokenKind.OCT_INTEGER, 0, 9)]
    assert result1 == [Token("12034", TokenKind.OCT_INTEGER, 0, 8)]


def test_lexer_fails_with_incomplete_non_decimal_integer_literal():
    lexer0 = Lexer("0o")
    lexer1 = Lexer("0btt")
    lexer2 = Lexer("0x")

    with raises(LexerError) as exc_info0:
        lexer0.lex()

    with raises(LexerError) as exc_info1:
        lexer1.lex()

    with raises(LexerError) as exc_info2:
        lexer2.lex()

    assert (exc_info0.value.message, exc_info0.value.row, exc_info0.value.column) == (
        "Unexpected end of integer literal",
        0,
        1,
    )

    assert (exc_info1.value.message, exc_info1.value.row, exc_info1.value.column) == (
        "Unexpected end of integer literal",
        0,
        1,
    )

    assert (exc_info2.value.message, exc_info2.value.row, exc_info2.value.column) == (
        "Unexpected end of integer literal",
        0,
        1,
    )


def test_lexer_fails_with_consecutive_underscores_in_integer_literal():
    lexer0 = Lexer("0o1_234__5")
    lexer1 = Lexer("0b1_111__0")
    lexer2 = Lexer("0x1_234__5")
    lexer3 = Lexer("1_234__5")

    with raises(LexerError) as exc_info0:
        lexer0.lex()

    with raises(LexerError) as exc_info1:
        lexer1.lex()

    with raises(LexerError) as exc_info2:
        lexer2.lex()

    with raises(LexerError) as exc_info3:
        lexer3.lex()

    assert (exc_info0.value.message, exc_info0.value.row, exc_info0.value.column) == (
        "Unexpected consecutive underscores in integer literal",
        0,
        8,
    )

    assert (exc_info1.value.message, exc_info1.value.row, exc_info1.value.column) == (
        "Unexpected consecutive underscores in integer literal",
        0,
        8,
    )

    assert (exc_info2.value.message, exc_info2.value.row, exc_info2.value.column) == (
        "Unexpected consecutive underscores in integer literal",
        0,
        8,
    )

    assert (exc_info3.value.message, exc_info3.value.row, exc_info3.value.column) == (
        "Unexpected consecutive underscores in integer literal",
        0,
        6,
    )


def test_lexer_tokenizes_coefficient_expression_with_adjacent_number_and_identifier_successfully():
    result0 = Lexer("045_").lex()
    result1 = Lexer("123f").lex()
    result2 = Lexer("1_234e_00").lex()
    result3 = Lexer("1_000_500r_ac").lex()
    result3 = Lexer("1_000.500r_ac").lex()

    assert result0 == [
        Token("045", TokenKind.DEC_INTEGER, 0, 2),
        Token("*", TokenKind.OPERATOR, 0, 2),
        Token("_", TokenKind.IDENTIFIER, 0, 3),
    ]

    assert result1 == [
        Token("123", TokenKind.DEC_INTEGER, 0, 2),
        Token("*", TokenKind.OPERATOR, 0, 2),
        Token("f", TokenKind.IDENTIFIER, 0, 3),
    ]

    assert result2 == [
        Token("1234", TokenKind.DEC_INTEGER, 0, 4),
        Token("*", TokenKind.OPERATOR, 0, 4),
        Token("e_00", TokenKind.IDENTIFIER, 0, 8),
    ]

    assert result3 == [
        Token("1000.500", TokenKind.DEC_FLOAT, 0, 8),
        Token("*", TokenKind.OPERATOR, 0, 8),
        Token("r_ac", TokenKind.IDENTIFIER, 0, 12),
    ]


def test_lexer_tokenizes_valid_dec_float_literal_successfully():
    result0 = Lexer("0123.456789").lex()
    result1 = Lexer(".00").lex()
    result2 = Lexer(".12_34").lex()
    result3 = Lexer(".12_34e-100").lex()
    result4 = Lexer("1_234e00").lex()
    result5 = Lexer("1234.").lex()
    result6 = Lexer("1234.e-56789").lex()
    result7 = Lexer("12_34.5_67e+8_900").lex()
    result8 = Lexer("00.1_23456_789").lex()
    assert result0 == [Token("0123.456789", TokenKind.DEC_FLOAT, 0, 10)]
    assert result1 == [Token("0.00", TokenKind.DEC_FLOAT, 0, 2)]
    assert result2 == [Token("0.1234", TokenKind.DEC_FLOAT, 0, 5)]
    assert result3 == [Token("0.1234e-100", TokenKind.DEC_FLOAT, 0, 10)]
    assert result4 == [Token("1234e00", TokenKind.DEC_FLOAT, 0, 7)]
    assert result5 == [Token("1234.0", TokenKind.DEC_FLOAT, 0, 4)]
    assert result6 == [Token("1234.0e-56789", TokenKind.DEC_FLOAT, 0, 11)]
    assert result7 == [Token("1234.567e+8900", TokenKind.DEC_FLOAT, 0, 16)]
    assert result8 == [Token("00.123456789", TokenKind.DEC_FLOAT, 0, 13)]


def test_lexer_tokenizes_valid_code_that_looks_like_dec_float_literal_successfully():
    result0 = Lexer("12_34.e_00").lex()
    result1 = Lexer("12_34.f100").lex()
    result2 = Lexer("12_34e_00").lex()

    assert result0 == [
        Token("1234", TokenKind.DEC_INTEGER, 0, 4),
        Token(".", TokenKind.DELIMITER, 0, 5),
        Token("e_00", TokenKind.IDENTIFIER, 0, 9),
    ]

    assert result1 == [
        Token("1234", TokenKind.DEC_INTEGER, 0, 4),
        Token(".", TokenKind.DELIMITER, 0, 5),
        Token("f100", TokenKind.IDENTIFIER, 0, 9),
    ]

    assert result2 == [
        Token("1234", TokenKind.DEC_INTEGER, 0, 4),
        Token("*", TokenKind.OPERATOR, 0, 4),
        Token("e_00", TokenKind.IDENTIFIER, 0, 8),
    ]


def test_lexer_fails_with_consecutive_underscores_in_dec_float_literal():
    lexer0 = Lexer("1_234.0__5")
    lexer1 = Lexer(".111__0")
    lexer2 = Lexer("1_23.e-4__5")
    lexer3 = Lexer("1_23.100e-4__5")

    with raises(LexerError) as exc_info0:
        lexer0.lex()

    with raises(LexerError) as exc_info1:
        lexer1.lex()

    with raises(LexerError) as exc_info2:
        lexer2.lex()

    with raises(LexerError) as exc_info3:
        lexer3.lex()

    assert (exc_info0.value.message, exc_info0.value.row, exc_info0.value.column) == (
        "Unexpected consecutive underscores in floating point literal",
        0,
        8,
    )

    assert (exc_info1.value.message, exc_info1.value.row, exc_info1.value.column) == (
        "Unexpected consecutive underscores in floating point literal",
        0,
        5,
    )

    assert (exc_info2.value.message, exc_info2.value.row, exc_info2.value.column) == (
        "Unexpected consecutive underscores in floating point literal",
        0,
        9,
    )

    assert (exc_info3.value.message, exc_info3.value.row, exc_info3.value.column) == (
        "Unexpected consecutive underscores in floating point literal",
        0,
        12,
    )


def test_lexer_fails_with_coefficient_literal_on_non_dec_numeric_literal():
    lexer0 = Lexer("0b1_110f")
    lexer1 = Lexer("0x1234fereef")
    lexer2 = Lexer("0o23_347good")

    with raises(LexerError) as exc_info0:
        lexer0.lex()

    with raises(LexerError) as exc_info1:
        lexer1.lex()

    with raises(LexerError) as exc_info2:
        lexer2.lex()

    assert (exc_info0.value.message, exc_info0.value.row, exc_info0.value.column) == (
        "Encountered invalid coefficient literal: '0b1110f'",
        0,
        7,
    )

    assert (exc_info1.value.message, exc_info1.value.row, exc_info1.value.column) == (
        "Encountered invalid coefficient literal: '0x1234fereef'",
        0,
        11,
    )

    assert (exc_info2.value.message, exc_info2.value.row, exc_info2.value.column) == (
        "Encountered invalid coefficient literal: '0o23347good'",
        0,
        11,
    )


def test_lexer_tokenizes_valid_dec_imaginary_literal_successfully():
    result0 = Lexer("1_234.0_5im").lex()
    result1 = Lexer("1_234im").lex()
    assert result0 == [Token("1234.05", TokenKind.DEC_FLOAT_IMAG, 0, 10)]
    assert result1 == [Token("1234", TokenKind.DEC_INTEGER_IMAG, 0, 6)]


def test_lexer_tokenizes_valid_operator_successfully():
    result0 = Lexer("+").lex()
    result1 = Lexer("-").lex()
    result2 = Lexer("/").lex()
    result3 = Lexer("*").lex()
    result4 = Lexer("//").lex()
    result5 = Lexer("%").lex()
    result6 = Lexer("<<").lex()
    result8 = Lexer(">>").lex()
    result9 = Lexer("&").lex()
    result10 = Lexer("|").lex()
    result11 = Lexer("^").lex()
    result12 = Lexer("~").lex()
    result13 = Lexer("<").lex()
    result14 = Lexer(">").lex()
    result15 = Lexer("<=").lex()
    result16 = Lexer(">=").lex()
    result17 = Lexer("==").lex()
    result18 = Lexer("!=").lex()
    result19 = Lexer("||").lex()
    result20 = Lexer("**").lex()
    result21 = Lexer("²").lex()
    result22 = Lexer("√").lex()

    assert result0 == [Token("+", TokenKind.OPERATOR, 0, 0)]
    assert result1 == [Token("-", TokenKind.OPERATOR, 0, 0)]
    assert result2 == [Token("/", TokenKind.OPERATOR, 0, 0)]
    assert result3 == [Token("*", TokenKind.OPERATOR, 0, 0)]
    assert result4 == [Token("//", TokenKind.OPERATOR, 0, 1)]
    assert result5 == [Token("%", TokenKind.OPERATOR, 0, 0)]
    assert result6 == [Token("<<", TokenKind.OPERATOR, 0, 1)]
    assert result8 == [Token(">>", TokenKind.OPERATOR, 0, 1)]
    assert result9 == [Token("&", TokenKind.OPERATOR, 0, 0)]
    assert result10 == [Token("|", TokenKind.OPERATOR, 0, 0)]
    assert result11 == [Token("^", TokenKind.OPERATOR, 0, 0)]
    assert result12 == [Token("~", TokenKind.OPERATOR, 0, 0)]
    assert result13 == [Token("<", TokenKind.OPERATOR, 0, 0)]
    assert result14 == [Token(">", TokenKind.OPERATOR, 0, 0)]
    assert result15 == [Token("<=", TokenKind.OPERATOR, 0, 1)]
    assert result16 == [Token(">=", TokenKind.OPERATOR, 0, 1)]
    assert result17 == [Token("==", TokenKind.OPERATOR, 0, 1)]
    assert result18 == [Token("!=", TokenKind.OPERATOR, 0, 1)]
    assert result19 == [Token("||", TokenKind.OPERATOR, 0, 1)]
    assert result20 == [Token("**", TokenKind.OPERATOR, 0, 1)]
    assert result21 == [Token("²", TokenKind.OPERATOR, 0, 0)]
    assert result22 == [Token("√", TokenKind.OPERATOR, 0, 0)]


def test_lexer_tokenizes_valid_delimiter_successfully():
    result0 = Lexer("(").lex()
    result1 = Lexer(")").lex()
    result2 = Lexer("[").lex()
    result3 = Lexer("]").lex()
    result4 = Lexer("{").lex()
    result5 = Lexer("}").lex()
    result6 = Lexer(",").lex()
    result8 = Lexer(":").lex()
    result9 = Lexer(".").lex()
    result10 = Lexer(";").lex()
    result11 = Lexer("@").lex()
    result12 = Lexer("=").lex()
    result13 = Lexer("->").lex()
    result14 = Lexer("+=").lex()
    result15 = Lexer("-=").lex()
    result16 = Lexer("*=").lex()
    result17 = Lexer("/=").lex()
    result18 = Lexer("//=").lex()
    result19 = Lexer("%=").lex()
    result20 = Lexer("@=").lex()
    result21 = Lexer("&=").lex()
    result22 = Lexer("|=").lex()
    result23 = Lexer("^=").lex()
    result24 = Lexer(">>=").lex()
    result25 = Lexer("<<=").lex()
    result26 = Lexer("||=").lex()

    assert result0 == [Token("(", TokenKind.DELIMITER, 0, 0)]
    assert result1 == [Token(")", TokenKind.DELIMITER, 0, 0)]
    assert result2 == [Token("[", TokenKind.DELIMITER, 0, 0)]
    assert result3 == [Token("]", TokenKind.DELIMITER, 0, 0)]
    assert result4 == [Token("{", TokenKind.DELIMITER, 0, 0)]
    assert result5 == [Token("}", TokenKind.DELIMITER, 0, 0)]
    assert result6 == [Token(",", TokenKind.DELIMITER, 0, 0)]
    assert result8 == [Token(":", TokenKind.DELIMITER, 0, 0)]
    assert result9 == [Token(".", TokenKind.DELIMITER, 0, 0)]
    assert result10 == [Token(";", TokenKind.DELIMITER, 0, 0)]
    assert result11 == [Token("@", TokenKind.DELIMITER, 0, 0)]
    assert result12 == [Token("=", TokenKind.DELIMITER, 0, 0)]
    assert result13 == [Token("->", TokenKind.DELIMITER, 0, 1)]
    assert result14 == [Token("+=", TokenKind.DELIMITER, 0, 1)]
    assert result15 == [Token("-=", TokenKind.DELIMITER, 0, 1)]
    assert result16 == [Token("*=", TokenKind.DELIMITER, 0, 1)]
    assert result17 == [Token("/=", TokenKind.DELIMITER, 0, 1)]
    assert result18 == [Token("//=", TokenKind.DELIMITER, 0, 2)]
    assert result19 == [Token("%=", TokenKind.DELIMITER, 0, 1)]
    assert result20 == [Token("@=", TokenKind.DELIMITER, 0, 1)]
    assert result21 == [Token("&=", TokenKind.DELIMITER, 0, 1)]
    assert result22 == [Token("|=", TokenKind.DELIMITER, 0, 1)]
    assert result23 == [Token("^=", TokenKind.DELIMITER, 0, 1)]
    assert result24 == [Token(">>=", TokenKind.DELIMITER, 0, 2)]
    assert result25 == [Token("<<=", TokenKind.DELIMITER, 0, 2)]
    assert result26 == [Token("||=", TokenKind.DELIMITER, 0, 2)]


def test_lexer_fails_with_single_exclamation_mark():
    lexer = Lexer('!')
    with raises(LexerError) as exc_info:
        lexer.lex()

    assert (exc_info.value.message, exc_info.value.row, exc_info.value.column) == (
        "Encountered unexpected character: '!'",
        0,
        0,
    )


def test_lexer_skips_comment():
    result0 = Lexer("# hello world!\n").lex()
    result1 = Lexer("# dhdgsdgjf,adtw%$#@5C%^@VY2;P'K9(").lex()
    result2 = Lexer("#").lex()

    assert result0 == [Token("", TokenKind.NEWLINE, 1, -1)]
    assert result1 == []
    assert result2 == []


def test_lexer_continues_on_valid_line_continuation():
    result = Lexer(r"""\
    """).lex()
    assert result == []


def test_lexer_fails_on_invalid_line_continuation():
    lexer0 = Lexer(r"\    \n")
    lexer1 = Lexer(r"\x")

    with raises(LexerError) as exc_info0:
        lexer0.lex()

    with raises(LexerError) as exc_info1:
        lexer1.lex()

    assert (exc_info0.value.message, exc_info0.value.row, exc_info0.value.column) == (
        "Unexpected character after line continuation character: ' '",
        0,
        0,
    )

    assert (exc_info1.value.message, exc_info1.value.row, exc_info1.value.column) == (
        "Unexpected character after line continuation character: 'x'",
        0,
        0,
    )


def test_lexer_tokenizes_keywords_successfully():
    result = Lexer(
        "False None True and as assert async await break class continue def del elif else except "
        "finally for from global if import in is lambda nonlocal not or pass raise return try "
        "while with yield const ref ptr val match let var enum true false interface where macro "
        "typealias"
    ).lex()

    assert result == [
        Token("False", TokenKind.KEYWORD, 0, 4),
        Token("None", TokenKind.KEYWORD, 0, 9),
        Token("True", TokenKind.KEYWORD, 0, 14),
        Token("and", TokenKind.KEYWORD, 0, 18),
        Token("as", TokenKind.KEYWORD, 0, 21),
        Token("assert", TokenKind.KEYWORD, 0, 28),
        Token("async", TokenKind.KEYWORD, 0, 34),
        Token("await", TokenKind.KEYWORD, 0, 40),
        Token("break", TokenKind.KEYWORD, 0, 46),
        Token("class", TokenKind.KEYWORD, 0, 52),
        Token("continue", TokenKind.KEYWORD, 0, 61),
        Token("def", TokenKind.KEYWORD, 0, 65),
        Token("del", TokenKind.KEYWORD, 0, 69),
        Token("elif", TokenKind.KEYWORD, 0, 74),
        Token("else", TokenKind.KEYWORD, 0, 79),
        Token("except", TokenKind.KEYWORD, 0, 86),
        Token("finally", TokenKind.KEYWORD, 0, 94),
        Token("for", TokenKind.KEYWORD, 0, 98),
        Token("from", TokenKind.KEYWORD, 0, 103),
        Token("global", TokenKind.KEYWORD, 0, 110),
        Token("if", TokenKind.KEYWORD, 0, 113),
        Token("import", TokenKind.KEYWORD, 0, 120),
        Token("in", TokenKind.KEYWORD, 0, 123),
        Token("is", TokenKind.KEYWORD, 0, 126),
        Token("lambda", TokenKind.KEYWORD, 0, 133),
        Token("nonlocal", TokenKind.KEYWORD, 0, 142),
        Token("not", TokenKind.KEYWORD, 0, 146),
        Token("or", TokenKind.KEYWORD, 0, 149),
        Token("pass", TokenKind.KEYWORD, 0, 154),
        Token("raise", TokenKind.KEYWORD, 0, 160),
        Token("return", TokenKind.KEYWORD, 0, 167),
        Token("try", TokenKind.KEYWORD, 0, 171),
        Token("while", TokenKind.KEYWORD, 0, 177),
        Token("with", TokenKind.KEYWORD, 0, 182),
        Token("yield", TokenKind.KEYWORD, 0, 188),
        Token("const", TokenKind.KEYWORD, 0, 194),
        Token("ref", TokenKind.KEYWORD, 0, 198),
        Token("ptr", TokenKind.KEYWORD, 0, 202),
        Token("val", TokenKind.KEYWORD, 0, 206),
        Token("match", TokenKind.KEYWORD, 0, 212),
        Token("let", TokenKind.KEYWORD, 0, 216),
        Token("var", TokenKind.KEYWORD, 0, 220),
        Token("enum", TokenKind.KEYWORD, 0, 225),
        Token("true", TokenKind.KEYWORD, 0, 230),
        Token("false", TokenKind.KEYWORD, 0, 236),
        Token("interface", TokenKind.KEYWORD, 0, 246),
        Token("where", TokenKind.KEYWORD, 0, 252),
        Token("macro", TokenKind.KEYWORD, 0, 258),
        Token("typealias", TokenKind.KEYWORD, 0, 268),
    ]


def test_lexer_tokenizes_valid_indentations_successfully():
    # Indentation with spaces
    lexer0 = Lexer("name \n    age \n        gender")
    result0 = lexer0.lex()

    # Indentation with tabs
    lexer1 = Lexer("name \n\t\tage \n\t\t\t\tgender\nhello")
    result1 = lexer1.lex()

    # Indentation in nested brackets
    lexer2 = Lexer("name \n\t(age \n{\n\t\n\t\tgender\n} try)\n\thello")
    result2 = lexer2.lex()

    # Unmatched indentation for parentheses with block inside
    lexer3 = Lexer(
        "name (\r\n"
        "\t\tlambda:\n"
        "\t\t\t\tname, match (x, y): \t\n"
        "\t\t\t\t\t\tage)"
    )
    result3 = lexer3.lex()

    # Matched indentation for parentheses with block inside
    lexer4 = Lexer(
        "name (\n"
        " 1_000_234, lambda:\n"
        "   name, match (x, y): \t\r\n"
        "     age   \n"
        ")"
    )
    result4 = lexer4.lex()

    # Matched indentation for parentheses with block inside
    lexer5 = Lexer(
        "name (\n"
        "  1_000_234\n"
        "    lambda:\n"
        "          \n"
        "        ( name, lambda: \t\n"
        "            age\r\n"
        "            hello)\n"
        "        gem)"
    )
    result5 = lexer5.lex()

    # Unmatched indentation for parentheses with block inside, but not currently in block
    lexer6 = Lexer(
        "name (\n"
        "  lambda:\n"
        "    name, match (x, y): \n"
        "      age\n"
        "      \r\n"
        "  { lambda: x})"
    )
    result6 = lexer6.lex()

    assert result0 == [
        Token("name", TokenKind.IDENTIFIER, 0, 3),
        Token("", TokenKind.INDENT, 1, 3),
        Token("age", TokenKind.IDENTIFIER, 1, 6),
        Token("", TokenKind.INDENT, 2, 7),
        Token("gender", TokenKind.IDENTIFIER, 2, 13),
        Token("", TokenKind.DEDENT, 2, 13),
        Token("", TokenKind.DEDENT, 2, 13),
    ]
    assert (lexer0.indent_factor, lexer0.indent_space_type) == (4, IndentSpaceKind.SPACE)

    assert result1 == [
        Token("name", TokenKind.IDENTIFIER, 0, 3),
        Token("", TokenKind.INDENT, 1, 1),
        Token("age", TokenKind.IDENTIFIER, 1, 4),
        Token("", TokenKind.INDENT, 2, 3),
        Token("gender", TokenKind.IDENTIFIER, 2, 9),
        Token("", TokenKind.DEDENT, 3, -1),
        Token("", TokenKind.DEDENT, 3, -1),
        Token("hello", TokenKind.IDENTIFIER, 3, 4),
    ]
    assert (lexer1.indent_factor, lexer1.indent_space_type) == (2, IndentSpaceKind.TAB)

    assert result2 == [
        Token("name", TokenKind.IDENTIFIER, 0, 3),
        Token("", TokenKind.INDENT, 1, 0),
        Token("(", TokenKind.DELIMITER, 1, 1),
        Token("age", TokenKind.IDENTIFIER, 1, 4),
        Token("{", TokenKind.DELIMITER, 2, 0),
        Token("gender", TokenKind.IDENTIFIER, 4, 7),
        Token("}", TokenKind.DELIMITER, 5, 0),
        Token("try", TokenKind.KEYWORD, 5, 4),
        Token(")", TokenKind.DELIMITER, 5, 5),
        Token("", TokenKind.NEWLINE, 6, 0),
        Token("hello", TokenKind.IDENTIFIER, 6, 5),
        Token("", TokenKind.DEDENT, 6, 5),
    ]
    assert (lexer2.indent_factor, lexer2.indent_space_type) == (1, IndentSpaceKind.TAB)

    assert result3 == [
        Token("name", TokenKind.IDENTIFIER, 0, 3),
        Token("(", TokenKind.DELIMITER, 0, 5),
        Token("lambda", TokenKind.KEYWORD, 1, 7),
        Token(":", TokenKind.DELIMITER, 1, 8),
        Token("", TokenKind.INDENT, 2, 3),
        Token("name", TokenKind.IDENTIFIER, 2, 7),
        Token(",", TokenKind.DELIMITER, 2, 8),
        Token("match", TokenKind.KEYWORD, 2, 14),
        Token("(", TokenKind.DELIMITER, 2, 16),
        Token("x", TokenKind.IDENTIFIER, 2, 17),
        Token(",", TokenKind.DELIMITER, 2, 18),
        Token("y", TokenKind.IDENTIFIER, 2, 20),
        Token(")", TokenKind.DELIMITER, 2, 21),
        Token(":", TokenKind.DELIMITER, 2, 22),
        Token("", TokenKind.INDENT, 3, 5),
        Token("age", TokenKind.IDENTIFIER, 3, 8),
        Token("", TokenKind.DEDENT, 3, 9),
        Token("", TokenKind.DEDENT, 3, 9),
        Token(")", TokenKind.DELIMITER, 3, 9)
    ]
    assert (lexer3.indent_factor, lexer3.indent_space_type) == (2, IndentSpaceKind.TAB)

    assert result4 == [
        Token("name", TokenKind.IDENTIFIER, 0, 3),
        Token("(", TokenKind.DELIMITER, 0, 5),
        Token("1000234", TokenKind.DEC_INTEGER, 1, 9),
        Token(",", TokenKind.DELIMITER, 1, 10),
        Token("lambda", TokenKind.KEYWORD, 1, 17),
        Token(":", TokenKind.DELIMITER, 1, 18),
        Token("", TokenKind.INDENT, 2, 2),
        Token("name", TokenKind.IDENTIFIER, 2, 6),
        Token(",", TokenKind.DELIMITER, 2, 7),
        Token("match", TokenKind.KEYWORD, 2, 13),
        Token("(", TokenKind.DELIMITER, 2, 15),
        Token("x", TokenKind.IDENTIFIER, 2, 16),
        Token(",", TokenKind.DELIMITER, 2, 17),
        Token("y", TokenKind.IDENTIFIER, 2, 19),
        Token(")", TokenKind.DELIMITER, 2, 20),
        Token(":", TokenKind.DELIMITER, 2, 21),
        Token("", TokenKind.INDENT, 3, 4),
        Token("age", TokenKind.IDENTIFIER, 3, 7),
        Token("", TokenKind.DEDENT, 4, -1),
        Token("", TokenKind.DEDENT, 4, -1),
        Token(")", TokenKind.DELIMITER, 4, 0)
    ]
    assert (lexer4.indent_factor, lexer4.indent_space_type) == (2, IndentSpaceKind.SPACE)

    assert result5 == [
        Token("name", TokenKind.IDENTIFIER, 0, 3),
        Token("(", TokenKind.DELIMITER, 0, 5),
        Token("1000234", TokenKind.DEC_INTEGER, 1, 10),
        Token("lambda", TokenKind.KEYWORD, 2, 9),
        Token(":", TokenKind.DELIMITER, 2, 10),
        Token("", TokenKind.INDENT, 4, 7),
        Token("(", TokenKind.DELIMITER, 4, 8),
        Token("name", TokenKind.IDENTIFIER, 4, 13),
        Token(",", TokenKind.DELIMITER, 4, 14),
        Token("lambda", TokenKind.KEYWORD, 4, 21),
        Token(":", TokenKind.DELIMITER, 4, 22),
        Token("", TokenKind.INDENT, 5, 11),
        Token("age", TokenKind.IDENTIFIER, 5, 14),
        Token("", TokenKind.NEWLINE, 6, 11),
        Token("hello", TokenKind.IDENTIFIER, 6, 16),
        Token("", TokenKind.DEDENT, 6, 17),
        Token(")", TokenKind.DELIMITER, 6, 17),
        Token("", TokenKind.NEWLINE, 7, 7),
        Token("gem", TokenKind.IDENTIFIER, 7, 10),
        Token("", TokenKind.DEDENT, 7, 11),
        Token(")", TokenKind.DELIMITER, 7, 11)
    ]
    assert (lexer5.indent_factor, lexer5.indent_space_type) == (4, IndentSpaceKind.SPACE)

    assert result6 == [
        Token("name", TokenKind.IDENTIFIER, 0, 3),
        Token("(", TokenKind.DELIMITER, 0, 5),
        Token("lambda", TokenKind.KEYWORD, 1, 7),
        Token(":", TokenKind.DELIMITER, 1, 8),
        Token("", TokenKind.INDENT, 2, 3),
        Token("name", TokenKind.IDENTIFIER, 2, 7),
        Token(",", TokenKind.DELIMITER, 2, 8),
        Token("match", TokenKind.KEYWORD, 2, 14),
        Token("(", TokenKind.DELIMITER, 2, 16),
        Token("x", TokenKind.IDENTIFIER, 2, 17),
        Token(",", TokenKind.DELIMITER, 2, 18),
        Token("y", TokenKind.IDENTIFIER, 2, 20),
        Token(")", TokenKind.DELIMITER, 2, 21),
        Token(":", TokenKind.DELIMITER, 2, 22),
        Token("", TokenKind.INDENT, 3, 5),
        Token("age", TokenKind.IDENTIFIER, 3, 8),
        Token("", TokenKind.DEDENT, 5, 1),
        Token("", TokenKind.DEDENT, 5, 1),
        Token("{", TokenKind.DELIMITER, 5, 2),
        Token("lambda", TokenKind.KEYWORD, 5, 9),
        Token(":", TokenKind.DELIMITER, 5, 10),
        Token("x", TokenKind.IDENTIFIER, 5, 12),
        Token("}", TokenKind.DELIMITER, 5, 13),
        Token(")", TokenKind.DELIMITER, 5, 14)
    ]
    assert (lexer6.indent_factor, lexer6.indent_space_type) == (2, IndentSpaceKind.SPACE)


def test_lexer_fails_on_invalid_indentation():
    # Mixed space types in indentation
    lexer0 = Lexer(
        "lambda *args:\n"
        "\t\t[1, 2, 3]\r\n"
        "\t\t  0x110"
    )

    # Wrong number of spaces in indent
    lexer1 = Lexer(
        "lambda *args:\n"
        "\t\t[1, 2, 3]\r\n"
        "\t\t\t0x110"
    )

    # Wrong number of spaces in dedent
    lexer2 = Lexer(
        "lambda *args:\n"
        "\t\t[1, 2, 3]\r\n"
        "\t0x110"
    )

    # Mixed space types in separate indentation
    lexer3 = Lexer(
        "lambda *args:\n"
        "\t\t[1, 2, 3]\r\n"
        "    0x110"
    )

    with raises(LexerError) as exc_info0:
        lexer0.lex()

    with raises(LexerError) as exc_info1:
        lexer1.lex()

    with raises(LexerError) as exc_info2:
        lexer2.lex()

    with raises(LexerError) as exc_info3:
        lexer3.lex()

    assert (exc_info0.value.message, exc_info0.value.row, exc_info0.value.column) == (
        "Unexpected mix of different types of spaces in indentation",
        2,
        3,
    )

    assert (exc_info1.value.message, exc_info1.value.row, exc_info1.value.column) == (
        "Expected an indent of 2 spaces",
        2,
        2,
    )

    assert (exc_info2.value.message, exc_info2.value.row, exc_info2.value.column) == (
        "Unexpected number of spaces in dedent",
        2,
        0,
    )

    assert (exc_info3.value.message, exc_info3.value.row, exc_info3.value.column) == (
        "Unexpected mix of different types of spaces in indentation",
        2,
        3,
    )
