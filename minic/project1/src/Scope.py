from __future__ import annotations
from typing import List, Mapping

from dist.MiniCParser import MiniCParser

SUPPORTED_TYPES = ['int', 'void', '']


def expr_type_calculator(ctx: MiniCParser.ExprContext):
    """
    Calculate the evaluated type of the expression
    """
    return 'int'


class MiniCException(Exception):

    def __init__(self, ctx: MiniCParser.ParserRuleContext) -> None:
        self.ctx = ctx

    def __repr__(self):
        return f"TypeError: Undefined Type: {self.type}"


class TypeError(Exception):

    def __init__(self, type: str):
        self.type = type

    def __str__(self):
        return f"TypeError: Undefined Type: {self.type}"


class Identifiable(object):

    def __init__(self, ident) -> None:
        self.ident = ident

    def get_ident(self):
        return self.ident


class UndefinedIdentifier(Exception):

    def __init__(self, ident) -> None:
        self.ident = ident

    def __str__(self):
        return f'Undefined identifier: {self.ident}'


class TwiceDefinedException(Exception):
    """
    Exception class
    """

    def __init__(self, arg: Identifiable):
        self.arg = arg

    def __str__(self):
        return f"{self.arg.get_ident()} is already defined"


class TypedVar(Identifiable):
    """
    Type class
    """

    def __init__(self, ident: str, type: str):
        super().__init__(ident)

        if (not type in SUPPORTED_TYPES):
            raise TypeError('Only int type is supported')
        self.type = type


class Function(Identifiable):
    """
    Function class
    """

    def __init__(self, type: str, ident: str, args: List[TypedVar]):
        super().__init__(ident)
        self.type = type
        self.args = args
        self.scope = None

    def from_ctx(ctx: MiniCParser.FuncdefContext | MiniCParser.FuncdecContext):
        args = []
        if (hasattr(ctx, 'scope')):  # Then it is a function definition
            for arg in ctx.arg():
                args.append(TypedVar(arg.ident.getText(), arg.ty.text))
        else:  # Then it is a function declaration
            for arg in ctx.WORD()[2:]:
                args.append(TypedVar('', str(arg)))

        return Function(ctx.ty.text, ctx.ident.text, args)

    def from_call_ctx(ctx: MiniCParser.FunccallContext):
        args = []
        for arg in ctx.expr():

            ty = expr_type_calculator(arg)
            args.append(TypedVar('', ty))
        return Function('', ctx.ident.text, args)

    def setup_scope(self, scope: Scope):
        self.scope = scope.new_sub_scope()
        for arg in self.args:
            self.scope.add_var(arg)


class Scope():
    """
    Scope class
    """

    def __init__(self):
        self.vars: Mapping[str, TypedVar] = {}
        self.functions: Mapping[str, Function] = {}
        self.parent = None

    def new_sub_scope(self):
        """
        Create a new sub scope
        """
        scope = Scope()
        scope.parent = self

        return scope

    def add_var(self, arg: TypedVar):
        """
        Add a variable to the scope
        """
        if arg.ident in self.vars:
            raise TwiceDefinedException(arg)

        self.vars[arg.ident] = arg

    def add_function(self, func: Function):
        """
        Add a function to the scope
        """
        if func.ident in self.functions:
            raise TwiceDefinedException(func)

        func.setup_scope(self)
        self.functions[func.ident] = func

    def check_var(self, ident: str):
        """
        Check if a variable is defined in the scope
        """
        if not ident in self.vars:
            if self.parent:
                return self.parent.check_var(ident)
            raise UndefinedIdentifier(ident)

    def check_function(self, func: Function):
        """
        Check if a function is defined in the scope, and if the variable count matches
        """
        if not func.ident in self.functions:
            if self.parent:
                return self.parent.check_function(func)
            raise UndefinedIdentifier(func)

        caller = self.functions[func.ident]
        for i, arg in enumerate(caller.args):
            if arg.type != func.args[i].type:
                raise Exception("Mismatched Argument Types: " + arg.type +
                                " and " + func.args[i].type)
