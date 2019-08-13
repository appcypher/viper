from compiler.lexer import Lexer, Token, TokenKind, LexerError
from pytest import raises


def test_lexer_tokenizes_identifier_that_starts_with_underscore_as_identifier():
    result = Lexer(r"_hello").lex()
    assert result == [Token(r"_hello", TokenKind.IDENTIFIER, 0, 5)]


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
    result2 = Lexer("01_23456_789").lex()
    result3 = Lexer("5_37450_899").lex()
    assert result0 == [Token("0123456789", TokenKind.DEC_INTEGER, 0, 9)]
    assert result1 == [Token("123456789", TokenKind.DEC_INTEGER, 0, 8)]
    assert result2 == [Token("0123456789", TokenKind.DEC_INTEGER, 0, 11)]
    assert result3 == [Token("537450899", TokenKind.DEC_INTEGER, 0, 10)]


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


def test_lexer_fails_with_trailing_underscore_in_integer_literal():
    lexer0 = Lexer("0o1_000_")
    lexer1 = Lexer("0b1_000_")
    lexer2 = Lexer("0x1_000_")
    lexer3 = Lexer("1_000_")
    lexer4 = Lexer("0o_")
    lexer5 = Lexer("0b_")
    lexer6 = Lexer("0x_")

    with raises(LexerError) as exc_info0:
        lexer0.lex()

    with raises(LexerError) as exc_info1:
        lexer1.lex()

    with raises(LexerError) as exc_info2:
        lexer2.lex()

    with raises(LexerError) as exc_info3:
        lexer3.lex()

    with raises(LexerError) as exc_info4:
        lexer4.lex()

    with raises(LexerError) as exc_info5:
        lexer5.lex()

    with raises(LexerError) as exc_info6:
        lexer6.lex()

    assert (exc_info0.value.message, exc_info0.value.row, exc_info0.value.column) == (
        "Unexpected trailing underscore in integer literal",
        0,
        7,
    )

    assert (exc_info1.value.message, exc_info1.value.row, exc_info1.value.column) == (
        "Unexpected trailing underscore in integer literal",
        0,
        7,
    )

    assert (exc_info2.value.message, exc_info2.value.row, exc_info2.value.column) == (
        "Unexpected trailing underscore in integer literal",
        0,
        7,
    )

    assert (exc_info3.value.message, exc_info3.value.row, exc_info3.value.column) == (
        "Unexpected trailing underscore in integer literal",
        0,
        5,
    )

    assert (exc_info4.value.message, exc_info4.value.row, exc_info4.value.column) == (
        "Unexpected trailing underscore in integer literal",
        0,
        2,
    )

    assert (exc_info5.value.message, exc_info5.value.row, exc_info5.value.column) == (
        "Unexpected trailing underscore in integer literal",
        0,
        2,
    )

    assert (exc_info6.value.message, exc_info6.value.row, exc_info6.value.column) == (
        "Unexpected trailing underscore in integer literal",
        0,
        2,
    )

