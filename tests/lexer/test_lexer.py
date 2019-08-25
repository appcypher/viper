from compiler.lexer import Lexer, Token, TokenKind, LexerError
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
    assert result0 == [Token("0123456789", TokenKind.DEC_INTEGER, 0, 9)]
    assert result1 == [Token("123456789", TokenKind.DEC_INTEGER, 0, 8)]
    assert result2 == [Token("0133456789", TokenKind.DEC_INTEGER, 0, 11)]
    assert result3 == [Token("53745099", TokenKind.DEC_INTEGER, 0, 9)]


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
    result2 = Lexer("*").lex()
    result3 = Lexer("**").lex()
    result4 = Lexer("/").lex()
    result5 = Lexer("//").lex()
    result6 = Lexer("%").lex()
    result8 = Lexer("<<").lex()
    result9 = Lexer(">>").lex()
    result10 = Lexer("&").lex()
    result11 = Lexer("|").lex()
    result12 = Lexer("^").lex()
    result13 = Lexer("~").lex()
    result14 = Lexer("<").lex()
    result15 = Lexer(">").lex()
    result16 = Lexer("<=").lex()
    result17 = Lexer(">=").lex()
    result18 = Lexer("==").lex()
    result19 = Lexer("!=").lex()

    assert result0 == [Token("+", TokenKind.OPERATOR, 0, 0)]
    assert result1 == [Token("-", TokenKind.OPERATOR, 0, 0)]
    assert result2 == [Token("*", TokenKind.OPERATOR, 0, 0)]
    assert result3 == [Token("**", TokenKind.OPERATOR, 0, 1)]
    assert result4 == [Token("/", TokenKind.OPERATOR, 0, 0)]
    assert result5 == [Token("//", TokenKind.OPERATOR, 0, 1)]
    assert result6 == [Token("%", TokenKind.OPERATOR, 0, 0)]
    assert result8 == [Token("<<", TokenKind.OPERATOR, 0, 1)]
    assert result9 == [Token(">>", TokenKind.OPERATOR, 0, 1)]
    assert result10 == [Token("&", TokenKind.OPERATOR, 0, 0)]
    assert result11 == [Token("|", TokenKind.OPERATOR, 0, 0)]
    assert result12 == [Token("^", TokenKind.OPERATOR, 0, 0)]
    assert result13 == [Token("~", TokenKind.OPERATOR, 0, 0)]
    assert result14 == [Token("<", TokenKind.OPERATOR, 0, 0)]
    assert result15 == [Token(">", TokenKind.OPERATOR, 0, 0)]
    assert result16 == [Token("<=", TokenKind.OPERATOR, 0, 1)]
    assert result17 == [Token(">=", TokenKind.OPERATOR, 0, 1)]
    assert result18 == [Token("==", TokenKind.OPERATOR, 0, 1)]
    assert result19 == [Token("!=", TokenKind.OPERATOR, 0, 1)]


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
    result26 = Lexer("**=").lex()

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
    assert result26 == [Token("**=", TokenKind.DELIMITER, 0, 2)]


def test_lexer_fails_with_single_exclamation_mark():
    lexer = Lexer('!')
    with raises(LexerError) as exc_info:
        lexer.lex()

    assert (exc_info.value.message, exc_info.value.row, exc_info.value.column) == (
        "Encountered unexpected character: '!'",
        0,
        0,
    )

def test_lexer_tokenizes_():
    result0 = Lexer("(").lex()

    assert result0 == [Token("(", TokenKind.DELIMITER, 0, 0)]
