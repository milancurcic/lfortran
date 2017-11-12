"""
Semantic analysis module
"""

from ..ast import ast

class SemanticError(Exception):
    pass

class UndeclaredVariableError(Exception):
    pass

class TypeMismatch(Exception):
    pass


# ----------------------------

# Types are immutable. Once instantiated, they never change.

class Type(object):

    def __neq__(self, other):
        return not self.__eq__(other)

class Intrinsic(Type):
    def __init__(self, kind=None):
        #super(Intrinsic, self).__init__()
        self.kind = kind

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        return self.kind == other.kind

    def __hash__(self):
        return 1

class Integer(Intrinsic):
    def __repr__(self):
        return "Integer()"
class Real(Intrinsic):
    def __repr__(self):
        return "Real()"
class Complex(Intrinsic): pass
class Character(Intrinsic): pass
class Logical(Intrinsic): pass

class Derived(Type):
    pass

class Array(Type):
    def __init__(self, type_, rank, shape):
        self.type_ = type_
        self.rank = rank
        self.shape = shape


# --------------------------------


class SymbolTableVisitor(ast.GenericASTVisitor):

    def __init__(self):
        self.types = {
                "integer": Integer,
                "real": Real,
                "complex": Complex,
                "character": Character,
                "logical": Logical,
            }
        self.symbol_table = {}

    def visit_Declaration(self, node):
        for v in node.vars:
            sym = v.sym
            type_f = v.sym_type
            if type_f not in self.types:
                # This shouldn't happen, as the parser checks types
                raise SemanticError("Type not implemented.")
            type_ = self.types[type_f]()
            self.symbol_table[sym] = {"name": sym, "type": type_}

def create_symbol_table(tree):
    v = SymbolTableVisitor()
    v.visit(tree)
    return v.symbol_table



class ExprVisitor(ast.GenericASTVisitor):

    def __init__(self, symbol_table):
        self.symbol_table = symbol_table

    def visit_Num(self, node):
        node._type = Integer()

    def visit_Constant(self, node):
        node._type = Logical()

    def visit_Name(self, node):
        if not node.id in self.symbol_table:
            raise UndeclaredVariableError("Variable '%s' not declared." \
                    % node.id)
        node._type = self.symbol_table[node.id]["type"]

    def visit_BinOp(self, node):
        self.visit(node.left)
        self.visit(node.right)
        if node.left._type != node.right._type:
            raise TypeMismatch("Type mismatch")
        node._type = node.left._type

    def visit_UnaryOp(self, node):
        self.visit(node.operand)
        node._type = node.operand._type

    def visit_Compare(self, node):
        self.visit(node.left)
        self.visit(node.right)
        if node.left._type != node.right._type:
            # TODO: allow combinations of Real/Integer
            raise TypeMismatch("Type mismatch")
        node._type = Logical()

    def visit_If(self, node):
        self.visit(node.test)
        if node.test._type != Logical():
            raise TypeMismatch("If condition must be of type logical.")
        self.visit_sequence(node.body)
        self.visit_sequence(node.orelse)

    def visit_Assignment(self, node):
        assert isinstance(node.target, ast.Name)
        if not node.target.id in self.symbol_table:
            raise UndeclaredVariableError("Variable '%s' not declared." \
                    % node.target)
        node._type = self.symbol_table[node.target.id]["type"]
        self.visit(node.value)
        if node.value._type != node._type:
            raise TypeMismatch("Type mismatch")

def annotate_tree(tree, symbol_table):
    """
    Annotates the `tree` with types.
    """
    v = ExprVisitor(symbol_table)
    v.visit(tree)