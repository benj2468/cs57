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
GPASS=GeneratorPass

CPASSFLAG = $(shell echo $(CPASS) | tr A-Z a-z)
DPASSFLAG = $(shell echo $(DPASS) | tr A-Z a-z)
GPASSFLAG = $(shell echo $(GPASS) | tr A-Z a-z)

MY_OPT=opt-bjc

all: $(CPASS).so $(DPASS).so $(GPASS).so

$(CPASS).so: $(CPASS).o
	$(CXX) --shared -o $(CPASS).so ${LDFLAGS} $^

$(DPASS).so: $(DPASS).o
	$(CXX) --shared -o $(DPASS).so ${LDFLAGS} $^

$(GPASS).so: $(GPASS).o
	$(CXX) --shared -o $(GPASS).so ${LDFLAGS} $^

clean:
	$(RM) $(CPASS).o $(CPASS).so $(DPASS).o $(DPASS).so $(GPASS).o $(GPASS).so *.ll tests/*.ll *.c *.o *.s *_f.sh
