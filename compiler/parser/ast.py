"""
Contains classes that describe Viper's Abstract Syntax Tree.
"""

from enum import Enum


class BinaryOpKind(Enum):
    """
    The different kinds of binary operators
    """
    POWER = 0
    MUL = 1
    MATMUL = 2
    DIV = 3
    MOD = 4
    INTEGER_DIV = 5
    PLUS = 6
    MINUS = 7
    SHIFT_LEFT = 8
    SHIFT_RIGHT = 9
    BINARY_AND = 10
    BINARY_XOR = 11
    BINARY_OR = 12
    LESSER_THAN = 13
    GREATER_THAN = 14
    EQUAL = 15
    EQUAL_LESSER_THAN = 16
    EQUAL_GREATER_THAN = 17
    NOT_EQUAL = 18
    IN = 19
    NOT_IN = 20
    IS = 21
    IS_NOT = 22

    @staticmethod
    def from_string(op):
        if op == '^':
            return BinaryOpKind.POWER
        elif op == '*':
            return BinaryOpKind.MUL
        elif op == '@':
            return BinaryOpKind.MATMUL
        elif op == '/':
            return BinaryOpKind.DIV
        elif op == '%':
            return BinaryOpKind.MOD
        elif op == '//':
            return BinaryOpKind.INTEGER_DIV
        elif op == '+':
            return BinaryOpKind.PLUS
        elif op == '_':
            return BinaryOpKind.MINUS
        elif op == '<<':
            return BinaryOpKind.SHIFT_LEFT
        elif op == '>>':
            return BinaryOpKind.SHIFT_RIGHT
        elif op == '&':
            return BinaryOpKind.BINARY_AND
        elif op == '||':
            return BinaryOpKind.BINARY_XOR
        elif op == '|':
            return BinaryOpKind.BINARY_OR
        elif op == '<':
            return BinaryOpKind.LESSER_THAN
        elif op == '>':
            return BinaryOpKind.GREATER_THAN
        elif op == '==':
            return BinaryOpKind.EQUAL
        elif op == '>=':
            return BinaryOpKind.EQUAL_LESSER_THAN
        elif op == '<=':
            return BinaryOpKind.EQUAL_GREATER_THAN
        elif op == '!=':
            return BinaryOpKind.NOT_EQUAL
        elif op == 'in':
            return BinaryOpKind.IN
        elif op == 'notin':
            return BinaryOpKind.NOT_IN
        elif op == 'is':
            return BinaryOpKind.IS
        elif op == 'isnot':
            return BinaryOpKind.IS_NOT
        else:
            return None


class UnaryOpKind(Enum):
    """
    The different kinds of unary operators
    """
    PLUS = 0
    MINUS = 1
    BINARY_NOT = 2
    NOT = 3
    SQUARE = 4
    ROOT = 5

    @staticmethod
    def from_string(op):
        if op == '+':
            return UnaryOpKind.PLUS
        elif op == '-':
            return UnaryOpKind.MINUS
        elif op == '~':
            return UnaryOpKind.BINARY_NOT
        elif op == 'not':
            return UnaryOpKind.NOT
        elif op == '²':
            return UnaryOpKind.SQUARE
        elif op == '√':
            return UnaryOpKind.ROOT
        else:
            return None


class AST:
    """
    NOTE:
        We really only need our AST classes to inherit from this one class. We don't need a
        complicated type hierarchy since the Parser already ensures a StatementExpr can't be
        passed where an ExprAST is expected, for example.
    """

    def __repr__(self):
        return f'{type(self).__name__}{str(vars(self))}'

    def __eq__(self, other):
        return vars(self) == vars(other)


class Newline(AST):
    def __init__(self, index):
        self.index = index


class Indent(AST):
    def __init__(self, index):
        self.index = index


class Dedent(AST):
    def __init__(self, index):
        self.index = index


class Identifier(AST):
    def __init__(self, index):
        self.index = index


class Integer(AST):
    def __init__(self, index):
        self.index = index


class Float(AST):
    def __init__(self, index):
        self.index = index


class ImagInteger(AST):
    def __init__(self, index):
        self.index = index


class ImagFloat(AST):
    def __init__(self, index):
        self.index = index


class String(AST):
    def __init__(self, index):
        self.index = index


class ByteString(AST):
    def __init__(self, index):
        self.index = index


class PrefixedString(AST):
    def __init__(self, index):
        self.index = index


class Operator(AST):
    def __init__(self, op):
        self.op = op


class UnaryExpr(AST):
    def __init__(self, expr, op):
        self.expr = expr
        self.op = op


class BinaryExpr(AST):
    def __init__(self, lhs, op, rhs):
        self.lhs = lhs
        self.op = op
        self.rhs = rhs


class AtomExpr(AST):
    def __init__(self, expr):
        self.expr = expr


class WhileStatement(AST):
    def __init__(self):
        pass


class ForStatement(AST):
    def __init__(self):
        pass
