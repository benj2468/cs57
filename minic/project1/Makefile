# Switch the two following lines if running on thayer
# ANTLR4 = java -jar /thayerfs/courses/22spring/cosc57/workspace/antlr-4.9.2-complete.jar
ANTLR4=java -jar /usr/local/lib/antlr-4.9.2-complete.jar

all: minic-python minic-java test

minic-python: src/MiniC.g4
	echo "BUILDING PYTHON"
	$(ANTLR4) -Dlanguage=Python3 src/MiniC.g4 -o src/dist/
	cp src/dist/src/* src/dist/ && rm -R -f src/dist/src

minic-java: src/MiniC.g4
	echo "BUILDING JAVA"
	$(ANTLR4) src/MiniC.g4 -o src/dist/
	javac src/dist/src/MiniC*.java
	cp src/dist/src/* src/dist/ && rm -R -f src/dist/src

test:
	echo "TESTING"
	python3 src/main.py src/examples/ex1.c
	python3 src/main.py src/examples/fact.c
	python3 src/main.py src/examples/pyramid.c 
	echo "TESTING DONE"

pull-workspace:
	scp -r f002q3z@babylon4.thayer.dartmouth.edu:/thayerfs/courses/22spring/cosc057/workspace/Project_1 ./workspace

clean:
	rm -f *.cpp