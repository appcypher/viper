from compiler.lexer import Lexer, Token, TokenKind, LexerError
from pytest import raises


def test_lexer_tokenizes_identifier_that_starts_with_underscore_as_identifier():
    lexer = Lexer(r"_hello")
    result = lexer.lex()
    assert result == [Token(r"_hello", TokenKind.IDENTIFIER, 0, 5)]


def test_lexer_tokenizes_identifier_with_digits_in_middle_as_identifier():
    lexer = Lexer(r"_hello88_")
    result = lexer.lex()
    assert result == [Token("_hello88_", TokenKind.IDENTIFIER, 0, 8)]


def test_lexer_tokenizes_single_character_as_identifier():
    lexer = Lexer("h")
    result = lexer.lex()
    assert result == [Token(r"h", TokenKind.IDENTIFIER, 0, 0)]


def test_lexer_tokenizes_valid_newline_successfully():
    lexer = Lexer("\r\n\n")
    result = lexer.lex()
    assert result == [
        Token("", TokenKind.NEWLINE, 1, -1),
        Token("", TokenKind.NEWLINE, 2, -1),
    ]


def test_lexer_tokenizes_underscore_as_identifier():
    lexer = Lexer("_")
    result = lexer.lex()
    assert result == [Token(r"_", TokenKind.IDENTIFIER, 0, 0)]


def test_lexer_tokenizes_valid_single_quote_short_string_successfully():
    lexer = Lexer(r"'erCA63y8hbb 54^58* (@$Q#3qDSHHScTw62-+'")
    result = lexer.lex()
    assert result == [
        Token(r"erCA63y8hbb 54^58* (@$Q#3qDSHHScTw62-+", TokenKind.STRING, 0, 39)
    ]


def test_lexer_tokenizes_valid_double_quote_short_string_successfully():
    lexer = Lexer(r'"erCA63y8hbb 54^58*(@$Q#3qDSHHScTw62-+"')
    result = lexer.lex()
    assert result == [
        Token(r"erCA63y8hbb 54^58*(@$Q#3qDSHHScTw62-+", TokenKind.STRING, 0, 38)
    ]


def test_lexer_tokenizes_valid_double_char_prefixed_single_quote_short_string_successfully():
    lexer = Lexer(r"fr'erCA63y8hbb 54^58* (@$Q#3qDSHHScTw62-+'")
    result = lexer.lex()
    assert result == [
        Token(
            r"erCA63y8hbb 54^58* (@$Q#3qDSHHScTw62-+", TokenKind.PREFIXED_STRING, 0, 41
        )
    ]


def test_lexer_tokenizes_valid_double_char_prefixed_double_quote_short_string_successfully():
    lexer = Lexer(r'RF"erCA63y8hbb 54^58*(@$Q#3qDSHHScTw62-+"')
    result = lexer.lex()
    assert result == [
        Token(
            r"erCA63y8hbb 54^58*(@$Q#3qDSHHScTw62-+", TokenKind.PREFIXED_STRING, 0, 40
        )
    ]


def test_lexer_tokenizes_valid_single_char_prefixed_double_quote_short_string_successfully():
    lexer = Lexer(r'r"erCA63y8hbb 54^58*(@$Q#3qDSHHScTw62-+"')
    result = lexer.lex()
    assert result == [
        Token(
            r"erCA63y8hbb 54^58*(@$Q#3qDSHHScTw62-+", TokenKind.PREFIXED_STRING, 0, 39
        )
    ]


def test_lexer_tokenizes_valid_empty_short_string_successfully():
    lexer = Lexer(r'""')
    result = lexer.lex()
    assert result == [Token(r"", TokenKind.STRING, 0, 1)]


def test_lexer_fails_with_return_char_in_short_string():
    lexer = Lexer('"\r"')
    with raises(LexerError) as exc_info:
        lexer.lex()

    assert exc_info.type == LexerError
    assert (exc_info.value.row, exc_info.value.column) == (0, 0)


def test_lexer_fails_with_newline_char_in_short_string():
    lexer = Lexer('"\n"')
    with raises(LexerError) as exc_info:
        lexer.lex()

    assert exc_info.type == LexerError
    assert (exc_info.value.message, exc_info.value.row, exc_info.value.column) == (
        "Encountered unexpected newline character",
        0,
        0,
    )


def test_lexer_fails_with_unclosed_delimiter_for_short_string():
    lexer = Lexer('"hello there')
    with raises(LexerError) as exc_info:
        lexer.lex()

    assert exc_info.type == LexerError
    assert (exc_info.value.message, exc_info.value.row, exc_info.value.column) == (
        "Unexpected end of string. Closing delimiter not found",
        0,
        11,
    )


