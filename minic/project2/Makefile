CC=clang-10
CFLAGS=`llvm-config --cflags` -fPIC
CXX=clang++
CXXFLAGS=`llvm-config --cxxflags` -fPIC
LDFLAGS=`llvm-config --cxxflags --ldflags --libs`
OPT=opt

CONSTPROPPASS=constprop


all:	${CONSTPROPPASS}

$(CONSTPROPPASS):
	$(CXX) lib/Transforms/${CONSTPROPPASS}.cpp --shared -o build/$(CONSTPROPPASS).so ${LDFLAGS} 

test:	$(CONSTPROPPASS)
	$(OPT) -load ./build/$(CONSTPROPPASS).so -constprop < test/example.ll > /dev/null

# clean:
# 	$(RM) $(TEMPLATENAME).o $(TEMPLATENAME).so
