/*
 * lex sample of a ROT3 encoder/decoder
 *
 */

%{
	#define ROTATION 3
	char rot(char);
%}

%%
[A-Za-z]	printf("%c", rot(yytext[0]));
%%


char rot(char c)
{
	int ascii = (int)c;
	int is_upper = ascii < 0x61;
	if (is_upper == 1) ascii += 0x20;
	
	int mapped = ascii + ROTATION;
	if (mapped > 0x7a) mapped = 0x61 + (mapped % 0x7b);
	if (is_upper) mapped -= 0x20;
	return (char)mapped;
}

