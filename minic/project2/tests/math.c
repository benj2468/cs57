#include <stdio.h>
int addsub(int a)
{
  int num;
  int b = 4;
  int c, d;

  num = b + 2;
  c = 4 + 6 + num;
  d = a * 5;
  if (b != 0)
    c = c / b;

  return num + c + d;
}

int main()
{
  return addsub(5);
}