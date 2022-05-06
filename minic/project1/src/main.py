import sys
from typing import List
import antlr4
from dist.MiniCLexer import MiniCLexer
from MiniCParser import MyMiniCParser

ERROR_PREFIX = """\
|---------------------------------
| MiniC Compiler Error
|"""

ERROR_POSTFIX = """\
|---------------------------------"""


def print_error(e: str):
    print(ERROR_PREFIX)
    for line in e.split("\n"):
        print("| " + line)
    print(ERROR_POSTFIX)


def raise_exception(_, e: Exception):
    raise e


def main(argv: List[str]):
    input_stream = 0
    file_ident = "input_stream"
    if len(argv) <= 1:
        input_stream = antlr4.StdinStream()
    else:
        file_ident = argv[1]
        input_stream = antlr4.FileStream(argv[1])
        print(argv[1], " ", end="\n")

    codegen = "-c" in argv and argv[argv.index("-c") + 1]
    verbose = "-v" in argv
    emit = not "--no-emit" in argv

    # Tokenize the input
    lexer = MiniCLexer(input_stream)
    stream = antlr4.CommonTokenStream(lexer)

    # Parse it
    parser = MyMiniCParser(stream)
    parser._errHandler.recover = raise_exception

    try:
        # Parse the AST
        ast = parser.parse(file_ident)

        # Print the tree
        if emit:
            ast.print()

        if codegen:
            with open(codegen or "out.cpp", "w") as f:
                f.write(ast.gen())
    except antlr4.RecognitionException:
        print_error("\n".join(parser.listener.getErrors()))
        exit(1)
    except Exception as e:
        if verbose:
            print(e.with_traceback())
        else:
            print_error(str(e))
        exit(1)
    exit(0)


if __name__ == "__main__":
    main(sys.argv)
