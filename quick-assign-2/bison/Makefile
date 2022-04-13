bluster: bluster.y bluster.lex
	bison -d bluster.y -o bluster.tab.c
	flex -o lex.yy.c bluster.lex 
	cc -o $@ bluster.tab.c lex.yy.c