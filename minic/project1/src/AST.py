### COSC57 AST class for Python
### By Ben Kallus
### Fully type checked by mypy; formatted with black.
### If you are cool, you will run your code through mypy and black when you use this library.
#
# 19 Apr 2022  bjk  Creation
# 24 Apr 2022  jpb  Released v1 for class
# 25 Apr 2022  bjc  Updated to handle multiple parameters to functions
#

from enum import Enum
from typing import List, Optional, Tuple

INDENT_STR = "|   "

# Enum's __str__ will spit out its class name by default.
# This class fixes that problem.
class MyEnum(Enum):
    def __str__(self):
        return self._name_


# Relational operators
class ASTROpType(MyEnum):
    LT = 0  # <
    GT = 1  # >
    LEQ = 2  # <=
    GEQ = 3  # >=
    EQ = 4  # ==
    NEQ = 5  # !=


# Binary operators
class ASTBOpType(MyEnum):
    ADD = 0  # +
    SUB = 1  # -
    DIV = 2  # /
    MUL = 3  # *


# Unary operators
class ASTUOpType(MyEnum):
    POS = 0  # +
    NEG = 1  # -


# The types in miniC
class ASTDataType(MyEnum):
    VOID_T = 0
    INT_T = 1
    FLOAT_T = 2
    BOOL_T = 3
    STR_T = 4


# Abstract class from which all node classes in the AST derive.
class ASTNode:
    def print(self, indentation_level: int = 0):
        assert False


# Abstract class from which all statements derive.
# A statement is (informally) anything that could sit on its own in a block.
class ASTStmtNode(ASTNode):
    pass


# Abstract class from which variable and function declarations derive.
class ASTDeclNode(ASTStmtNode):
    pass


# Abstract class from which all expressions derive.
# An expression is a term, a function call, or expressions combined with appropriate operators.
class ASTExprNode(ASTStmtNode):
    pass


# An assignment (eg. "a = 1;")
class ASTAsgnNode(ASTStmtNode):
    def __init__(self, lhs: str, rhs: ASTExprNode) -> None:
        # The left-hand side of the assignment
        self.lhs = lhs
        # The right-hand side of the assignment
        self.rhs = rhs

    def print(self, indentation_level: int = 0) -> None:
        print(f"{INDENT_STR * indentation_level}Asgn. {self.lhs} =")
        self.rhs.print(indentation_level + 1)


# A block (eg. "{ int a; a = 10 + b; exit(1); return will_never_get_here; }")
class ASTBlockNode(ASTStmtNode):
    def __init__(self, stmt_list: List[ASTStmtNode]) -> None:
        # The statements that make up the block
        self.stmt_list = stmt_list

    def print(self, indentation_level: int = 0) -> None:
        print(f"{INDENT_STR * indentation_level}Block.")
        for stmt in self.stmt_list:
            stmt.print(indentation_level + 1)


# A function definition (eg. "int the_identity_fn(int n) { return n; }")
class ASTFuncDefNode(ASTNode):
    def __init__(
        self,
        return_type: ASTDataType,
        name: str,
        params: List[Tuple[ASTDataType, str]],
        body: ASTBlockNode,
    ) -> None:
        # The return type of the function
        self.return_type = return_type
        # The name of the function
        self.name = name
        # The parameter type of the function
        self.params = params
        # The function body
        self.body = body

    def print(self, indentation_level: int = 0) -> None:
        print(
            f"{INDENT_STR * indentation_level}FuncDef. {self.return_type} {self.name}({', '.join([f'{str(x[0])} {x[1]}' for x in self.params])})"
        )
        self.body.print(indentation_level + 1)


# A root node of an AST. You should have one of these per compilation unit.
class ASTRootNode(ASTNode):
    def __init__(
        self,
        decls: List[ASTDeclNode],
        asgns: List[ASTAsgnNode],
        funcs: List[ASTFuncDefNode],
    ) -> None:
        # List of function and variable declarations.
        # Must be at the top of the file.
        self.decls = decls
        # List of variable assignments for global variables.
        # Must be after declarations and before functions in the file.
        self.asgns = asgns
        # List of function definitions.
        # Must be at the end of the file.
        self.funcs = funcs

    def print(self, indentation_level: int = 0) -> None:
        print(f"{INDENT_STR * indentation_level}Root.")
        if self.asgns != []:
            print(f"{INDENT_STR * indentation_level}Assignments:")
        for asgn in self.asgns:
            asgn.print(indentation_level + 1)
        if self.decls != []:
            print(f"{INDENT_STR * indentation_level}Declarations:")
        for decl in self.decls:
            decl.print(indentation_level + 1)
        if self.funcs != []:
            print(f"{INDENT_STR * indentation_level}Functions:")
        for func in self.funcs:
            func.print(indentation_level + 1)


