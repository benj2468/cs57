CC=clang-10
CFLAGS=`llvm-config --cflags` -fPIC
CXX=clang++-10
CXXFLAGS=`llvm-config-10 --cxxflags` -fPIC
LDFLAGS=`llvm-config-10 --cxxflags --ldflags --libs`
OPT=opt-10

ASM := as
PROJECT := foo

CPASS=ConstPass
DPASS=DeadPass
GPASS2=GeneratorPass

MY_OPT=opt-bjc

all: $(CPASS).so $(DPASS).so $(GPASS2).so

$(CPASS).so: $(CPASS).o
	$(CXX) --shared -o $(CPASS).so ${LDFLAGS} $^

$(DPASS).so: $(DPASS).o
	$(CXX) --shared -o $(DPASS).so ${LDFLAGS} $^

$(GPASS2).so: $(GPASS2).o
	$(CXX) --shared -o $(GPASS2).so ${LDFLAGS} $^

clean:
	$(RM) $(CPASS).o $(CPASS).so $(DPASS).o $(DPASS).so $(GPASS).o $(GPASS).so $(GPASS2).o $(GPASS2).so *.ll tests/*.ll *.c *.o *.s *_f.sh
	$(RM) tests/*.o tests/*.sh tests/*.s
	$(RM) ll_tests/*.ll.o ll_tests/*_f.sh ll_tests/*.out* ll_tests/*.ll.s
