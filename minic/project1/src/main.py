import sys
from antlr4 import *
from dist.MiniCLexer import MiniCLexer
from dist.MiniCParser import MiniCParser
from dist.MiniCListener import MiniCListener


def main(argv):
    input_stream = 0
    if (len(argv) <= 1):
        input_stream = StdinStream()
    else:
        input_stream = FileStream(argv[1])
        print(argv[1], ' ', end='\n')

    # Tokenize the input
    lexer = MiniCLexer(input_stream)
    stream = CommonTokenStream(lexer)

    # Parse it
    parser = MiniCParser(stream)

    try:
        tree = parser.start()

        print(tree.toStringTree(recog=parser))

        # Walk the tree, counting up words
        listener = MiniCListener()
        walker = ParseTreeWalker()
        walker.walk(listener, tree)
    except NoViableAltException as e:
        print(e)
    except RecognitionException as e:
        print(e)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main(sys.argv)
