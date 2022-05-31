#! /bin/sh
make

for file in ./tests/*.c
do
  echo "------"
  echo "Running: " $file
  ./opt-bjc.sh $file $file
  $file\_f.sh
  echo "Recieved Output: " $?
  gcc $file -o $file.sh
  $file.sh
  echo "Expected Output: " $?
done

for file in ./ll_tests/*.ll
do
  echo "------"
  echo "Running: " $file
  opt-10 -S -load=./GeneratorPass.so --generatorpass -o ./$file.out.ll < $file > $file.s
  as $file.s -o $file.o
  ld $file.o -o $file\_f.sh
  chmod +x $file\_f.sh
  $file\_f.sh
  echo "Recieved Output: " $?
done


rm -f ll_tests/*.ll.o  ll_tests/*.out* 