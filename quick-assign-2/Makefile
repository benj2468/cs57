ANTLR4=antlr4

all: bluster-antlr bluster-bison

bluster-antlr: antlr/
	$(ANTLR4) -Dlanguage=Python3 antlr/BlusterGrammer.g4 -o antlr/dist

bluster-bison:  bison/
	bison -d bison/bluster.y -o bison/bluster.tab.c
	flex -o bison/lex.yy.c bison/bluster.lex 
	cc -o bison/$@ bison/bluster.tab.c bison/lex.yy.c