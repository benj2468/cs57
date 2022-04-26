from myAST.AST import ASTStmtNode, ASTExprNode, INDENT_STR, ASTDataType, ASTBlockNode
from typing import List
from typing import Optional


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

    def gen(self) -> str:
        ret_val = self.expr.gen()
        return f"""
        {ret_val}
        """


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

    def gen(self) -> str:
        cond = self.cond.gen()
        body = self.body.gen()

        return f"""
        ({{
            Value *CondV = {cond};
            if (!CondV)
                nullptr;

            // Convert condition to a bool by comparing non-equal to 0.0.
            CondV = Builder->CreateFCmpONE(
                CondV, ConstantFP::get(*TheContext, APFloat(0.0)), "ifcond");

            
            Function *TheFunction = Builder->GetInsertBlock()->getParent();

            // Create blocks for the body and for after the loop.
            BasicBlock *BodyBB =
                BasicBlock::Create(*TheContext, "body", TheFunction);
            BasicBlock *PostLoop =
                BasicBlock::Create(*TheContext, "afterloop", TheFunction);

            // Insert the conditional branch into the end of LoopEndBB.
            Builder->CreateCondBr(CondV, LoopBB, AfterBB);

            // Emit body value.
            Builder->SetInsertPoint(BodyBB);
            Value *BodyV = {body};
            if (!BodyV)
                nullptr;

            // Any new code will be inserted in AfterBB.
            Builder->SetInsertPoint(AfterBB);
        }})
        
        """


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

    def gen(self) -> str:
        cond = self.cond.gen()
        if_body = self.if_body.gen()
        else_body = self.else_body.gen()

        return f"""
        {{
            Value *CondV = {cond};
            if (!CondV)
                nullptr;

            // Convert condition to a bool by comparing non-equal to 0.0.
            CondV = Builder->CreateFCmpONE(
                CondV, ConstantFP::get(*TheContext, APFloat(0.0)), "ifcond");

            Function *TheFunction = Builder->GetInsertBlock()->getParent();

            // Create blocks for the then and else cases.  Insert the 'then' block at the
            // end of the function.
            BasicBlock *ThenBB =
                BasicBlock::Create(*TheContext, "then", TheFunction);
            BasicBlock *ElseBB = BasicBlock::Create(*TheContext, "else");
            BasicBlock *MergeBB = BasicBlock::Create(*TheContext, "ifcont");

            Builder->CreateCondBr(CondV, ThenBB, ElseBB);

            // Emit then value.
            Builder->SetInsertPoint(ThenBB);
            Value *ThenV = {if_body};
            if (!ThenV)
                nullptr;

            Builder->CreateBr(MergeBB);
            // Codegen of 'Then' can change the current block, update ThenBB for the PHI.
            ThenBB = Builder->GetInsertBlock();

            // Emit else block.
            TheFunction->getBasicBlockList().push_back(ElseBB);
            Builder->SetInsertPoint(ElseBB);

            Value *ElseV = {else_body};
            if (!ElseV)
                nullptr;

            Builder->CreateBr(MergeBB);
            // codegen of 'Else' can change the current block, update ElseBB for the PHI.
            ElseBB = Builder->GetInsertBlock();

            // Emit merge block.
            TheFunction->getBasicBlockList().push_back(MergeBB);
            Builder->SetInsertPoint(MergeBB);
            PHINode *PN =
                Builder->CreatePHI(Type::getDoubleTy(*TheContext), 2, "iftmp");
        }}
        """


# A variable declaration. (eg. "int a;")
class ASTVarDeclStmtNode(ASTStmtNode):
    def __init__(self, data_type: ASTDataType, name: str) -> None:
        # The type of the variable
        self.data_type = data_type
        # The name of the variable
        self.name = name

    def print(self, indentation_level: int = 0) -> None:
        print(f"{INDENT_STR * indentation_level}VarDecl. {self.data_type} {self.name}")

    def gen(self) -> str:
        ty = self.data_type.gen()
        return f"""
        ({{
            // Create an alloca for this variable.
            llvm::AllocaInst *Alloca = Builder->CreateAlloca({ty}, 0, "{self.name}");

            // Add arguments to variable symbol table.
            NamedValues["{self.name}"] = Alloca;
        }})
        """


# An empty statement (eg. ";")
# (This could just be ASTStmtNode, but I'd rather have that be an abstract class)
class ASTEmptyStmtNode(ASTStmtNode):
    def __init__(self) -> None:
        pass

    def print(self, indentation_level: int = 0) -> None:
        print(f"{INDENT_STR * indentation_level}EmptyStmt.")

    def gen(self) -> str:
        return ""
