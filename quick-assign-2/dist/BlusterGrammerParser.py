# Generated from BlusterGrammer.g4 by ANTLR 4.9.2
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO


def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\3\t")
        buf.write("\17\4\2\t\2\3\2\3\2\3\2\3\2\3\2\3\2\3\2\3\2\5\2\r\n\2")
        buf.write("\3\2\2\2\3\2\2\2\2\20\2\f\3\2\2\2\4\r\7\6\2\2\5\6\7\5")
        buf.write("\2\2\6\r\7\b\2\2\7\b\7\4\2\2\b\t\7\7\2\2\t\r\7\b\2\2\n")
        buf.write("\13\7\3\2\2\13\r\7\7\2\2\f\4\3\2\2\2\f\5\3\2\2\2\f\7\3")
        buf.write("\2\2\2\f\n\3\2\2\2\r\3\3\2\2\2\3\f")
        return buf.getvalue()


class BlusterGrammerParser ( Parser ):

    grammarFileName = "BlusterGrammer.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [  ]

    symbolicNames = [ "<INVALID>", "ADD", "SEND", "BLAST", "EXIT", "USER", 
                      "MESSAGE", "WS" ]

    RULE_expr = 0

    ruleNames =  [ "expr" ]

    EOF = Token.EOF
    ADD=1
    SEND=2
    BLAST=3
    EXIT=4
    USER=5
    MESSAGE=6
    WS=7

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.9.2")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class ExprContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return BlusterGrammerParser.RULE_expr

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)



    class SendExprContext(ExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BlusterGrammerParser.ExprContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def SEND(self):
            return self.getToken(BlusterGrammerParser.SEND, 0)
        def USER(self):
            return self.getToken(BlusterGrammerParser.USER, 0)
        def MESSAGE(self):
            return self.getToken(BlusterGrammerParser.MESSAGE, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSendExpr" ):
                listener.enterSendExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSendExpr" ):
                listener.exitSendExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSendExpr" ):
                return visitor.visitSendExpr(self)
            else:
                return visitor.visitChildren(self)


    class AddExprContext(ExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BlusterGrammerParser.ExprContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def ADD(self):
            return self.getToken(BlusterGrammerParser.ADD, 0)
        def USER(self):
            return self.getToken(BlusterGrammerParser.USER, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAddExpr" ):
                listener.enterAddExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAddExpr" ):
                listener.exitAddExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAddExpr" ):
                return visitor.visitAddExpr(self)
            else:
                return visitor.visitChildren(self)


    class BlastExprContext(ExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BlusterGrammerParser.ExprContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def BLAST(self):
            return self.getToken(BlusterGrammerParser.BLAST, 0)
        def MESSAGE(self):
            return self.getToken(BlusterGrammerParser.MESSAGE, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterBlastExpr" ):
                listener.enterBlastExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitBlastExpr" ):
                listener.exitBlastExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitBlastExpr" ):
                return visitor.visitBlastExpr(self)
            else:
                return visitor.visitChildren(self)


    class ExitExprContext(ExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BlusterGrammerParser.ExprContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def EXIT(self):
            return self.getToken(BlusterGrammerParser.EXIT, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterExitExpr" ):
                listener.enterExitExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitExitExpr" ):
                listener.exitExitExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitExitExpr" ):
                return visitor.visitExitExpr(self)
            else:
                return visitor.visitChildren(self)



    def expr(self):

        localctx = BlusterGrammerParser.ExprContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_expr)
        try:
            self.state = 10
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [BlusterGrammerParser.EXIT]:
                localctx = BlusterGrammerParser.ExitExprContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 2
                self.match(BlusterGrammerParser.EXIT)
                pass
            elif token in [BlusterGrammerParser.BLAST]:
                localctx = BlusterGrammerParser.BlastExprContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 3
                self.match(BlusterGrammerParser.BLAST)
                self.state = 4
                self.match(BlusterGrammerParser.MESSAGE)
                pass
            elif token in [BlusterGrammerParser.SEND]:
                localctx = BlusterGrammerParser.SendExprContext(self, localctx)
                self.enterOuterAlt(localctx, 3)
                self.state = 5
                self.match(BlusterGrammerParser.SEND)
                self.state = 6
                self.match(BlusterGrammerParser.USER)
                self.state = 7
                self.match(BlusterGrammerParser.MESSAGE)
                pass
            elif token in [BlusterGrammerParser.ADD]:
                localctx = BlusterGrammerParser.AddExprContext(self, localctx)
                self.enterOuterAlt(localctx, 4)
                self.state = 8
                self.match(BlusterGrammerParser.ADD)
                self.state = 9
                self.match(BlusterGrammerParser.USER)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





