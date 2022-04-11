grammar BlusterGrammer;

expr	:	EXIT						# ExitExpr
	|	BLAST MESSAGE					# BlastExpr
	|	SEND SPACE USER MESSAGE			# SendExpr
	|	ADD SPACE USER					# AddExpr
	;

MESSAGE: 	(SPACE WORD)+			;


ADD:		('add'|'ADD')			;
SEND:		('send'|'SEND')			;
BLAST:		('blast'|'BLAST')		;
EXIT:		('exit'|'EXIT')			;
USER:		'@'[a-zA-Z0-9_]+		;
WORD:		[a-zA-Z0-9_.,!]+		;
SPACE:		[ \t]+					;
WS: 		[ \n\t\r]+ -> skip		;