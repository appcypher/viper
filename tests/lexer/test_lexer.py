from compiler.lexer import Lexer, Token, TokenKind


def test_lexer_tokenizes_identifier_that_starts_with_underscore_as_identifier(
):
    lexer = Lexer('_hello')
    result = lexer.lex()
    assert result == [Token('_hello', TokenKind.IDENTIFIER, 0, -1)]


def test_lexer_tokenizes_identifier_with_digits_in_middle_as_identifier():
    lexer = Lexer('_hello88_')
    result = lexer.lex()
    assert result == [Token('_hello88_', TokenKind.IDENTIFIER, 0, -1)]


def test_lexer_tokenizes_single_character_as_identifier():
    lexer = Lexer('h')
    result = lexer.lex()
    assert result == [Token('h', TokenKind.IDENTIFIER, 0, -1)]


def test_lexer_tokenizes_underscore_as_identifier():
    lexer = Lexer('_')
    result = lexer.lex()
    assert result == [Token('_', TokenKind.IDENTIFIER, 0, -1)]
