grammar BlusterGrammer;

// Start rule
start: line (EOL line)* EOF;

line:	EXIT							# ExitExpr
	|	BLAST MESSAGE					# BlastExpr
	|	SEND SPACE USER MESSAGE			# SendExpr
	|	ADD SPACE USER					# AddExpr
	|	.								# UnRecExpr
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
