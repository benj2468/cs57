bluster: bluster.y bluster.lex
	bison -d bison/bluster.y -o bison/bluster.tab.c
	flex -o bison/lex.yy.c bison/bluster.lex 
	cc -o bison/$@ bison/bluster.tab.c bison/lex.yy.c