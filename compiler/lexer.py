""" Contains Viper's lexer implementation """

from enum import Enum


class ValidTokens:
    """
    Contains some of the legal characters, tokens and keywords allowed by the
    Lexer
    """
    keywords = [
        'False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await',
        'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except',
        'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is',
        'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'try',
        'while', 'with', 'yield', 'const', 'ref', 'ptr', 'val', 'match', 'let',
        'var', 'enum', 'true', 'false', 'interface', 'where', 'macro', 'typealias'
    ]


class Indentation:
    """ Contains a lexer's indentation information """
    def __init__(self):
        self.indent_count = 0
        self.is_space = True
        self.indent_factor = 4


class Token:
    """ Token is a unit extracted """
    def __init__(self, data, kind, row, column):
        self.data = data
        self.kind = kind
        self.row = row
        self.column = column

    def __repr__(self):
        return (f'Token(data="{self.data}", kind={self.kind}, row={self.row}'
                f', column={self.column})')

    def __eq__(self, other):
        return (self.data == other.data and self.kind == other.kind
                and self.row == other.row and self.column == other.column)


class TokenKind(Enum):
    """ The different kinds of token """
    IDENTIFIER = 0
    NEWLINE = 1
    INTEGER_DEC = 2
    FLOAT_DEC = 3
    INDENT = 4
    DEDENT = 5


class LexerError(Exception):
    """ Represents the error the lexer can raise """
    def __init__(self, message, row, column):
        super().__init__(message)
        self.row = row
        self.column = column


class Lexer:
    """ Contains the lexer implementation """
    def __init__(self, code):
        self.code = code
        self.code_length = len(code)
        self.cursor = -1
        self.row = 0
        self.column = -1
        self.indentation = Indentation()
        self.valid_tokens = ValidTokens

    def eat_char(self):
        """
        Returns the next character in code and advances the cursor
        position
        """
        if self.cursor + 1 < self.code_length:
            self.cursor += 1
            return self.code[self.cursor]

        return None

    def peek_char(self):
        """ Peeks at the next character in code """
        if self.cursor + 1 < self.code_length:
            return self.code[self.cursor + 1]

        return None

    def is_identifier_start(char):
        """ Checks if a character has the following pattern: [A-Za-z_] """
        num = ord(char)
        return ((64 < num < 91) or  # A-Z
                (96 < num < 123) or  # a-z
                (char == '_')  # _
                )

    def is_identifier_mid(char):
        """ Checks if a character has the following pattern: [A-Za-z0-9_] """
        num = ord(char)
        return ((64 < num < 91) or  # A-Z
                (96 < num < 123) or  # a-z
                (47 < num < 58) or  # 0-9
                (char == '_')  # _
                )

    def lex(self):
        """ Breaks code string into tokens that the parser can digest """
        char = self.eat_char()
        tokens = []

        # Loops through each character in the code.
        while char:
            row, column = self.row, self.column

            # We check each character in the code and categorize it
            if char == '\r':  # character is a NEWLINE
                if self.peek_char() == '\n':
                    self.eat_char()

                tokens.append(Token('', TokenKind.NEWLINE, row, column))

            elif char == '\n':  # character is a NEWLINE
                tokens.append(Token('', TokenKind.NEWLINE, row, column))

            elif Lexer.is_identifier_start(char):  # character is an IDENTIFIER
                token = char
                peeked_char = self.peek_char()

                while peeked_char and Lexer.is_identifier_mid(peeked_char):
                    token += self.eat_char()

                    # Peek at the next character in code.
                    peeked_char = self.peek_char()

                tokens.append(Token(token, TokenKind.IDENTIFIER, row, column))

            # elif ...:  # ...
            # print('>>>', peeked_char)

            # Consume the next character in code.
            char = self.eat_char()

        return tokens
