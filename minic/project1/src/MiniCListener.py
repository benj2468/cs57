from ast import AST
from typing import List
from ASTconverter import parse_start
from dist.MiniCParser import MiniCParser
from dist.MiniCListener import MiniCListener
from Scope import Function, Scope, TypedVar


# This class defines a complete listener for a parse tree produced by MiniCParser.
class MyMiniCListener(MiniCListener):
    def __init__(self):
        self.scope = None
        self.ast = None

    # Enter a parse tree produced by MiniCParser#start.
    def enterStart(self, ctx: MiniCParser.StartContext):
        self.scope = Scope()
        pass

    # Exit a parse tree produced by MiniCParser#start.
    def exitStart(self, ctx: MiniCParser.StartContext):
        self.ast = parse_start(ctx)
        pass

    # Enter a parse tree produced by MiniCParser#line.
    def enterLine(self, ctx: MiniCParser.LineContext):
        pass

    # Exit a parse tree produced by MiniCParser#line.
    def exitLine(self, ctx: MiniCParser.LineContext):
        pass

    # Enter a parse tree produced by MiniCParser#funcdec.
    def enterFunctionDec(self, ctx: MiniCParser.FunctionDecContext):
        # Scope work for parsing
        function = Function.from_ctx(ctx)
        self.scope.add_function(function)

    # Exit a parse tree produced by MiniCParser#funcdec.
    def exitFunctionDec(self, ctx: MiniCParser.FunctionDecContext):
        pass

    # Enter a parse tree produced by MiniCParser#funcdef.
    def enterFuncdef(self, ctx: MiniCParser.FuncdefContext):
        function = Function.from_ctx(ctx)
        self.scope.add_function(function)
        self.scope = function

    # Exit a parse tree produced by MiniCParser#funcdef.
    def exitFuncdef(self, ctx: MiniCParser.FuncdefContext):
        function = self.scope
        self.scope = self.scope.parent

    # Enter a parse tree produced by MiniCParser#TermExpr.
    def enterTermExpr(self, ctx: MiniCParser.TermExprContext):
        pass

    # Exit a parse tree produced by MiniCParser#TermExpr.
    def exitTermExpr(self, ctx: MiniCParser.TermExprContext):
        pass

    # Enter a parse tree produced by MiniCParser#funccall.
    def enterFunccall(self, ctx: MiniCParser.FunccallContext):
        function = Function.from_call_ctx(self.scope, ctx)
        self.scope.check_function(function)

    # Exit a parse tree produced by MiniCParser#funccall.
    def exitFunccall(self, ctx: MiniCParser.FunccallContext):
        pass

    # Enter a parse tree produced by MiniCParser#TermExpr.
    def enterTermExpr(self, ctx: MiniCParser.TermExprContext):
        pass

    # Exit a parse tree produced by MiniCParser#TermExpr.
    def exitTermExpr(self, ctx: MiniCParser.TermExprContext):
        pass

    # Enter a parse tree produced by MiniCParser#BinOpExpr.
    def enterBinOpExpr(self, ctx: MiniCParser.BinOpExprContext):
        pass

    # Exit a parse tree produced by MiniCParser#BinOpExpr.
    def exitBinOpExpr(self, ctx: MiniCParser.BinOpExprContext):
        pass

    # Enter a parse tree produced by MiniCParser#UnOpExor.
    def enterUnOpExor(self, ctx: MiniCParser.UnOpExprContext):
        pass

    # Exit a parse tree produced by MiniCParser#UnOpExor.
    def exitUnOpExor(self, ctx: MiniCParser.UnOpExprContext):
        pass

    # Enter a parse tree produced by MiniCParser#ParenExpr.
    def enterParenExpr(self, ctx: MiniCParser.ParenExprContext):
        pass

    # Exit a parse tree produced by MiniCParser#ParenExpr.
    def exitParenExpr(self, ctx: MiniCParser.ParenExprContext):
        pass

    # Enter a parse tree produced by MiniCParser#FuncCallExpr.
    def enterFuncCallExpr(self, ctx: MiniCParser.FuncCallExprContext):
        pass

    # Exit a parse tree produced by MiniCParser#FuncCallExpr.
    def exitFuncCallExpr(self, ctx: MiniCParser.FuncCallExprContext):
        pass

    # Enter a parse tree produced by MiniCParser#CompOpExor.
    def enterCompOpExpr(self, ctx: MiniCParser.CompOpExprContext):
        pass

    # Exit a parse tree produced by MiniCParser#CompOpExor.
    def exitCompOpExpr(self, ctx: MiniCParser.CompOpExprContext):
        pass

    # Enter a parse tree produced by MiniCParser#Variable.
    def enterVariable(self, ctx: MiniCParser.VariableContext):
        self.scope.check_var(ctx.ident.text)

    # Exit a parse tree produced by MiniCParser#Variable.
    def exitVariable(self, ctx: MiniCParser.VariableContext):
        pass

    # Enter a parse tree produced by MiniCParser#Assign.
    def enterAssign(self, ctx: MiniCParser.AssignContext):
        self.scope.expr = None
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
        self.scope = self.scope.new_while()
        pass

    # Exit a parse tree produced by MiniCParser#While.
    def exitWhile(self, ctx: MiniCParser.WhileContext):
        self.scope = self.scope.parent

    # Enter a parse tree produced by MiniCParser#block.
    def enterBlock(self, ctx: MiniCParser.BlockContext):
        self.scope = self.scope.new_sub_scope()

    # Exit a parse tree produced by MiniCParser#block.
    def exitBlock(self, ctx: MiniCParser.BlockContext):
        self.scope = self.scope.parent
