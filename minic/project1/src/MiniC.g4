grammar MiniC;

// Start rule
start: line*;

line: funcdec # FuncDec | funcdef # FuncDef;

funcdec:
	EXTERN? ty = WORD ident = WORD LPAREN (WORD (COMMA WORD)*)? RPAREN SEMICOLON;
funcdef:
	ty = WORD ident = WORD LPAREN (arg (COMMA arg)*)? RPAREN block;

expr:
	left = term B_OP right = term						# BinOp
	| U_OP term											# UnOp
	| left = expr C_OP right = expr						# CompOp
	| term												# TermExpr
	| ident = WORD LPAREN (expr (COMMA expr)*)? RPAREN	# FuncCall
	| .													# ErrorExpr;

term: WORD # Variable | NUMBER # Constant;

stmt:
	WORD EQUALS expr SEMICOLON # Assign
	// Will need to check that it's the right kind of expression :) 
	| RETURN expr SEMICOLON					# Return
	| arg SEMICOLON							# Declare
	| WHILE LPAREN expr RPAREN stmt			# While
	| IF LPAREN expr RPAREN stmt			# If
	| IF LPAREN expr RPAREN stmt ELSE stmt	# IfElse
	| block									# BlockStmt;

block: LBRACKET stmt* RBRACKET;

arg: ty = WORD ident = WORD;

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
WS: [ \t\n\r]+ -> skip;
