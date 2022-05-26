#include <stdio.h>
int addsub(int a)
{
    int num;
    int b = 4;
    int c, d;

    num = b + 2;     // 6
    c = 4 + 6 + num; // 16
    d = a + 5;       // 10
    c = c - b;       // 12

    return num + c + d; // 6 + 12 + 10 = 28
}

int main()
{
    return addsub(5); // Should be 28
}