#include <stdio.h>
int addsub(int a)
{
  int num;
  int b = 4;
  int c, d;

  num = b + 2;     // 6
  c = 4 + 6 + num; // 16
  d = a + 5;       // 10
  if (d > num)
    c = c + b; // 16 + 4 = 20
  else
    c = c - b;

  return num + c + d; // 6 + 20 + 10 = 36
}

int main()
{
  return addsub(5);
}

// b = 4
// num = 6
// c = 16
// d = a + 5
// if (a + 5 > 6)
//  c = 20
// else
//  c = 12
// return 6 + c + c
