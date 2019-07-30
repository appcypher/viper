from compiler.lexer import (Lexer)

if __name__ == '__main__':
    lexer = Lexer('hello world')
    print(lexer.lex())