# A variable declaration. (eg. "int a;")
class ASTVarDeclNode(ASTDeclNode):
    def __init__(self, is_extern: bool, data_type: ASTDataType, name: str) -> None:
        # Whether the variable is extern
        self.is_extern = is_extern
        # The type of the variable
        self.data_type = data_type
        # The name of the variable
        self.name = name

    def print(self, indentation_level: int = 0) -> None:
        print(
            f"{INDENT_STR * indentation_level}VarDecl. {'extern ' * self.is_extern}{self.data_type} {self.name}"
        )


# A function declaration (eg. "int main(void);" or "extern int square(int);")
class ASTFuncDeclNode(ASTDeclNode):
    def __init__(
        self,
        is_extern: bool,
        return_type: ASTDataType,
        name: str,
        params: List[ASTDataType],
    ) -> None:
        # Whether the function is extern
        self.is_extern = is_extern
        # The return type of the function
        self.return_type = return_type
        # The name of the function
        self.name = name
        # The type of the parameter to the function
        self.params = params
        # Note that parameter names don't matter in C function declarations because all arguments are positional.
        # Thus, we don't store that info in the AST.

    def print(self, indentation_level: int = 0) -> None:
        print(
            f"{INDENT_STR * indentation_level}FuncDecl. {'extern' * self.is_extern} {self.return_type} {self.name}({', '.join(self.params)})"
        )


# A variable term (eg. the "a" in "b = 10 + a * 2.1;")
class ASTVarNode(ASTExprNode):
    def __init__(self, name: str) -> None:
        # The variable's name
        self.name = name
        # Note that we don't know the variable's type here.
        # We'll get to that when we decorate the AST.

    def print(self, indentation_level: int = 0) -> None:
        print(f"{INDENT_STR * indentation_level}Var. {self.name}")


# An integer constant term (eg. the "10" in "b = 10 + a * 2.1;")
class ASTIntLiteralNode(ASTExprNode):
    def __init__(self, value: int) -> None:
        # The constant's value
        self.value = value

    def print(self, indentation_level: int = 0) -> None:
        print(f"{INDENT_STR * indentation_level}IntLiteral. {self.value}")


# A floating point constant term (eg. the "2.1" in "b = 10 + a * 2.1;")
class ASTFloatLiteralNode(ASTExprNode):
    def __init__(self, value: float) -> None:
        # The constant's value
        self.value = value

    def print(self, indentation_level: int = 0) -> None:
        print(f"{INDENT_STR * indentation_level}FloatLiteral. {self.value}")


# A boolean constant term (eg. "false")
class ASTBoolLiteralNode(ASTExprNode):
    def __init__(self, value: bool) -> None:
        # The constant's value
        self.value = value

    def print(self, indentation_level: int = 0) -> None:
        print(f"{INDENT_STR * indentation_level}BoolLiteral. {self.value}")


# An integer constant term (eg. the "10" in "b = 10 + a * 2.1;")
class ASTStrLiteralNode(ASTExprNode):
    def __init__(self, value: str) -> None:
        # The constant's value
        self.value = value

    def print(self, indentation_level: int = 0) -> None:
        print(f"{INDENT_STR * indentation_level}StrLiteral. {self.value}")


# A relational expression (eg. "10 > 2")
class ASTRExprNode(ASTExprNode):
    def __init__(self, lhs: ASTExprNode, rhs: ASTExprNode, op: ASTROpType) -> None:
        # The left-hand side of the relational operator
        self.lhs = lhs
        # The right-hand side of the relational operator
        self.rhs = rhs
        # The relational operator
        self.op = op

    def print(self, indentation_level: int = 0) -> None:
        print(f"{INDENT_STR * indentation_level}RExpr. {self.op}")
        print(f"{INDENT_STR * indentation_level}(RExpr) LHS =")
        self.lhs.print(indentation_level + 1)
        print(f"{INDENT_STR * indentation_level}(RExpr) RHS =")
        self.rhs.print(indentation_level + 1)


