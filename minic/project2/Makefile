CC=clang-10
CFLAGS=`llvm-config --cflags` -fPIC
CXX=clang++-10
CXXFLAGS=`llvm-config-10 --cxxflags` -fPIC
LDFLAGS=`llvm-config-10 --cxxflags --ldflags --libs`
OPT=opt-10

CPASS=ConstPass
DPASS=DeadPass
CPASSFLAG = $(shell echo $(CPASS) | tr A-Z a-z)
DPASSFLAG = $(shell echo $(DPASS) | tr A-Z a-z)

OTPIMIZE = optimize.sh

$(OTPIMIZE): $(CPASS).so $(DPASS).so
	echo "$(CC) -O -S -Xclang -disable-llvm-passes -emit-llvm \$$1 -o ./tmp1.ll" > optimize.sh
	echo "$(OPT) -S -mem2reg -o ./tmp2.ll < ./tmp1.ll" >> optimize.sh
	echo "$(OPT) -S -load=./$(CPASS).so --$(CPASSFLAG) -o ./tmp3.ll < ./tmp2.ll" >> optimize.sh
	echo "$(OPT) -S -load=./$(DPASS).so --$(DPASSFLAG) -o ./\$$1.out.ll < ./tmp3.ll" >> optimize.sh
	chmod +x $(OTPIMIZE)

$(CPASS).so: $(CPASS).o
	$(CXX) --shared -o $(CPASS).so ${LDFLAGS} $^

$(DPASS).so: $(DPASS).o
	$(CXX) --shared -o $(DPASS).so ${LDFLAGS} $^

clean:
	$(RM) $(CPASS).o $(CPASS).so $(DPASS).o $(DPASS).so *.ll $(OTPIMIZE)

test:
	./$(OTPIMIZE) ./tests/*
	rm ./tmp*.ll
