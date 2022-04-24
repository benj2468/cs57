grammar MiniC;

// Start rule
start: line*;

// A line is a component of the global scope
line: funcdec | funcdef | stmt;

// -----------------------------------------------------------------------------
// ------------------------------ Functions ------------------------------------
// -----------------------------------------------------------------------------

/*
 A function declaration contains: 1. An option extern 2. A return type 3. A function name 4. A list
 of parameters
 */
funcdec:
	EXTERN? ty = WORD ident = WORD LPAREN (WORD (COMMA WORD)*)? RPAREN SEMICOLON;

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
	// A Binary expression with a left and a right component
	left = term B_OP right = term # BinOp
	// A unary expression with a right component
	| U_OP term # UnOp
	// A comparator expression with a left and a right component
	| left = expr C_OP right = expr # CompOp
	// An expression can also just be a regular term
	| term # TermExpr
	// An expression can also be a function call which returns a value
	| funccall # FuncCallExpr;

// A Term is either a variable (WORD) or a literal (INTEGER, (etc, if we wanted to implement more))
term: ident = variable | value = NUMBER;

// Statements
stmt:
	// A statement can be a variable assignment
	variable EQUALS expr SEMICOLON # Assign
	// A statement can be a return value - semantic analysis will need to check that this is in a function/block
	| RETURN expr SEMICOLON # Return
	// A statement can be a declaration of a variable
	| arg SEMICOLON # Declare
	// A stmt can simply be a function call
	| funccall SEMICOLON # FuncCallStmt
	// A stmt can be a while loop
	| WHILE LPAREN expr RPAREN stmt # While
	// A stmt can be an if block
	| IF LPAREN expr RPAREN stmt # If
	// A stmt can also be an ifelse block
	| IF LPAREN expr RPAREN stmt ELSE stmt # IfElse
	// A stmt can also just be a normal block (sub-scope, or somponent of if/else)
	| block # BlockStmt;

// A block contains a new scope
block: LBRACKET stmt* RBRACKET;

// An arg is really a typed variable, but this is used in various locations
arg: ty = WORD ident = variable;
// A variable is a subcomponent of a many things, and we always want to check it's validity so we extract it here
variable: ident = WORD;

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

// Spaces
// 
// (Whitespace is ignored)
// 
// C doesn't care about spaces, so we are getting rid of all of them here.
WS: [ \t\n\r]+ -> skip;
