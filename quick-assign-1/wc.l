%{
	int char_count = 0;
	int word_count = 0;
	int line_count = 0;
%}

%%
\n|\r 			{ line_count++; char_count ++; }
[0-9A-Za-z\-]+		{ word_count++; char_count += yyleng;  }
.			char_count++;
%%

int main (int argc, char **argv)
{
	argc--;
	if (argc > 0)
		yyin = fopen (argv[1], "r");
	else
		yyin = stdin;
  	yylex();  // kick off the lexer
  	printf ("Chars: %d, Words: %d, Lines: %d\n", char_count, word_count, line_count);
}
