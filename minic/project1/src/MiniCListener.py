from dist.MiniCParser import MiniCParser
from antlr4 import ParseTreeListener


class MiniCListener(ParseTreeListener):

    # Enter a parse tree produced by MiniCParser#start.
    def enterStart(self, ctx: MiniCParser.StartContext):
        pass

    # Exit a parse tree produced by MiniCParser#start.
    def exitStart(self, ctx: MiniCParser.StartContext):
        pass

    # Enter a parse tree produced by MiniCParser#FuncDef.
    def enterFuncDef(self, ctx: MiniCParser.FuncDefContext):
        print(ctx.getText())
        pass

    # Exit a parse tree produced by MiniCParser#FuncDef.
    def exitFuncDef(self, ctx: MiniCParser.FuncDefContext):
        pass

    # Enter a parse tree produced by MiniCParser#FuncCall.
    def enterFuncCall(self, ctx: MiniCParser.FuncCallContext):
        pass

    # Exit a parse tree produced by MiniCParser#FuncCall.
    def exitFuncCall(self, ctx: MiniCParser.FuncCallContext):
        pass

    # Enter a parse tree produced by MiniCParser#funcdef.
    def enterFuncdef(self, ctx: MiniCParser.FuncdefContext):
        pass

    # Exit a parse tree produced by MiniCParser#funcdef.
    def exitFuncdef(self, ctx: MiniCParser.FuncdefContext):
        pass

    # Enter a parse tree produced by MiniCParser#funccall.
    def enterFunccall(self, ctx: MiniCParser.FunccallContext):
        pass

    # Exit a parse tree produced by MiniCParser#funccall.
    def exitFunccall(self, ctx: MiniCParser.FunccallContext):
        pass

    # Enter a parse tree produced by MiniCParser#arg.
    def enterArg(self, ctx: MiniCParser.ArgContext):
        pass

    # Exit a parse tree produced by MiniCParser#arg.
    def exitArg(self, ctx: MiniCParser.ArgContext):
        pass

    # Enter a parse tree produced by MiniCParser#TermExpr.
    def enterTermExpr(self, ctx: MiniCParser.TermExprContext):
        pass

    # Exit a parse tree produced by MiniCParser#TermExpr.
    def exitTermExpr(self, ctx: MiniCParser.TermExprContext):
        pass

    # Enter a parse tree produced by MiniCParser#UnOp.
    def enterUnOp(self, ctx: MiniCParser.UnOpContext):
        pass

    # Exit a parse tree produced by MiniCParser#UnOp.
    def exitUnOp(self, ctx: MiniCParser.UnOpContext):
        pass

    # Enter a parse tree produced by MiniCParser#ErrorExpr.
    def enterErrorExpr(self, ctx: MiniCParser.ErrorExprContext):
        pass

    # Exit a parse tree produced by MiniCParser#ErrorExpr.
    def exitErrorExpr(self, ctx: MiniCParser.ErrorExprContext):
        pass

    # Enter a parse tree produced by MiniCParser#CompOp.
    def enterCompOp(self, ctx: MiniCParser.CompOpContext):
        pass

    # Exit a parse tree produced by MiniCParser#CompOp.
    def exitCompOp(self, ctx: MiniCParser.CompOpContext):
        pass

    # Enter a parse tree produced by MiniCParser#BinOp.
    def enterBinOp(self, ctx: MiniCParser.BinOpContext):
        pass

    # Exit a parse tree produced by MiniCParser#BinOp.
    def exitBinOp(self, ctx: MiniCParser.BinOpContext):
        pass

    # Enter a parse tree produced by MiniCParser#Variable.
    def enterVariable(self, ctx: MiniCParser.VariableContext):
        pass

    # Exit a parse tree produced by MiniCParser#Variable.
    def exitVariable(self, ctx: MiniCParser.VariableContext):
        pass

    # Enter a parse tree produced by MiniCParser#Constant.
    def enterConstant(self, ctx: MiniCParser.ConstantContext):
        pass

    # Exit a parse tree produced by MiniCParser#Constant.
    def exitConstant(self, ctx: MiniCParser.ConstantContext):
        pass

    # Enter a parse tree produced by MiniCParser#Assign.
    def enterAssign(self, ctx: MiniCParser.AssignContext):
        pass

    # Exit a parse tree produced by MiniCParser#Assign.
    def exitAssign(self, ctx: MiniCParser.AssignContext):
        pass

    # Enter a parse tree produced by MiniCParser#Return.
    def enterReturn(self, ctx: MiniCParser.ReturnContext):
        pass

    # Exit a parse tree produced by MiniCParser#Return.
    def exitReturn(self, ctx: MiniCParser.ReturnContext):
        pass

    # Enter a parse tree produced by MiniCParser#Declare.
    def enterDeclare(self, ctx: MiniCParser.DeclareContext):
        pass

    # Exit a parse tree produced by MiniCParser#Declare.
    def exitDeclare(self, ctx: MiniCParser.DeclareContext):
        pass

    # Enter a parse tree produced by MiniCParser#While.
    def enterWhile(self, ctx: MiniCParser.WhileContext):
        pass

    # Exit a parse tree produced by MiniCParser#While.
    def exitWhile(self, ctx: MiniCParser.WhileContext):
        pass

    # Enter a parse tree produced by MiniCParser#If.
    def enterIf(self, ctx: MiniCParser.IfContext):
        pass

    # Exit a parse tree produced by MiniCParser#If.
    def exitIf(self, ctx: MiniCParser.IfContext):
        pass

    # Enter a parse tree produced by MiniCParser#IfElse.
    def enterIfElse(self, ctx: MiniCParser.IfElseContext):
        pass

    # Exit a parse tree produced by MiniCParser#IfElse.
    def exitIfElse(self, ctx: MiniCParser.IfElseContext):
        pass

    # Enter a parse tree produced by MiniCParser#BlockStmt.
    def enterBlockStmt(self, ctx: MiniCParser.BlockStmtContext):
        pass

    # Exit a parse tree produced by MiniCParser#BlockStmt.
    def exitBlockStmt(self, ctx: MiniCParser.BlockStmtContext):
        pass

    # Enter a parse tree produced by MiniCParser#ErrorStmt.
    def enterErrorStmt(self, ctx: MiniCParser.ErrorStmtContext):
        pass

    # Exit a parse tree produced by MiniCParser#ErrorStmt.
    def exitErrorStmt(self, ctx: MiniCParser.ErrorStmtContext):
        pass

    # Enter a parse tree produced by MiniCParser#block.
    def enterBlock(self, ctx: MiniCParser.BlockContext):
        pass

    # Exit a parse tree produced by MiniCParser#block.
    def exitBlock(self, ctx: MiniCParser.BlockContext):
        pass