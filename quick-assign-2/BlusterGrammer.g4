grammar BlusterGrammer;

expr	:	EXIT			# ExitExpr
	|	BLAST MESSAGE		# BlastExpr
	|	SEND USER MESSAGE	# SendExpr
	|	ADD USER			# AddExpr
	;


ADD:		('add'|'ADD')			;
SEND:		('send'|'SEND')			;
BLAST:		('blast'|'BLAST')		;
EXIT:		('exit'|'EXIT')			;
USER:		'@'[a-zA-Z0-9_]+		;
MESSAGE: 	[a-zA-Z0-9_.,!]+		;
WS: 		[ \n\t\r]+ -> skip		;