from __future__ import annotations
from typing import List, Mapping

from prometheus_client import Enum

from dist.MiniCParser import MiniCParser

SUPPORTED_TYPES = ["int", "void", "string", ""]


class MiniCException(Exception):
    def __init__(self, ctx: MiniCParser.ParserRuleContext) -> None:
        self.ctx = ctx

    def __repr__(self):
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
        return f"Undefined identifier: {self.ident}"


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

        if not type in SUPPORTED_TYPES:
            raise TypeError("Only int type is supported")
        self.type = type


class ScopeType(Enum):
    STATIC = 1
    LOOP = 3


class Scope(Identifiable):
    """
    Scope class
    """

    def __init__(self, ident="global", ty=ScopeType.STATIC) -> None:
        super().__init__(ident)
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

    def new_while(self):
        """
        Create a new while loop
        """
        loop = While()
        loop.parent = self
        loop.ty = ScopeType.LOOP
        return loop

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

        func.parent = self
        self.functions[func.ident] = func

    def check_var(self, ident: str):
        """
        Check if a variable is defined in the scope
        """
        if not ident in self.vars:
            if self.parent:
                return self.parent.check_var(ident)
            raise UndefinedIdentifier(ident)

        return self.vars[ident]

    def check_function(self, func: Function):
        """
        Check if a function is defined in the scope, and if the variable count matches
        """
        if not func.ident in self.functions:
            if self.parent:
                return self.parent.check_function(func)
            raise UndefinedIdentifier(func.ident)

        caller = self.functions[func.ident]
        for i, arg in enumerate(caller.args):
            if arg.type != func.args[i].type:
                raise Exception(
                    "Mismatched Argument Types: got "
                    + arg.type
                    + ", but expected "
                    + func.args[i].type
                )

        return self.functions[func.ident]

    def expr_type_calculator(self, ctx: MiniCParser.ExprContext):
        def isTypeUOperable(ty: str):
            if ty in ["int", "bool", "void"]:
                return True
            return False

        def areTypesComparable(a: str, b: str):
            if a == b:
                return True
            return False

        """
        Calculate the evaluated type of the expression
        """
        if type(ctx) == MiniCParser.BinOpExprContext:
            leftTy = self.expr_type_calculator(ctx.left)
            rightTy = self.expr_type_calculator(ctx.right)
            if leftTy != rightTy:
                raise TypeError("Type mismatch in binary operation")
            return leftTy
        elif type(ctx) == MiniCParser.UnOpExprContext:
            exprTy = self.expr_type_calculator(ctx.expr())
            if not isTypeUOperable(exprTy):
                raise TypeError("Cannot perform unary operation on type " + exprTy)
            return exprTy
        elif type(ctx) == MiniCParser.CompOpExprContext:
            leftTy = self.expr_type_calculator(ctx.left)
            rightTy = self.expr_type_calculator(ctx.right)
            if not areTypesComparable(leftTy, rightTy):
                raise TypeError(
                    "Unable to compare two types " + leftTy + " and " + rightTy
                )
            return leftTy
        elif type(ctx) == MiniCParser.TermExprContext:
            term = ctx.term()
            if term.ident:
                return self.check_var(term.ident.getText()).type
            elif term.number:
                return "int"
            elif term.string:
                return "string"
        elif type(ctx) == MiniCParser.FuncCallExprContext:
            return self.check_function[ctx.ident.text].type
        elif type(ctx) == MiniCParser.ParenExprContext:
            return self.expr_type_calculator(ctx.expr())

        raise Exception("Unknown Exception, error in parsing expression type")


class While(Scope):
    """
    While Loop Class
    """

    def __init__(self):
        super().__init__(ty=ScopeType.LOOP)
        self.condition = None


class IfElse(Scope):
    """
    IfElse Loop Class
    """

    def __init__(self):
        super().__init__(ty=ScopeType.LOOP)
        self.condition = None
        self.if_scope = None
        self.else_scope = None


class Function(Scope):
    """
    Function class
    """

    def __init__(self, type: str, ident: str, args: List[TypedVar]):
        super().__init__(ident)
        self.type = type
        self.args = args

        for arg in self.args:
            self.add_var(arg)
        self.functions[self.ident] = self

    def from_ctx(ctx: MiniCParser.FuncdefContext | MiniCParser.FunctionDecContext):
        args = []
        if hasattr(ctx, "scope"):  # Then it is a function definition
            for arg in ctx.arg():
                args.append(TypedVar(arg.ident.getText(), arg.ty.text))
        else:  # Then it is a function declaration
            for arg in ctx.WORD()[2:]:
                args.append(TypedVar("", str(arg)))

        return Function(ctx.ty.text, ctx.ident.text, args)

    def from_call_ctx(scope: Scope, ctx: MiniCParser.FunccallContext):
        args = []
        for arg in ctx.expr():
            ty = scope.expr_type_calculator(arg)
            args.append(TypedVar("", ty))
        return Function("", ctx.ident.text, args)
