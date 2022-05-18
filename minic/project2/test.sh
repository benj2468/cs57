#! /bin/sh
make

for file in ./tests/*.c
do
  echo $file
  ./opt-bjc.sh $file
done

rm ./tmp*.ll
