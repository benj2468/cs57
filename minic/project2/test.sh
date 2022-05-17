#! /bin/sh
make

for file in ./tests/*.c
do
  echo $file
  ./opt-bjc.sh $file
donew

rm ./tmp*.ll
