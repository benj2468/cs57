import sys
from antlr4 import *
from dist.antlr.BlusterGrammerLexer import BlusterGrammerLexer
from dist.antlr.BlusterGrammerParser import BlusterGrammerParser
from typing import List

MESSAGE_MAX_LEN = 81
USER_MAX_LEN = 16


def is_message_valid(message: List[tree.Tree.TerminalNodeImpl]):
    if len(message.getText()) > MESSAGE_MAX_LEN:
        raise Exception("MESSAGE TOO LONG")
    return message


def is_user_valid(user: tree.Tree.TerminalNodeImpl):
    if len(user.getText()) > USER_MAX_LEN:
        raise Exception("USER TOO LONG")
    return user


class BlusterListener(ParseTreeListener):

    # Enter a parse tree produced by BlusterGrammerParser#ExitExpr.
    def enterExitExpr(self, ctx: BlusterGrammerParser.ExitExprContext):
        pass

    # Exit a parse tree produced by BlusterGrammerParser#ExitExpr.
    def exitExitExpr(self, ctx: BlusterGrammerParser.ExitExprContext):
        sys.exit(0)

    # Enter a parse tree produced by BlusterGrammerParser#BlastExpr.
    def enterBlastExpr(self, ctx: BlusterGrammerParser.BlastExprContext):
        pass

    # Exit a parse tree produced by BlusterGrammerParser#BlastExpr.
    def exitBlastExpr(self, ctx: BlusterGrammerParser.BlastExprContext):
        message = is_message_valid(ctx.MESSAGE()).getText().strip()
        print(f"Blast Message: \"{message}\"")

    # Enter a parse tree produced by BlusterGrammerParser#SendExpr.
    def enterSendExpr(self, ctx: BlusterGrammerParser.SendExprContext):
        pass

    # Exit a parse tree produced by BlusterGrammerParser#SendExpr.
    def exitSendExpr(self, ctx: BlusterGrammerParser.SendExprContext):
        message = is_message_valid(ctx.MESSAGE()).getText().strip()
        user = is_user_valid(ctx.USER())
        print(f"Sending message: \"{message}\" to user: {user}")

    # Enter a parse tree produced by BlusterGrammerParser#AddExpr.
    def enterAddExpr(self, ctx: BlusterGrammerParser.AddExprContext):
        pass

    # Exit a parse tree produced by BlusterGrammerParser#AddExpr.
    def exitAddExpr(self, ctx: BlusterGrammerParser.AddExprContext):
        user = is_user_valid(ctx.USER())
        print(f"Adding User: {user}")

    # Enter a parse tree produced by BlusterGrammerParser#UnRecExpr.
    def enterUnRecExpr(self, ctx: BlusterGrammerParser.UnRecExprContext):
        pass

    # Exit a parse tree produced by BlusterGrammerParser#UnRecExpr.
    def exitUnRecExpr(self, ctx: BlusterGrammerParser.UnRecExprContext):
        raise Exception("UNRECOGNIZED COMMAND")


def main(argv):
    input_stream = 0
    if (len(argv) <= 1):
        input_stream = StdinStream()
    else:
        input_stream = FileStream(argv[1])
        print(argv[1], ' ', end='\n')

    # Tokenize the input
    lexer = BlusterGrammerLexer(input_stream)
    stream = CommonTokenStream(lexer)

    # Parse it
    parser = BlusterGrammerParser(stream)
    parser._errHandler = BailErrorStrategy()
    tree = parser.start()

    print(tree.exception)

    # Walk the tree, counting up words
    listener = BlusterListener()
    walker = ParseTreeWalker()
    walker.walk(listener, tree)


if __name__ == "__main__":
    main(sys.argv)
