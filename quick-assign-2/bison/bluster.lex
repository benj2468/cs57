%{
    #import "bluster.tab.h"
%}

%option noyywrap

word        [a-zA-Z0-9_.,!]+
user        @[a-zA-Z0-9_]{1,15}
space       [ \t]+

%%

[Ee][Xx][Ii][Tt]        { return EXIT; }
[Aa][Dd][Dd]            { char *foo = malloc(yyleng); strncpy(foo, yytext, yyleng); yylval.val = foo; return ADD; }
[Ss][Ee][Nn][Dd]        { char *foo = malloc(yyleng); strncpy(foo, yytext, yyleng); yylval.val = foo; return SEND; }
[Bb][Ll][Aa][Ss][Tt]    { char *foo = malloc(yyleng); strncpy(foo, yytext, yyleng); yylval.val = foo; return BLAST; }
{word}                  { char *foo = malloc(yyleng); strncpy(foo, yytext, yyleng); yylval.val = foo; return WORD; }
{user}                  { char *foo = malloc(yyleng); strncpy(foo, yytext, yyleng); yylval.val = foo; return USER; }

[\n\r]                  { return EOL; }
{space}                 { return SPACE; } 
.                       { printf("Unrecognized Character"); }
%%