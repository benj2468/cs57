int f(void)
{
    return 2;
}

int main(void)
{
    int a = 0;
    int b;
    if (a == 1)
    {
        b = a + 9;
    }
    else
    {
        b = a + 10;
    }
    b += 1;
    return f() / (a + 1 + 1 + 1 + b);
}