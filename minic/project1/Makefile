# Switch the two following lines if running on thayer
# ANTLR4 = java -jar /thayerfs/courses/22spring/cosc57/workspace/antlr-4.9.2-complete.jar
ANTLR4=java -jar /usr/local/lib/antlr-4.9.2-complete.jar

all: minic-python  test

minic-python: src/MiniC.g4
	echo "BUILDING PYTHON"
	$(ANTLR4) -Dlanguage=Python3 src/MiniC.g4 -o src/dist/
	cp src/dist/src/* src/dist/ && rm -R -f src/dist/src

test:
	echo "TESTING"
	python3 src/main.py src/examples/ex1.c --no-emit
	python3 src/main.py src/examples/fact.c --no-emit 
	python3 src/main.py src/examples/pyramid.c --no-emit
	echo "TESTING DONE"

pull-workspace:
	scp -r f002q3z@babylon4.thayer.dartmouth.edu:/thayerfs/courses/22spring/cosc057/workspace/Project_1 ./workspace

codegen:
	python3 src/main.py ${FILE} -c out.cpp --no-emit
	clang++ -g -O3 out.cpp `llvm-config --cxxflags --ldflags --system-libs --libs core` -o gen
	./gen

clean:
	rm -f *.cpp
	rm -f -r  *.dSYM