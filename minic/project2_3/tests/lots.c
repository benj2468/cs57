int a(int i)
{
    int b = 10;
    int a = i + b;
    if (a > 5)
    {
        return -1;
    }
    return 1;
}

int b(int i)
{
    if (i > 0)
    {
        return 1;
    }
    return -1;
}

int c(int i)
{
    if (i == 4)
    {
        return b(i);
    }
    return a(i);
}

int d(int i)
{
    int d = i + 5;        // 10
    int e = d / 2;        // 5
    int f = e * 5;        // 25
    int g = f - 10;       // 15
    int h = g + 4;        // 19
    int j = i + h + c(h); // 5 + 19 - 1 = 23

    return (j + 5); // 28
}

int small()
{
    return 2;
}

int main()
{
    return d(5);
}