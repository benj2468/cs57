int looper(int i)
{
    int j = 0;
    while (j < i)
    {
        j += 2;
    }
    return j;
}

int main()
{
    return looper(5);
}