# Project 3

## Description

This project was to take in compiled, and partially optimized IR, and output assembly that can run the program!

## Design Brief

### Overview of the Structure

All of my work for this assignment can be found in the [GeneratorPass2.cpp](../project2/GeneratorPass2.cpp) file. I chose to build this as an LLVM pass, becuase I figured using LLVM's structure of instructions would save me the work of building my own datastructures to parse instructions from simple IR. While it might have been easier for me to code this in python, I didn't want the extra overhead of antlr to deal with, and that ended up being fine.

So, the way this works. The pass simply loops over all the functions in a program, and all the basic blocks within those functions, and for each instruction, build assemply that roughly corresponds to that instruction. IR->Assembly is not a 1:1 mapping though, nor is a clear x->Y function. In fact, there are some dependencies that exist, for example PHI nodes result in not-so-simple logic that is dependent both on blocks that are seen before the PHI node, and affect the block itself. Therefore, for example, in my implementation, at the end of every basic block, we push %rbx to the stack, put into %rbx the number block that we are leaving. Then, whenever we enter into a new block, we either use %rbx to determine which block we came from (for the PHI node), or we don't need to becuase there's no PHI node, and then we pop %rbx to returns its potentially important value. 

Adding, Subtracting are simply. Dividing is a bit tricky, since we need to zero out %rdx. Also pretty simple though, since we only worry about integers, we can push %rdx to the stack, zero it out, do the division, and then pop it back.

I did decide, that in order to make life easier, and since we only ever will have at most one argument, to set aside %rdi to always be the argument registers. So within a function, %rdi will never be used as a register for something else. That being said, %rdi can change (recursive), push %rdi for current scope, make recursive call, pop %rdi back in. 

I use temporary registers during my first back, and then when the generation actually happens we fill them in with real registers. This made coding MUCH easier. I refactored a lot to make this change. Alother thing this allows me to do, is very easily reset the registers at the beginning of each function. Since all I'm using is a temporary integer variable that increments each time we need to assign a new register, it's very easy to just set it back to 0 and start over for a new function!

My code consists of three major classes.


1. **Generator**: Runs through Functions, BasicBlocks, and Instructions. This is the actual Pass Class.
2. **Memory**: Handles temporary registers, and keeps a DS that maps Values to their virtual registers for future lookup.
3. **X86Builder**: For wrapping x86 Instructions. Though each instruction is not its own class (like Ben's code), this keeps me from needing to format the lines each time I write one. This class also allows for a second pass to assign registers. (Although my assignment is not clever at this point, it very well could become clever), and the level of abstraction allows this to happen in the `assign` function.

Maybe some more...?



### Pipeline

```
C File --(clang-10)>> IR --(Project 2)>> Optimized IR --(Project 3)>> Assembly --(as)>> Machine Code
```

### Testing

Place a c file you wish to test in the `./tests` directory. Then, simply run `./test.sh` and it will load the c files into the pipeline. This will run `make` and loop through each test. It will also build using `gcc` and run to compare exit values!



# Contributors

- Benjamin Cape '22
