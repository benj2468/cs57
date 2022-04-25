grammar MiniC;

// Start rule
start: line*;

// A line is a component of the global scope
line: dec | funcdef | assignment;

dec:
	EXTERN? ty = WORD ident = WORD LPAREN (WORD (COMMA WORD)*)? RPAREN SEMICOLON	# FunctionDec
	| EXTERN? arg SEMICOLON															# VariableDec;

// -----------------------------------------------------------------------------
// ------------------------------ Functions ------------------------------------
// -----------------------------------------------------------------------------

/*
 A function declaration contains: 1. An option extern 2. A return type 3. A function name 4. A list
 of parameters
 */
/* A function definition contains 1. A return type 2. A function name 3. A list of parameters 4. A block with stmts */
funcdef:
	ty = WORD ident = WORD LPAREN (arg (COMMA arg)*)? RPAREN scope = block;
/* A function call contains 1. a function name 2. a list of parameters */
funccall: ident = WORD LPAREN (expr (COMMA expr)*)? RPAREN;

// -----------------------------------------------------------------------------
// ------------------------ Expressions & Statements ---------------------------
// -----------------------------------------------------------------------------

// Expressions
expr:
	// A parenthesized expression
	LPAREN expr RPAREN # ParenExpr
	// A Binary expression with a left and a right component
	| left = expr B_OP right = expr # BinOpExpr
	// A unary expression with a right component
	| U_OP expr # UnOpExpr
	// A comparator expression with a left and a right component
	| left = expr C_OP right = expr # CompOpExpr
	// An expression can also just be a regular term
	| term # TermExpr
	// An expression can also be a function call which returns a value
	| funccall # FuncCallExpr;

// A Term is either a variable (WORD) or a literal (INTEGER, (etc, if we wanted to implement more))
term: ident = variable | number = NUMBER | string = stringlit;

// Statements
stmt:
	// A statement can be a variable assignment
	assignment # Assign
	// A statement can be a return value - semantic analysis will need to check that this is in a function/block
	| RETURN expr? SEMICOLON # Return
	// A statement can be a declaration of a variable
	| arg SEMICOLON # Declare
	// A stmt can be a while loop
	| WHILE expr stmt # While
	// A stmt can be an if block
	| IF expr stmt # If
	// A stmt can also be an ifelse block
	| IF expr stmt ELSE stmt # IfElse
	// A stmt can also just be a normal block (sub-scope, or somponent of if/else)
	| block	# BlockStmt
	| expr	# ExprStmt;

// A block contains a new scope
block: LBRACKET stmt* RBRACKET;

// An Assignment
assignment: variable EQUALS expr SEMICOLON;

// An arg is really a typed variable, but this is used in various locations
arg: ty = WORD ident = variable;
// A variable is a subcomponent of a many things, and we always want to check it's validity so we extract it here
variable: ident = WORD;
// A string is a string literal
stringlit: DQUOTE literal = WORD DQUOTE;

// Keywords
EXTERN: 'extern';
WHILE: 'while';
IF: 'if';
ELSE: 'else';
RETURN: 'return';

// Tokens
WORD: [a-zA-Z_]+;
NUMBER: [0-9]+;
B_OP: [+-/*];
U_OP: [-];
C_OP: ('==' | '!=' | '>' | '<' | '>=' | '<=');
EQUALS: '=';

// Special Characters
LPAREN: '(';
RPAREN: ')';
COMMA: ',';
LBRACKET: '{';
RBRACKET: '}';
SEMICOLON: ';';
DQUOTE: '"';

// Spaces
// 
// (Whitespace is ignored)
// 
// C doesn't care about spaces, so we are getting rid of all of them here.
WS: [ \t\n\r]+ -> skip;