# A binary expression (eg. "10 + 2")
class ASTBExprNode(ASTExprNode):
    def __init__(self, lhs: ASTExprNode, rhs: ASTExprNode, op: ASTBOpType) -> None:
        # The left-hand side of the binary operator
        self.lhs = lhs
        # The right-hand side of the binary operator
        self.rhs = rhs
        # The binary operator
        self.op = op

    def print(self, indentation_level: int = 0) -> None:
        print(f"{INDENT_STR * indentation_level}BExpr. {self.op}")
        print(f"{INDENT_STR * indentation_level}(BExpr) LHS =")
        self.lhs.print(indentation_level + 1)
        print(f"{INDENT_STR * indentation_level}(BExpr) RHS =")
        self.rhs.print(indentation_level + 1)


# A unary expression (eg. "-10")
class ASTUExprNode(ASTExprNode):
    def __init__(self, expr: ASTExprNode, op: ASTUOpType) -> None:
        # The expression to which the unary operation applies
        self.expr = expr
        # The unary operator
        self.op = op

    def print(self, indentation_level: int = 0) -> None:
        print(f"{INDENT_STR * indentation_level}UExpr. {self.op}, expression =")
        self.expr.print(indentation_level + 1)


# A function call (eg. "set_coolness_factor(100);")
class ASTCallNode(ASTExprNode):
    def __init__(self, name: str, params: List[ASTExprNode]) -> None:
        # The name of the function being called
        self.name = name
        # The parameter to the function
        self.params = params  # Could be None

    def print(self, indentation_level: int = 0) -> None:
        print(
            f"{INDENT_STR * indentation_level}Call. {self.name}{', parameters =' * (bool(len(self.params)))}"
        )
        for param in self.params:
            param.print(indentation_level + 1)


# A return statement (eg. "return 10;")
class ASTRetNode(ASTStmtNode):
    def __init__(self, expr: Optional[ASTExprNode] = None) -> None:
        # The thing being returned
        self.expr = expr  # Could be None

    def print(self, indentation_level: int = 0) -> None:
        print(
            f"{INDENT_STR * indentation_level}Ret.{' expression =' * (self.expr is not None)}"
        )
        if self.expr is not None:
            self.expr.print(indentation_level + 1)


# A while statement (eg. "while (1 == 1) { 1; }")
class ASTWhileNode(ASTStmtNode):
    def __init__(self, cond: ASTExprNode, body: ASTBlockNode) -> None:
        # The loop condition
        self.cond = cond
        # The loop body
        self.body = body

    def print(self, indentation_level: int = 0) -> None:
        print(f"{INDENT_STR * indentation_level}While.")
        print(f"{INDENT_STR * indentation_level}(While) condition =")
        self.cond.print(indentation_level + 1)
        print(f"{INDENT_STR * indentation_level}(While) body =")
        self.body.print(indentation_level + 1)


# An if statement (eg. "if (1 != 1) { return BAD_NEWS; } else { return ALL_IS_WELL; }")
class ASTIfNode(ASTStmtNode):
    def __init__(
        self,
        cond: ASTExprNode,
        if_body: ASTBlockNode,
        else_body: Optional[ASTBlockNode] = None,
    ) -> None:
        # The if condition
        self.cond = cond
        # The if body
        self.if_body = if_body
        # The else body
        self.else_body = ASTBlockNode(stmt_list=[]) if else_body is None else else_body

    def print(self, indentation_level: int = 0) -> None:
        print(f"{INDENT_STR * indentation_level}If.")
        print(f"{INDENT_STR * indentation_level}(If) condition =")
        self.cond.print(indentation_level + 1)
        print(f"{INDENT_STR * indentation_level}(If) if_body =")
        self.if_body.print(indentation_level + 1)
        print(f"{INDENT_STR * indentation_level}(If) else_body =")
        self.else_body.print(indentation_level + 1)


# A variable declaration. (eg. "int a;")
class ASTVarDeclStmtNode(ASTStmtNode):
    def __init__(self, data_type: ASTDataType, name: str) -> None:
        # The type of the variable
        self.data_type = data_type
        # The name of the variable
        self.name = name

    def print(self, indentation_level: int = 0) -> None:
        print(f"{INDENT_STR * indentation_level}VarDecl. {self.data_type} {self.name}")


# An empty statement (eg. ";")
# (This could just be ASTStmtNode, but I'd rather have that be an abstract class)
class ASTEmptyStmtNode(ASTStmtNode):
    def __init__(self) -> None:
        pass

    def print(self, indentation_level: int = 0) -> None:
        print(f"{INDENT_STR * indentation_level}EmptyStmt.")


if __name__ == "__main__":
    print("This file isn't meant to be run on its own.")
