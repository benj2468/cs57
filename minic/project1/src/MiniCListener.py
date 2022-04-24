from dist.MiniCParser import MiniCParser
from dist.MiniCListener import MiniCListener
from Scope import Function, Scope, TypedVar


# This class defines a complete listener for a parse tree produced by MiniCParser.
class MyMiniCListener(MiniCListener):

    def __init__(self):
        self.scope = None

    # Enter a parse tree produced by MiniCParser#start.
    def enterStart(self, ctx: MiniCParser.StartContext):
        self.scope = Scope()
        pass

    # Exit a parse tree produced by MiniCParser#start.
    def exitStart(self, ctx: MiniCParser.StartContext):
        pass

    # Enter a parse tree produced by MiniCParser#line.
    def enterLine(self, ctx: MiniCParser.LineContext):
        pass

    # Exit a parse tree produced by MiniCParser#line.
    def exitLine(self, ctx: MiniCParser.LineContext):
        pass

    # Enter a parse tree produced by MiniCParser#funcdec.
    def enterFuncdec(self, ctx: MiniCParser.FuncdecContext):
        function = Function.from_ctx(ctx)
        self.scope.add_function(function)
        self.scope = function.scope

    # Exit a parse tree produced by MiniCParser#funcdec.
    def exitFuncdec(self, ctx: MiniCParser.FuncdecContext):
        pass

    # Enter a parse tree produced by MiniCParser#funcdef.
    def enterFuncdef(self, ctx: MiniCParser.FuncdefContext):
        function = Function.from_ctx(ctx)
        self.scope.add_function(function)
        self.scope = function.scope

    # Exit a parse tree produced by MiniCParser#funcdef.
    def exitFuncdef(self, ctx: MiniCParser.FuncdefContext):
        self.scope = self.scope.parent

    # Enter a parse tree produced by MiniCParser#TermExpr.
    def enterTermExpr(self, ctx: MiniCParser.TermExprContext):
        pass

    # Exit a parse tree produced by MiniCParser#TermExpr.
    def exitTermExpr(self, ctx: MiniCParser.TermExprContext):
        pass

    # Enter a parse tree produced by MiniCParser#funccall.
    def enterFunccall(self, ctx: MiniCParser.FunccallContext):
        function = Function.from_ctx(ctx)
        self.scope.check_function(function)

    # Exit a parse tree produced by MiniCParser#funccall.
    def exitFunccall(self, ctx: MiniCParser.FunccallContext):
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
        self.scope.check_var(ctx.ident.text)
        pass

    # Exit a parse tree produced by MiniCParser#Variable.
    def exitVariable(self, ctx: MiniCParser.VariableContext):
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
        arg = ctx.arg()
        var = TypedVar(arg.ident.getText(), arg.ty.text)
        self.scope.add_var(var)

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

    # # Enter a parse tree produced by MiniCParser#BlockStmt.
    # def enterBlockStmt(self, ctx: MiniCParser.BlockStmtContext):
    #     pass

    # # Exit a parse tree produced by MiniCParser#BlockStmt.
    # def exitBlockStmt(self, ctx: MiniCParser.BlockStmtContext):
    #     pass

    # Enter a parse tree produced by MiniCParser#block.
    def enterBlock(self, ctx: MiniCParser.BlockContext):
        self.scope = self.scope.new_sub_scope()

    # Exit a parse tree produced by MiniCParser#block.
    def exitBlock(self, ctx: MiniCParser.BlockContext):
        self.scope = self.scope.parent

    # Enter a parse tree produced by MiniCParser#arg.
    def enterArg(self, ctx: MiniCParser.ArgContext):
        pass

    # Exit a parse tree produced by MiniCParser#arg.
    def exitArg(self, ctx: MiniCParser.ArgContext):
        pass
