# Goal

Create an LLVM function pass(s) that do(es) constant propagation, constant folding, and dead code elimination.

# Plan

Use process here: https://llvm.org/docs/WritingAnLLVMPass.html

Look into Mark/Sweep for Dead Code Removal

# Design Brief

> This is a page or less describing your function pass design, the average number of
> passes it takes to evaluate the code to a steady state, other passes that work in concert with your pass
> (if any), any issues or problems you had with the design or building of the pass, and how to run the
> pass. Companies or academia expect some sort of design paper when you are building software – for
> this course we don’t need a book, just a few paragraphs describing what you did.
