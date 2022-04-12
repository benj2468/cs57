# Quick Assignment #2 (ANTLR + BISON)

## How to Run:

1. run `make` in the root
2. To run the antlr version, run `python3 antlr/main.py`
3. To run the bison version, run `bison/bluster`

# TODO

## Bison

- [x] message cannot have the word blast in it
- [x] User is also getting the message in it's yylval

## ANTLR

- [x] send @jie What's going on? Get's parsed as SEND @jie What and doesn't throw an error for the remainder

```
send @jie What's going on?
line 1:14 token recognition error at: '''
None
Sending message: "What" to user: @jie
```

- [x] similar error with exit

```
exit some extra
line 1:4 extraneous input ' some extra' expecting {<EOF>, EOL}
line 2:0 mismatched input '<EOF>' expecting {MESSAGE, ADD, EXIT, SEND, BLAST, USER, WORD, SPACE, EOL, WS}
None
```

- [x] similar error with blast

```
BLAST Are you there?
line 1:19 token recognition error at: '?'
line 2:0 mismatched input '<EOF>' expecting {MESSAGE, ADD, EXIT, SEND, BLAST, USER, WORD, SPACE, EOL, WS}
None
Blast Message: "Are you there"
```
