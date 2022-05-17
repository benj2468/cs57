#! /bin/sh
make

for file in ./tests/*.c
do
  ./opt-bjc.sh $file
done

rm ./tmp*.ll
