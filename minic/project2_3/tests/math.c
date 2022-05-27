#include <stdio.h>
int addsub(int a)
{
  int num;
  int b = 4;
  int c, d;

  num = b + 2;     // 6
  c = 4 + 6 + num; // 16
  d = a * 5;       // 25
  if (b != 0)
    c = c / b; // 4

  return num + c + d; // 6 + 4 + 25 = 35
}

int main()
{
  return addsub(5); // Should be 35
}