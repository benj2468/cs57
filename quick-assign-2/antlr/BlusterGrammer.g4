grammar BlusterGrammer;

expr	:	EXIT EOF							# ExitExpr
	|	BLAST MESSAGE EOF					# BlastExpr
	|	SEND SPACE USER MESSAGE EOF			# SendExpr
	|	ADD SPACE USER EOF					# AddExpr
	;

MESSAGE: 	(SPACE WORD)+			;


ADD:		[Aa][Dd][Dd]			;
EXIT:		[Ee][Xx][Ii][Tt]		;
SEND:		[Ss][Ee][Nn][Dd]		;
BLAST:		[Bb][Ll][Aa][Ss][Tt]	;
USER:		'@'[a-zA-Z0-9_]+		;
WORD:		[a-zA-Z0-9_.,!]+		;
SPACE:		[ \t]+ 					;
EOL:		[\n\r]					;
WS: 		[ \n\t\r]+ -> skip		;