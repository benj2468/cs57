# Goal

Create an LLVM function pass(s) that do(es) constant propagation, constant folding, and dead code elimination.

# Plan

Use process here: https://llvm.org/docs/WritingAnLLVMPass.html

Look into Mark/Sweep for Dead Code Removal

# TODO
- [ ] Allow legitimate access to registers, and I guess use the stack somehow to keep track of where we've put things.

# Design Brief

> This is a page or less describing your function pass design, the average number of
> passes it takes to evaluate the code to a steady state, other passes that work in concert with your pass
> (if any), any issues or problems you had with the design or building of the pass, and how to run the
> pass. Companies or academia expect some sort of design paper when you are building software – for
> this course we don’t need a book, just a few paragraphs describing what you did.

I have coded a single function pass, called ConstPass. This pass deals with Constant Propagation and Constant Folding. It is a simple single pass that deals with all propogation. Since variables are used in order, this works effectively at getting all constant variables propogated in a single pass. 

Constant Propogation is simple. In order, consider an instruction. If the instruction can be evaluated at compile time, then evaluate it, and propogate it's value to all uses it it, which will always be in consequent lines. This means we do not need to alter previous lines, once we have reached line $x$, all lines $[0..x]$ will have been fixed.

Consant folding is also simple, and happens in line with Constant propogation! Since we also all consecutive lines when we propogate, getting to an instruction that who's operands are all constants means we can fold the instruction, calculate it, and propogate it as well. Therefore these two components are heavily interdependent.

By propogating in place, we actually are performing more looks at each instruction that usualy. This means we might end up looking at a single instruction up to three times, two times to update a `Use` of a variable to a constant value (propagating), and a third time when we actually see that instruction. This is OK, becuase we know we will only ever see each instruction at most a constant number of times, therefore keeping our runtime linear. Furthermore, we don't need to worry ourselves about extra complexity and extra space.

I should note that this implementation is incredibly limited. it assumes all variables are of type `i32`, it also assumes that you are not ever returning a value from a function (i.e. all functions are `void` type).

Before running the `ConstPass` make sure to run the `mem2reg` pass. This removes all `alloca`s and `load`s, and allows us to simply work solely on arithmetic operations.

The structure of the application is very simple. It loops over every instruction, and consider each one, one by one. In considering an instruction, we atttempt to fold it, using `MyConstantFolder`. This function will, provided that all the operands of the instruction are constants, perform the operations in compile time, and return an `llvm::Constant` with the calculated value.

We consider a few different cases, as well as some sub-cases that correspond to the expressions that we allowed for in project1
- Comparison Expression -> CmpInst::Predicate::*
- Arithmetic Operation -> Instruction::Add, Instruction::Mult, Instruction::FDiv, Instruction::Sub
- Unary Operations -> Instruction::UnaryOps::FNeg

We calculate a `opResult`, and then store our `opResult` in a `ConstantInt` (since we on'y have to deal with `i32`s)

This has been updated to be a **Module Pass** to enhance folding on the entire module. The pass still performs folding within functions on everything described above, but now also performs the following folding:

1. If a function returns a single value, which is a constant, replace all instances of the value returned from the call instruction with the constant value to potentially fold other values on compile time.
2. Evaluate constant PHI nodes
    - This will need to be run AFTER Dead Code removal is run, becuase the dead basic blocks make the PHI nodes redundant.


### Extra Credit Dead Code Remove

Dead code removal is currently being built, but performs the following tasks:

1. will simplify conditional branches that have constant evaluations
2. will remove basic blocks that have no predecessors


# Testing

To test, simply add a `C` file into the tests/ directory, build the optimizer (`make`), and then run the test script: `./test.sh`. It will convert all the files in `/test` to IR, run `mem2reg` on them, then run our `constpass`, and finally run `deadpass`. It should then output them in the tests file to view. If you want to do more constand folding, for example on redundant phi nodes (since you removed some dead code, there might be some more constants that can be folded) go ahead and run it again!