import sys
from antlr4 import *
from dist.MiniCLexer import MiniCLexer
from MiniCParser import MyMiniCParser


def main(argv):
    input_stream = 0
    file_ident = "input_stream"
    print(",".join(argv))
    if len(argv) <= 1:
        input_stream = StdinStream()
    else:
        file_ident = argv[1]
        input_stream = FileStream(argv[1])
        print(argv[1], " ", end="\n")

    print(",".join(argv))

    codegen = len(argv) > 2 and argv[2] == "-c"

    # Tokenize the input
    lexer = MiniCLexer(input_stream)
    stream = CommonTokenStream(lexer)

    # Parse it
    parser = MyMiniCParser(stream)

    try:
        # Parse the AST
        ast = parser.parse(file_ident)

        # Print the tree
        ast.print()

        if codegen:

            with open(argv[3] or "out.cpp", "w") as f:
                f.write(ast.gen())

    except Exception as e:
        print(e.with_traceback())


if __name__ == "__main__":
    main(sys.argv)
