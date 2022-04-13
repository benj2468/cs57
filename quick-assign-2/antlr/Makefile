# Switch the two following lines if running on thayer
# ANTLR4 = java -jar /thayerfs/courses/22spring/cosc57/workspace/antlr-4.9.2-complete.jar
ANTLR4=java -jar /usr/local/lib/antlr-4.9.2-complete.jar

bluster: BlusterGrammer.g4
	$(ANTLR4) -Dlanguage=Python3 BlusterGrammer.g4 -o dist/