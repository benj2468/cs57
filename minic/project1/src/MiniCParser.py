from MiniCErrorListener import MiniCErrorListener
from myAST.AST import *
from myAST.Declarations import *
from myAST.Statements import *
from myAST.Expressions import *
from dist.MiniCParser import MiniCParser
from Scope import Function, Scope, ScopeType, TypedVar


# This class defines a complete listener for a parse tree produced by MiniCParser.
class MyMiniCParser(MiniCParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scope: Scope = Scope()
        self.removeErrorListeners()
        self.listener = MiniCErrorListener()
        self.addErrorListener(self.listener)

    def parse(self, file_ident: str):
        def parse_term(term: MiniCParser.TermContext):
            if term.ident != None:
                ident = term.ident.getText()

                self.scope.check_var(ident)

                return ASTVarNode(ident)
            if term.number != None:
                return ASTIntLiteralNode(int(term.number.text))
            if term.string != None:
                return ASTStrLiteralNode(
                    ", ".join([t.getText() for t in term.string.WORD()])
                )

        def parse_block(block: MiniCParser.BlockContext):
            self.scope = self.scope.new_sub_scope()
            stmts = [parse_stmt(stmt) for stmt in block.stmt()]
            self.scope = self.scope.parent
            return ASTBlockNode(stmts)

        def parse_assignment(assgn: MiniCParser.AssignmentContext):
            self.scope.check_assignment(assgn)
            return ASTAsgnNode(
                assgn.variable().ident.text, parse_expression(assgn.expr())
            )

        def parse_arg(arg: MiniCParser.ArgContext) -> Tuple[ASTDataType, str]:
            ty: ASTDataType = ASTDataType.VOID_T
            argTy = arg.ty.text
            if argTy == "int":
                ty = ASTDataType.INT_T
            elif argTy == "str":
                ty = ASTDataType.STR_T
            elif argTy == "bool":
                ty = ASTDataType.BOOL_T
            elif argTy == "float":
                ty = ASTDataType.FLOAT_T

            return (ty, arg.ident.getText())

        def parse_expression(expr: MiniCParser.ExprContext):
            if type(expr) == MiniCParser.TermExprContext:
                return parse_term(expr.term())
            if type(expr) == MiniCParser.UnOpExprContext:
                op = None
                if expr.U_OP() == "-":
                    op = ASTUOpType.NEG
                else:
                    op = ASTUOpType.POS
                return ASTUExprNode(parse_expression(expr.expr()), op)

            if type(expr) == MiniCParser.BinOpExprContext:
                op = None
                if expr.B_OP().getText() == "+":
                    op = ASTBOpType.ADD
                elif expr.B_OP().getText() == "-":
                    op = ASTBOpType.SUB
                elif expr.B_OP().getText() == "*":
                    op = ASTBOpType.MUL
                elif expr.B_OP().getText() == "/":
                    op = ASTBOpType.DIV
                return ASTBExprNode(
                    parse_expression(expr.left), parse_expression(expr.right), op
                )
            if type(expr) == MiniCParser.ParenExprContext:
                return parse_expression(expr.expr())
            if type(expr) == MiniCParser.CompOpExprContext:
                op = None
                if expr.C_OP().getText() == ">":
                    op = ASTROpType.GT
                elif expr.C_OP().getText() == "<":
                    op = ASTROpType.LT
                elif expr.C_OP().getText() == ">=":
                    op = ASTROpType.GEQ
                elif expr.C_OP().getText() == "<=":
                    op = ASTROpType.LEQ
                elif expr.C_OP().getText() == "==":
                    op = ASTROpType.EQ
                elif expr.C_OP().getText() == "!=":
                    op = ASTROpType.NE
                return ASTRExprNode(
                    parse_expression(expr.left), parse_expression(expr.right), op
                )
            if type(expr) == MiniCParser.FuncCallExprContext:
                funccall = expr.funccall()

                function = Function.from_call_ctx(self.scope, funccall)
                self.scope.check_function(function)

                return ASTCallNode(
                    funccall.ident.text,
                    [parse_expression(arg) for arg in funccall.expr()],
                )
            return None

        def parse_dec(decl: MiniCParser.DecContext):
            if type(decl) == MiniCParser.FunctionDecContext:

                function = Function.from_ctx(decl)
                self.scope.add_function(function)

                func = Function.from_ctx(decl)
                args = [ASTDataType.from_str(ty.getText()) for ty in decl.WORD()[2:]]

                return ASTFuncDeclNode(
                    bool(decl.EXTERN()),
                    ASTDataType.from_str(func.type),
                    func.ident,
                    args,
                )
            if type(decl) == MiniCParser.VariableDecContext:

                arg = decl.arg()
                var = TypedVar(arg.ident.getText(), arg.ty.text)
                self.scope.add_var(var)

                (ty, name) = parse_arg(arg)
                return ASTVarDeclNode(bool(decl.EXTERN()), ty, name)

        def parse_stmt(stm: MiniCParser.StmtContext):
            if type(stm) == MiniCParser.ReturnContext:
                return ASTRetNode(parse_expression(stm.expr()))
            if type(stm) == MiniCParser.ExprStmtContext:
                return parse_expression(stm.expr())
            if type(stm) == MiniCParser.IfElseContext:
                return ASTIfNode(
                    parse_expression(stm.expr()),
                    parse_stmt(stm.stmt(0)),
                    parse_stmt(stm.stmt(1)),
                )
            if type(stm) == MiniCParser.BlockStmtContext:
                return parse_block(stm.block())
            if type(stm) == MiniCParser.AssignContext:
                return parse_assignment(stm.assignment())
            if type(stm) == MiniCParser.WhileContext:
                self.scope = self.scope.new_sub_scope()
                self.scope.ty = ScopeType.LOOP
                node = ASTWhileNode(
                    parse_expression(stm.expr()), parse_stmt(stm.stmt())
                )
                self.scope = self.scope.parent
                return node
            if type(stm) == MiniCParser.DeclareContext:

                arg = stm.arg()
                var = TypedVar(arg.ident.getText(), arg.ty.text)
                self.scope.add_var(var)

                (ty, name) = parse_arg(arg)
                return ASTVarDeclStmtNode(ty, name)
            if type(stm) == MiniCParser.IfContext:
                return ASTIfNode(parse_expression(stm.expr()), parse_stmt(stm.stmt()))

            raise Exception("Unknown statement type: " + str(type(stm)))

        def parse_start(start: MiniCParser.StartContext):
            decls = []
            assignments = []
            functions = []
            for line in start.line():
                dec = line.dec()
                if dec:
                    decls.append(parse_dec(dec))
                assgn = line.assignment()
                if assgn:
                    assignments.append(parse_assignment(assgn))
                funcdef = line.funcdef()
                if funcdef:
                    function = Function.from_ctx(funcdef)
                    self.scope.add_function(function)
                    self.scope = function
                    args = [parse_arg(arg) for arg in funcdef.arg()]
                    functions.append(
                        ASTFuncDefNode(
                            ASTDataType.from_str(function.type),
                            function.ident,
                            args,
                            parse_block(funcdef.block()),
                        )
                    )
                    self.scope = self.scope.parent

            return ASTRootNode(file_ident, decls, assignments, functions)

        return parse_start(self.start())
