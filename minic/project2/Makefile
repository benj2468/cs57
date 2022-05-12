CC=clang-10
CFLAGS=`llvm-config --cflags` -fPIC
CXX=clang++-10
CXXFLAGS=`llvm-config-10 --cxxflags` -fPIC
LDFLAGS=`llvm-config-10 --cxxflags --ldflags --libs`
OPT=opt-10

CPASS=ConstPass
CPASSFLAG = $(shell echo $(CPASS) | tr A-Z a-z)

optimize.sh: $(CPASS).so
	echo "$(CC) -O -S -Xclang -disable-llvm-passes -emit-llvm \$$1 -o ./tmp.ll" > optimize.sh
	echo "$(OPT) -S -mem2reg -o ./tmp.ll < ./tmp.ll" >> optimize.sh
	echo "$(OPT) -S -load=./$(CPASS).so --$(CPASSFLAG) < ./tmp.ll" >> optimize.sh
	chmod +x optimize.sh

$(CPASS).so: $(CPASS).o
	$(CXX) --shared -o $(CPASS).so ${LDFLAGS} $^

clean:
	$(RM) $(CPASS).o $(CPASS).so
