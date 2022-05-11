CC=clang-10
CFLAGS=`llvm-config --cflags` -fPIC
CXX=clang++-10
CXXFLAGS=`llvm-config-10 --cxxflags` -fPIC
LDFLAGS=`llvm-config-10 --cxxflags --ldflags --libs`
OPT=opt-10

CPROP=ConstProp

$(CPROP)Pass.sh: $(CPROP).so
	echo $(OPT) -S -load ./$(CPROP).so -constproppass >> $@
	chmod +x $@

$(CPROP).so: $(CPROP).o
	$(CXX) --shared -o $(CPROP).so ${LDFLAGS} $^

clean:
	$(RM) $(CPROP).o $(CPROP).so $(CPROP)Pass.sh
