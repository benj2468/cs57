clang-10 -O -S -Xclang -disable-llvm-passes -emit-llvm $1 -o ./tmp.ll
opt-10 -S -mem2reg -o ./tmp.ll < ./tmp.ll
opt-10 -S -load=./ConstPass.so --constpass < ./tmp.ll
