%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int yylex();
void yyerror(char *s);

%}

%start prog

%union {
  char *val;
}

%token <val> WORD USER
%token EOL EXIT ADD BLAST SEND SPACE

%type <val> message

%%

prog: exp
  |   prog exp
  ;

exp:    EXIT                                    { exit(1); }
    |   ADD SPACE USER EOL                      { printf("Adding user: %s\n", $3); }
    |   BLAST message                     { printf("Blasting: %s\n", $2); }
    |   SEND SPACE USER message EOL       { printf("Sending: \"%s\" to %s\n", $4, $3); }
    ;

message:  SPACE WORD                      
    |     message SPACE WORD
    ;        


%%

int main(int argc, char **argv)
{
  yyparse();

  return 1;
}

void yyerror(char *s)
{
  fprintf(stderr, "error: %s\n", s);

  exit(0);
}

