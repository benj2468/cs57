clang-10 -O -S -Xclang -disable-llvm-passes -emit-llvm $1 -o ./tmp1.ll
opt-10 -S -mem2reg -o ./tmp2.ll < ./tmp1.ll
opt-10 -S -load=./ConstPass.so --constpass -o ./tmp3.ll < ./tmp2.ll
opt-10 -S -load=./DeadPass.so --deadpass -o ./tmp4.ll < ./tmp3.ll
opt-10 -S -load=./ConstPass.so --constpass -o ./tmp5.ll < ./tmp4.ll
opt-10 -S -load=./GeneratorPass.so --generatorpass -o ./$1.out.ll < ./tmp5.ll > $2.s
as $2.s -o $2.o
ld $2.o -o $2_f.sh
chmod +x $2_f.sh