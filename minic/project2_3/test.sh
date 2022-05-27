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


rm *.ll