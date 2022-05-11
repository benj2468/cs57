CC=clang-10
CFLAGS=`llvm-config --cflags` -fPIC
CXX=clang++-10
CXXFLAGS=`llvm-config-10 --cxxflags` -fPIC
LDFLAGS=`llvm-config-10 --cxxflags --ldflags --libs`
OPT=opt-10

CPASS=ConstPass
CPASSFLAG = $(shell echo $(CPASS) | tr A-Z a-z)


$(CPASS).sh: $(CPASS).so
	echo $(OPT) -S -load ./$(CPASS).so -$(CPASSFLAG) > $@
	chmod +x $@

$(CPASS).so: $(CPASS).o
	$(CXX) --shared -o $(CPASS).so ${LDFLAGS} $^

clean:
	$(RM) $(CPASS).o $(CPASS).so $(CPASS).sh
