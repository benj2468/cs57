# Generated from BlusterGrammer.g4 by ANTLR 4.9.2
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .BlusterGrammerParser import BlusterGrammerParser
else:
    from BlusterGrammerParser import BlusterGrammerParser

# This class defines a complete generic visitor for a parse tree produced by BlusterGrammerParser.

class BlusterGrammerVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by BlusterGrammerParser#ExitExpr.
    def visitExitExpr(self, ctx:BlusterGrammerParser.ExitExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by BlusterGrammerParser#BlastExpr.
    def visitBlastExpr(self, ctx:BlusterGrammerParser.BlastExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by BlusterGrammerParser#SendExpr.
    def visitSendExpr(self, ctx:BlusterGrammerParser.SendExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by BlusterGrammerParser#AddExpr.
    def visitAddExpr(self, ctx:BlusterGrammerParser.AddExprContext):
        return self.visitChildren(ctx)



del BlusterGrammerParser