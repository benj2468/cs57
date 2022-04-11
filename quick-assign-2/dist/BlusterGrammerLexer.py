# Generated from BlusterGrammer.g4 by ANTLR 4.9.2
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
    from typing import TextIO
else:
    from typing.io import TextIO



def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\2\t")
        buf.write("K\b\1\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7")
        buf.write("\4\b\t\b\3\2\3\2\3\2\3\2\3\2\3\2\5\2\30\n\2\3\3\3\3\3")
        buf.write("\3\3\3\3\3\3\3\3\3\3\3\5\3\"\n\3\3\4\3\4\3\4\3\4\3\4\3")
        buf.write("\4\3\4\3\4\3\4\3\4\5\4.\n\4\3\5\3\5\3\5\3\5\3\5\3\5\3")
        buf.write("\5\3\5\5\58\n\5\3\6\3\6\6\6<\n\6\r\6\16\6=\3\7\6\7A\n")
        buf.write("\7\r\7\16\7B\3\b\6\bF\n\b\r\b\16\bG\3\b\3\b\2\2\t\3\3")
        buf.write("\5\4\7\5\t\6\13\7\r\b\17\t\3\2\5\6\2\62;C\\aac|\t\2##")
        buf.write("..\60\60\62;C\\aac|\5\2\13\f\17\17\"\"\2Q\2\3\3\2\2\2")
        buf.write("\2\5\3\2\2\2\2\7\3\2\2\2\2\t\3\2\2\2\2\13\3\2\2\2\2\r")
        buf.write("\3\2\2\2\2\17\3\2\2\2\3\27\3\2\2\2\5!\3\2\2\2\7-\3\2\2")
        buf.write("\2\t\67\3\2\2\2\139\3\2\2\2\r@\3\2\2\2\17E\3\2\2\2\21")
        buf.write("\22\7c\2\2\22\23\7f\2\2\23\30\7f\2\2\24\25\7C\2\2\25\26")
        buf.write("\7F\2\2\26\30\7F\2\2\27\21\3\2\2\2\27\24\3\2\2\2\30\4")
        buf.write("\3\2\2\2\31\32\7u\2\2\32\33\7g\2\2\33\34\7p\2\2\34\"\7")
        buf.write("f\2\2\35\36\7U\2\2\36\37\7G\2\2\37 \7P\2\2 \"\7F\2\2!")
        buf.write("\31\3\2\2\2!\35\3\2\2\2\"\6\3\2\2\2#$\7d\2\2$%\7n\2\2")
        buf.write("%&\7c\2\2&\'\7u\2\2\'.\7v\2\2()\7D\2\2)*\7N\2\2*+\7C\2")
        buf.write("\2+,\7U\2\2,.\7V\2\2-#\3\2\2\2-(\3\2\2\2.\b\3\2\2\2/\60")
        buf.write("\7g\2\2\60\61\7z\2\2\61\62\7k\2\2\628\7v\2\2\63\64\7G")
        buf.write("\2\2\64\65\7Z\2\2\65\66\7K\2\2\668\7V\2\2\67/\3\2\2\2")
        buf.write("\67\63\3\2\2\28\n\3\2\2\29;\7B\2\2:<\t\2\2\2;:\3\2\2\2")
        buf.write("<=\3\2\2\2=;\3\2\2\2=>\3\2\2\2>\f\3\2\2\2?A\t\3\2\2@?")
        buf.write("\3\2\2\2AB\3\2\2\2B@\3\2\2\2BC\3\2\2\2C\16\3\2\2\2DF\t")
        buf.write("\4\2\2ED\3\2\2\2FG\3\2\2\2GE\3\2\2\2GH\3\2\2\2HI\3\2\2")
        buf.write("\2IJ\b\b\2\2J\20\3\2\2\2\n\2\27!-\67=BG\3\b\2\2")
        return buf.getvalue()


class BlusterGrammerLexer(Lexer):

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    ADD = 1
    SEND = 2
    BLAST = 3
    EXIT = 4
    USER = 5
    MESSAGE = 6
    WS = 7

    channelNames = [ u"DEFAULT_TOKEN_CHANNEL", u"HIDDEN" ]

    modeNames = [ "DEFAULT_MODE" ]

    literalNames = [ "<INVALID>",
 ]

    symbolicNames = [ "<INVALID>",
            "ADD", "SEND", "BLAST", "EXIT", "USER", "MESSAGE", "WS" ]

    ruleNames = [ "ADD", "SEND", "BLAST", "EXIT", "USER", "MESSAGE", "WS" ]

    grammarFileName = "BlusterGrammer.g4"

    def __init__(self, input=None, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.9.2")
        self._interp = LexerATNSimulator(self, self.atn, self.decisionsToDFA, PredictionContextCache())
        self._actions = None
        self._predicates = None


