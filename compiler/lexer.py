from enum import Enum


class ValidTokens:
    identifier_char = [

    ]
    keywords = [
        'False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await',
        'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except',
        'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is',
        'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return',
        'try', 'while', 'with', 'yield',
        'const', 'ref', 'ptr', 'val', 'match', 'let', 'var', 'enum', 'true',
        'false', 'interface', 'where'
    ]


class Token:
    def __init__(self, data, kind, row, column):
        self.data = data
        self.kind = kind
        self.row = row
        self.column = column


class TokenKind(Enum):
    IDENTIFIER = 1
    NEWLINE = 1
    INTEGER_DEC = 2
    FLOAT_DEC = 3


class LexerError(Exception):
    def __init__(self, message, parser):
        super().__init__(message)
        self.row = parser.row
        self.column = parser.column


class Lexer:
    def __init__(self, code):
        self.code = code
        self.code_length = len(code)
        self.cursor = -1
        self.row = -1
        self.column = -1
        self.indentation = 0
        self.valid_tokens = ValidTokens

    def eat_char(self):
        # Check if there is a character to be consumed.
        if self.cursor >= self.code_length:
            return None

        self.cursor += 1
        return self.code[self.cursor]

    def peek_char(self):
        # Check if there is a character to be consumed.
        if self.cursor >= self.code_length:
            return None

        return self.code[self.cursor + 1]

    def is_identifier(char):
        num = ord(char)
        return (
            (64 < num < 91) or   # A-Z
            (96 < num < 123) or  # a-z
            (47 < num < 58)      # 0-9
            (char == '_')        # _
        )

    def lex(self):
        char = self.eat_char()
        tokens = []

        while char:
            if char == '\r':
                if self.peek_char() == '\n':
                    self.eat_char()
                tokens.append(Token('', TokenKind.NEWLINE, self))

            elif char == '\n':
                tokens.append(Token('', TokenKind.NEWLINE, self))

            elif Lexer.is_identifier(char):
                token = char

                while Lexer.is_identifier(self.peek_char()):
                    token.append(self.eat_char())

                tokens.append(Token(token, TokenKind.IDENTIFIER, self))

            char = self.eat_char()

        return tokens

    def lex_identifier(): pass

    def lex_integer_dec(): pass
