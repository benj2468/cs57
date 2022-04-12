%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int yylex();
void yyerror(char *s);

#define MAX_MESSAGE_LEN 80

%}

%start prog

%union {
  char *val;
  int len;
}

%token <val> WORD USER ADD BLAST SEND
%token EOL EXIT SPACE

%type <val> message
%type <val> word

%%

prog: exp
  |   prog exp
  ;

exp:    EXIT EOL                                { exit(0); }
    |   ADD SPACE USER EOL                      { printf("Adding user: %s\n", $3); }
    |   BLAST message EOL                       { 
      if (strlen($2)-1 > MAX_MESSAGE_LEN) {
        printf("Message too long.\n");
        exit(1);
      }
      printf("Blasting: %s\n", $2); 
    }
    |   SEND SPACE USER message EOL             { 
      if (strlen($4)-1 > MAX_MESSAGE_LEN) {
        printf("Message too long.\n");
        exit(1);
      }
      printf("Sending: \"%s\" to %s\n", $4, $3); 
    }
    ;

message:  SPACE word { $$ = $2; }                      
    |     message SPACE word { $$ = $1; strcat($$, " "); strcat($$, $3); }
    ;  

word: WORD | BLAST | ADD | SEND;


%%

int main(int argc, char **argv)
{
  yyparse();

  return 1;
}

void yyerror(char *s)
{
  fprintf(stderr, "error: %s\n", s);

  exit(1);
}

