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

MY_OPT=opt-bjc


$(MY_OPT): $(CPASS).so $(DPASS).so
	echo "$(CC) -O -S -Xclang -disable-llvm-passes -emit-llvm \$$1 -o ./tmp1.ll" > $(MY_OPT).sh
	echo "$(OPT) -S -mem2reg -o ./tmp2.ll < ./tmp1.ll" >> $(MY_OPT).sh
	echo "$(OPT) -S -load=./$(CPASS).so --$(CPASSFLAG) -o ./tmp3.ll < ./tmp2.ll" >> $(MY_OPT).sh
	echo "$(OPT) -S -load=./$(DPASS).so --$(DPASSFLAG) -o ./tmp4.ll < ./tmp3.ll" >> $(MY_OPT).sh
	echo "$(OPT) -S -load=./$(CPASS).so --$(CPASSFLAG) -o ./\$$1.out.ll < ./tmp4.ll" >> $(MY_OPT).sh
	chmod +x $(MY_OPT).sh

$(CPASS).so: $(CPASS).o
	$(CXX) --shared -o $(CPASS).so ${LDFLAGS} $^

$(DPASS).so: $(DPASS).o
	$(CXX) --shared -o $(DPASS).so ${LDFLAGS} $^

clean:
	$(RM) $(CPASS).o $(CPASS).so $(DPASS).o $(DPASS).so *.ll $(MY_OPT).sh tests/*.ll
