
all: bluster-antlr bluster-bison

bluster-antlr: 
	cd antlr && make

bluster-bison:
	cd bison && make
	

clean:
	rm -f -R antlr/dist/* 
	rm -f bison/*.tab.* bison/bluster bison/lex.yy.c