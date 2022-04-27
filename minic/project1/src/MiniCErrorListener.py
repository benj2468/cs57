from typing import List
from antlr4 import DiagnosticErrorListener
import sys


class MiniCErrorListener(DiagnosticErrorListener):
    def __init__(self):
        super().__init__()
        self.errors: List[str] = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self.errors.append("line " + str(line) + ":" + str(column) + " " + msg)

    def getErrors(self) -> List[str]:
        return self.errors
