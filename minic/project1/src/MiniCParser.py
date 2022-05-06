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
        # Build up the grand scope for the program
        self.scope: Scope = Scope()
        # Remove the standard error listeners - they suck
        self.removeErrorListeners()
        # Use our custom error listener that prints pretty errors
        self.listener = MiniCErrorListener()
        self.addErrorListener(self.listener)

    def parse(self, file_ident: str):

        # Parses a term, differentiating between identifiers and literals
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

        # Block Parser Helper
        def parse_block(block: MiniCParser.BlockContext):
            # When we parse a block we also move into a subscope!
            self.scope = self.scope.new_sub_scope()
            stmts = [parse_stmt(stmt) for stmt in block.stmt()]
            # Once we are done parsing all of it's statements we move back into the parent scope
            self.scope = self.scope.parent
            return ASTBlockNode(stmts)

        # Assignment Parser Helper
        def parse_assignment(assgn: MiniCParser.AssignmentContext):
            self.scope.check_assignment(assgn)
            return ASTAsgnNode(
                assgn.variable().ident.text, parse_expression(assgn.expr())
            )

        # Argument Pardser Helper
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

        # Top Level Parser for Expressions
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

                # Build our representation of a function - this helps with scoping stuff
                function = Function.from_call_ctx(self.scope, funccall)
                # Check to make sure the function has been defined in our scope
                self.scope.check_function(function)

                return ASTCallNode(
                    funccall.ident.text,
                    [parse_expression(arg) for arg in funccall.expr()],
                )
            return None

        # Top Level Parser for Declarations
        def parse_dec(decl: MiniCParser.DecContext):
            if type(decl) == MiniCParser.FunctionDecContext:

                # Build up our representation of a function
                func = Function.from_ctx(decl)
                # Add the function to our scope
                self.scope.add_function(func)

                args = [ASTDataType.from_str(ty.getText()) for ty in decl.WORD()[2:]]

                return ASTFuncDeclNode(
                    bool(decl.EXTERN()),
                    ASTDataType.from_str(func.type),
                    func.ident,
                    args,
                )
            if type(decl) == MiniCParser.VariableDecContext:

                arg = decl.arg()

                # Build up our representation of a variable
                var = TypedVar(arg.ident.getText(), arg.ty.text)
                # Add the variable to our scope
                self.scope.add_var(var)

                (ty, name) = parse_arg(arg)
                return ASTVarDeclNode(bool(decl.EXTERN()), ty, name)

        # Top Level Parser for Statements
        def parse_stmt(stm: MiniCParser.StmtContext):
            if type(stm) == MiniCParser.ReturnContext:
                # recursively parse
                return ASTRetNode(parse_expression(stm.expr()))
            if type(stm) == MiniCParser.ExprStmtContext:
                # Since an expression can be used as a stmt, lets recursively parse here
                return parse_expression(stm.expr())
            if type(stm) == MiniCParser.IfElseContext:
                # recursively parse
                return ASTIfNode(
                    parse_expression(stm.expr()),
                    parse_stmt(stm.stmt(0)),
                    parse_stmt(stm.stmt(1)),
                )
            if type(stm) == MiniCParser.BlockStmtContext:
                # recursively parse
                return parse_block(stm.block())
            if type(stm) == MiniCParser.AssignContext:
                # recursively parse
                return parse_assignment(stm.assignment())
            if type(stm) == MiniCParser.WhileContext:
                # When we parse a while we also move into a subscope!
                self.scope = self.scope.new_sub_scope()
                self.scope.ty = ScopeType.LOOP
                node = ASTWhileNode(
                    parse_expression(stm.expr()), parse_stmt(stm.stmt())
                )
                # Once we are done parsing all of it's statements, and the expression we move back into the parent scope
                self.scope = self.scope.parent
                return node
            if type(stm) == MiniCParser.DeclareContext:
                arg = stm.arg()

                # Build up our representation of a variable
                var = TypedVar(arg.ident.getText(), arg.ty.text)
                # Add the variable to our scope
                self.scope.add_var(var)

                (ty, name) = parse_arg(arg)
                return ASTVarDeclStmtNode(ty, name)
            if type(stm) == MiniCParser.IfContext:
                return ASTIfNode(parse_expression(stm.expr()), parse_stmt(stm.stmt()))

            raise Exception("Unknown statement type: " + str(type(stm)))

        # Top Level Parser for a Module/Context
        # This gathers all the delcarations, assignments, and functions and parses them into a single AST.
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
                    # Build up our representation of a function
                    function = Function.from_ctx(funcdef)
                    # ADd the function to our scope, as if it were declared
                    self.scope.add_function(function)
                    # Change the current scope to the scope of our function (function in inherits scope)
                    self.scope = function
                    # Parse the arguments of the function
                    args = [parse_arg(arg) for arg in funcdef.arg()]

                    # Parse the body of the function
                    body = parse_block(funcdef.block())

                    # Create the AST function
                    functions.append(
                        ASTFuncDefNode(
                            ASTDataType.from_str(function.type),
                            function.ident,
                            args,
                            body,
                        )
                    )
                    # Return to the parent scope
                    self.scope = self.scope.parent

            return ASTRootNode(file_ident, decls, assignments, functions)

        return parse_start(self.start())
