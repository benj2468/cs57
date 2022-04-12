%{
    #import "bluster.tab.h"
%}

%option noyywrap

word        [a-zA-Z0-9_.,!]{1,80}
user        @[a-zA-Z0-9_]{1,15}
space       [ \t]+

%%

[Aa][Dd][Dd]                 { return ADD; }
[Ee][Xx][Ii][Tt]             { return EXIT; }
[Ss][Ee][Nn][Dd]             { return SEND; }
[Bb][Ll][Aa][Ss][Tt]         { return BLAST; }
{word}                       { yylval.val = yytext; return WORD; }
{user}                       { yylval.val = yytext; return USER; }

[\n\r]          { return EOL; }
{space}         { return SPACE; } 
. {}
%%