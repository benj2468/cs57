CC=clang
LEX=flex
LDFLAGS=-lfl

all: wc caesar-encode caesar-decode

wc: wc.o
	$(CC) -o $@ $(LDFLAGS) $^

caesar-encode: caesar-encode.o
	$(CC) -o $@ $(LDFLAGS) $^

caesar-decode: caesar-decode.o
	$(CC) -o $@ $(LDFLAGS) $^

test: caesar-encode caesar-decode
	rm -f encoded.txt decoded.txt
	./caesar-encode test.txt >> encoded.txt
	./caesar-decode encoded.txt >> decoded.txt
	cmp test.txt decoded.txt

clean:
	rm -f *.o wc caesar-encode caesar-decode encoded.txt decoded.txt