def test_lexer_tokenizes_valid_single_quote_long_string_successfully():
    lexer = Lexer(r"'''erCA63y8hbb 54^58* (@$Q#3qDSHHScTw62-+'''")
    result = lexer.lex()
    assert result == [
        Token(r"erCA63y8hbb 54^58* (@$Q#3qDSHHScTw62-+", TokenKind.STRING, 0, 43)
    ]


def test_lexer_tokenizes_valid_double_quote_long_string_successfully():
    lexer = Lexer(r'"""erCA63y8hbb 54^58*(@$Q#3qDSHHScTw62-+"""')
    result = lexer.lex()
    assert result == [
        Token(r"erCA63y8hbb 54^58*(@$Q#3qDSHHScTw62-+", TokenKind.STRING, 0, 42)
    ]


def test_lexer_tokenizes_valid_double_char_prefixed_single_quote_long_string_successfully():
    lexer = Lexer(r"fr'''erCA63y8hbb 54^58* (@$Q#3qDSHHScTw62-+'''")
    result = lexer.lex()
    assert result == [
        Token(
            r"erCA63y8hbb 54^58* (@$Q#3qDSHHScTw62-+", TokenKind.PREFIXED_STRING, 0, 45
        )
    ]


def test_lexer_tokenizes_valid_double_char_prefixed_double_quote_long_string_successfully():
    lexer = Lexer(r'RF"""erCA63y8hbb 54^58*(@$Q#3qDSHHScTw62-+"""')
    result = lexer.lex()
    assert result == [
        Token(
            r"erCA63y8hbb 54^58*(@$Q#3qDSHHScTw62-+", TokenKind.PREFIXED_STRING, 0, 44
        )
    ]


def test_lexer_tokenizes_valid_single_char_prefixed_double_quote_long_string_successfully():
    lexer = Lexer(r'r"""erCA63y8hbb 54^58*(@$Q#3qDSHHScTw62-+"""')
    result = lexer.lex()
    assert result == [
        Token(
            r"erCA63y8hbb 54^58*(@$Q#3qDSHHScTw62-+", TokenKind.PREFIXED_STRING, 0, 43
        )
    ]


def test_lexer_tokenizes_valid_empty_long_string_successfully():
    lexer = Lexer(r'""""""')
    result = lexer.lex()
    assert result == [Token(r"", TokenKind.STRING, 0, 5)]


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
    lexer = Lexer('"""\n this is a \ndoc #3qDSHHScTw62-+"""')
    result = lexer.lex()
    assert result == [
        Token("\n this is a \ndoc #3qDSHHScTw62-+", TokenKind.STRING, 2, 21)
    ]


def test_lexer_fails_with_unclosed_delimiter_for_long_string():
    lexer = Lexer('"""hello there""')
    with raises(LexerError) as exc_info:
        lexer.lex()

    assert exc_info.type == LexerError
    assert (exc_info.value.message, exc_info.value.row, exc_info.value.column) == (
        "Unexpected end of string. Closing delimiter not found",
        0,
        15,
    )


def test_lexer_tokenizes_with_valid_long_byte_string():
    lexer = Lexer('"""This is spartan 0078#*"""')
    result = lexer.lex()
    assert result == [Token("This is spartan 0078#*", TokenKind.STRING, 0, 27)]


def test_lexer_fails_with_non_ascii_char_in_long_byte_string():
    lexer = Lexer('b"""hello thereΣ"""')
    with raises(LexerError) as exc_info:
        lexer.lex()

    assert exc_info.type == LexerError
    assert (exc_info.value.message, exc_info.value.row, exc_info.value.column) == (
        "Encountered unexpected non-ASCII character: 'Σ'",
        0,
        14,
    )


def test_lexer_fails_with_unclosed_delimiter_for_short_byte_string():
    lexer = Lexer('br"hello there')
    with raises(LexerError) as exc_info:
        lexer.lex()

    assert exc_info.type == LexerError
    assert (exc_info.value.message, exc_info.value.row, exc_info.value.column) == (
        "Unexpected end of string. Closing delimiter not found",
        0,
        13,
    )


def test_lexer_fails_with_unclosed_delimiter_for_long_byte_string():
    lexer = Lexer('b"""hello there""')
    with raises(LexerError) as exc_info:
        lexer.lex()

    assert exc_info.type == LexerError
    assert (exc_info.value.message, exc_info.value.row, exc_info.value.column) == (
        "Unexpected end of string. Closing delimiter not found",
        0,
        16,
    )


def test_lexer_tokenizes_():
    assert True
