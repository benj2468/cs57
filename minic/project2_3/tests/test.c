int foo(int argc)
{
    int b;
    if (argc == 0)
    {
        b = 100;
    }
    else
    {
        b = 200;
    }
    return b; // Should be 100
}

int main()
{
    return foo(0);
}