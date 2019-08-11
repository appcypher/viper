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
        'var', 'enum', 'true', 'false', 'interface', 'where', 'macro',
        'typealias'
    ]

    def is_Lu(codepoint):
        pass

    def is_identifier_start(codepoint):
        pass

    def is_identifier_remainder(codepoint):
        pass
