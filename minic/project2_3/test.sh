#! /bin/sh
make

# for file in ./tests/*.c
# do
#   echo "------"
#   echo "Running: " $file
#   ./opt-bjc.sh $file $file
#   $file\_f.sh
#   echo "Recieved Output: " $?
#   gcc $file -o $file.sh
#   $file.sh
#   echo "Expected Output: " $?
# done

for file in ./ll_tests/*.ll
do
  echo "------"
  echo "Running: " $file
  ./opt-bjc2.sh $file $file
  $file\_f.sh
  echo "Recieved Output: " $?
  # clang-10 $file -S -mllvm --x86-asm-syntax=intel -o $file.a
  # as $file.a -o $file.o
  # ld $file.o -o $file.sh
  # chmod +x $file.sh
  # $file.sh
  # echo "Expected Output: " $?
done


rm -f ll_tests/*.ll.o ll_tests/*_f.sh ll_tests/*.out* ll_tests/*.sh