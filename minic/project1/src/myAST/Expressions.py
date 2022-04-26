from Scope import Scope
from myAST.AST import ASTExprNode, INDENT_STR, ASTROpType, ASTBOpType, ASTUOpType
from typing import List


# A variable term (eg. the "a" in "b = 10 + a * 2.1;")
class ASTVarNode(ASTExprNode):
    def __init__(self, name: str) -> None:
        # The variable's name
        self.name = name
        # Note that we don't know the variable's type here.
        # We'll get to that when we decorate the AST.

    def print(self, indentation_level: int = 0) -> None:
        print(f"{INDENT_STR * indentation_level}Var. {self.name}")

    def gen(self):
        return f"""
        ({{
            llvm::Value *V = NamedValues["{self.name}"];
            if (!V)
                LogErrorV("Unknown variable name: {self.name}");

            Builder->CreateLoad(V, "{self.name}");
        }})
        """


# An integer constant term (eg. the "10" in "b = 10 + a * 2.1;")
class ASTIntLiteralNode(ASTExprNode):
    def __init__(self, value: int) -> None:
        # The constant's value
        self.value = value

    def print(self, indentation_level: int = 0) -> None:
        print(f"{INDENT_STR * indentation_level}IntLiteral. {self.value}")

    def gen(self):
        return f"""
        llvm::ConstantInt::get(*TheContext, llvm::APInt(32, {self.value}))
        """


# A floating point constant term (eg. the "2.1" in "b = 10 + a * 2.1;")
class ASTFloatLiteralNode(ASTExprNode):
    def __init__(self, value: float) -> None:
        # The constant's value
        self.value = value

    def print(self, indentation_level: int = 0) -> None:
        print(f"{INDENT_STR * indentation_level}FloatLiteral. {self.value}")

    def gen(self):
        return f"""
        llvm::ConstantFP::get(*TheContext, llvm::APFloat({self.value}))
        """


# A boolean constant term (eg. "false")
class ASTBoolLiteralNode(ASTExprNode):
    def __init__(self, value: bool) -> None:
        # The constant's value
        self.value = value

    def print(self, indentation_level: int = 0) -> None:
        print(f"{INDENT_STR * indentation_level}BoolLiteral. {self.value}")

    def gen(self):
        return f"""
        llvm::ConstantFP::get(*TheContext, llvm::APFloat({self.value}))
        """


# An integer constant term (eg. the "10" in "b = 10 + a * 2.1;")
class ASTStrLiteralNode(ASTExprNode):
    def __init__(self, value: str) -> None:
        # The constant's value
        self.value = value

    def print(self, indentation_level: int = 0) -> None:
        print(f"{INDENT_STR * indentation_level}StrLiteral. {self.value}")

    def gen(self):
        return f"""
        llvm::ConstantFP::get(*TheContext, llvm::StringRef({self.value}))
        """


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

    def gen(self):
        lhs = self.lhs.gen()
        rhs = self.rhs.gen()
        if not lhs or not rhs:
            return "nullptr"

        if self.op == ASTROpType.EQ:
            return f"Builder->CreateICmpEQ({lhs}, {rhs})"
        elif self.op == ASTROpType.NEQ:
            return f"Builder->CreateICmpNE({lhs}, {rhs})"
        elif self.op == ASTROpType.LT:
            return f"Builder->CreateICmpSLT({lhs}, {rhs})"
        elif self.op == ASTROpType.LTE:
            return f"Builder->CreateICmpSLE({lhs}, {rhs})"
        elif self.op == ASTROpType.GT:
            return f"Builder->CreateICmpSGT({lhs}, {rhs})"
        elif self.op == ASTROpType.GTE:
            return f"Builder->CreateICmpSGE({lhs}, {rhs})"


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

    def gen(self):
        lhs = self.lhs.gen()
        rhs = self.rhs.gen()
        if not lhs or not rhs:
            return "nullptr"

        if self.op == ASTBOpType.ADD:
            return f"Builder->CreateFAdd({lhs}, {rhs})"
        elif self.op == ASTBOpType.SUB:
            return f"Builder->CreateFSub({lhs}, {rhs})"
        elif self.op == ASTBOpType.MUL:
            return f"Builder->CreateFMul({lhs}, {rhs})"
        elif self.op == ASTBOpType.DIV:
            return f"Builder->CreateFDiv({lhs}, {rhs})"


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

    def gen(self):
        rhs = self.rhs.gen()
        if not rhs:
            return "nullptr"

        if self.op == ASTUOpType.NEG:
            return f"Builder->CreateFNeg({rhs})"
        elif self.op == ASTUOpType.POS:
            return rhs


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

    def gen(self):
        args = [arg.gen() for arg in self.params]
        return f"""
        ({{
            Function *CalleeF = TheModule->getFunction("{self.name}");

            std::vector<Value *> ArgsV{{{', '.join(args)}}};

            Builder->CreateCall(CalleeF, ArgsV);
        }})
        """
