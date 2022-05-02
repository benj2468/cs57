from __future__ import annotations
from typing import List, Mapping

from prometheus_client import Enum

from dist.MiniCParser import MiniCParser

SUPPORTED_TYPES = ["int", "void", "str", ""]


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
        self.parent: Scope = None
        self.ty: ScopeType = ty

    def new_sub_scope(self):
        """
        Create a new sub scope
        """
        scope = Scope(ty=self.ty)
        scope.parent = self

        return scope

    def add_var(self, arg: TypedVar):
        """
        Add a variable to the scope
        """
        if arg.ident == "":
            return
        if self.check_var(arg.ident, throw=False):
            raise TwiceDefinedException(arg)
        if self.ty == ScopeType.LOOP:
            raise Exception("Cannot declare variables within a loop")

        self.vars[arg.ident] = arg

    def add_function(self, func: Function):
        """
        Add a function to the scope
        """
        if func.ident == "":
            return
        if func.ident in self.functions:
            raise TwiceDefinedException(func)
        if self.ty == ScopeType.LOOP:
            raise Exception("Cannot declare functions within a loop")

        func.parent = self
        self.functions[func.ident] = func

    def check_var(self, ident: str, throw=True):
        """
        Check if a variable is defined in the scope
        """
        if not ident in self.vars:
            if self.parent:
                return self.parent.check_var(ident, throw)
            if throw:
                raise UndefinedIdentifier(ident)
            else:
                return None

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

    def check_assignment(self, assgn: MiniCParser.AssignmentContext):
        """
        Check if an assignment is valid
        """
        variable_ty = self.check_var(assgn.variable().ident.text).type
        expr_type = self.expr_type_calculator(assgn.expr())
        if variable_ty != expr_type:
            raise TypeError(
                f"Type mismatch: got {expr_type}, but expected {variable_ty}"
            )

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
                return "str"
        elif type(ctx) == MiniCParser.FuncCallExprContext:
            func = Function.from_call_ctx(self, ctx.funccall())
            return self.check_function(func).type
        elif type(ctx) == MiniCParser.ParenExprContext:
            return self.expr_type_calculator(ctx.expr())

        raise Exception("Unknown Exception, error in parsing expression type")


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
