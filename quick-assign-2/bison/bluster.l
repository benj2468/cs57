/* this is only for scanner, not link with parser yet */
%{
int lineNum = 0;
%}
%%

"ADD" { printf("ADD\n"); }
"SEND" { printf("SEND\n"); }
"BLAST" { printf("BLAST\n"); }
"EXIT" { printf("EXIT\n"); }

%% 