# opt-10 -S -mem2reg -o ./tmp2.ll < $1
# opt-10 -S -load=./ConstPass.so --constpass -o ./tmp3.ll < ./tmp2.ll
# opt-10 -S -load=./DeadPass.so --deadpass -o ./tmp4.ll < ./tmp3.ll
# opt-10 -S -load=./ConstPass.so --constpass -o ./tmp5.ll < ./tmp4.ll
opt-10 -S -load=./GeneratorPass.so --generatorpass -o ./$1.out.ll < $1 > $2.s
as $2.s -o $2.o
ld $2.o -o $2_f.sh
chmod +x $2_f.sh