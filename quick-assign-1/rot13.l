/*
 * lex sample of a ROT13 encoder/decoder
 *
 * 14 Mar 22  jpb  Creation.
 */

%%
[a-mA-M]  printf ("%c", yytext[0]+13);
[n-zN-Z]  printf ("%c", yytext[0]-13);
%%

