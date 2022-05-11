CC=clang-10
CFLAGS=`llvm-config --cflags` -fPIC
CXX=clang++-10
CXXFLAGS=`llvm-config-10 --cxxflags` -fPIC
LDFLAGS=`llvm-config-10 --cxxflags --ldflags --libs`
OPT=opt-10

CPROP=ConstProp


all:	$(CPROP).so

$(CPROP).so:	$(CPROP).o
	$(CXX) --shared -o $(CPROP).so ${LDFLAGS} $^

test:	$(CPROP).so
	$(OPT) -S -load ./$(CPROP).so -constproppass < test/example.ll > /dev/null

clean:
	$(RM) $(CPROP).o $(CPROP).so
