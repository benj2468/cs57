import sys
from antlr4 import *
from dist.BlusterGrammerLexer import BlusterGrammerLexer
from dist.BlusterGrammerParser import BlusterGrammerParser
from dist.BlusterGrammerVisitor import BlusterGrammerVisitor

MESSAGE_MAX_LEN = 80
USER_MAX_LEN = 15

def is_message_valid(message: str):
    if len(message.getText()) > MESSAGE_MAX_LEN:
        raise Exception("MESSAGE TOO LONG")
    return message

def is_user_valid(user: str):
    if len(user.getText()) > USER_MAX_LEN:
        raise Exception("USER TOO LONG")
    return user

class BlusterVisistor(BlusterGrammerVisitor):
    def visitExitExpr(self, ctx:BlusterGrammerParser.ExitExprContext):
        print(ctx.getText())
        print("Goodbye")
        sys.exit(0)

    def visitBlastExpr(self, ctx:BlusterGrammerParser.BlastExprContext):
        message = is_message_valid(ctx.MESSAGE())
        return f"Blast Message: {message}"
    
    def visitSendExpr(self, ctx:BlusterGrammerParser.SendExprContext):
        message = is_message_valid(ctx.MESSAGE())
        user = is_user_valid(ctx.USER())
        return f"Sending message: {message} to user: ${user}"

    def visitAddExpr(self, ctx:BlusterGrammerParser.AddExprContext):
        user = is_user_valid(ctx.USER())
        return f"Adding User: {user}"

def main():
    while 1:
        data = InputStream(input(">>> "))
        # lexer
        lexer = BlusterGrammerLexer(data)
        stream = CommonTokenStream(lexer)
        # parser
        parser = BlusterGrammerParser(stream)
        tree = parser.expr()
        # evaluator
        visitor = BlusterVisistor()
        try:
            output = visitor.visit(tree)
            print(output)
        except Exception as e:
            print(f"ERROR Invalid tokens: {e}")


if __name__ == '__main__':
    main()
