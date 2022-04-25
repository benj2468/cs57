import sys
from antlr4 import *
from dist.MiniCLexer import MiniCLexer
from dist.MiniCParser import MiniCParser
from MiniCListener import MyMiniCListener


def main(argv):
    input_stream = 0
    if len(argv) <= 1:
        input_stream = StdinStream()
    else:
        input_stream = FileStream(argv[1])
        print(argv[1], " ", end="\n")

    # Tokenize the input
    lexer = MiniCLexer(input_stream)
    stream = CommonTokenStream(lexer)

    # Parse it
    parser = MiniCParser(stream)

    try:
        tree = parser.start()

        # Walk the tree, counting up words
        listener = MyMiniCListener()
        walker = ParseTreeWalker()
        walker.walk(listener, tree)

        listener.ast.print()

    except Exception as e:
        print(e.with_traceback())


if __name__ == "__main__":
    main(sys.argv)
