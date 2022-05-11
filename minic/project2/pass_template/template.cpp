//
// LLVM Function Pass Template
//
// Parts taken from skeleton Copyright (c) 2015 Adrian Sampson at 
// https://github.com/sampsyo/llvm-pass-skeleton/blob/master/skeleton/Skeleton.cpp
// License file included in directory.
//
// 01 May 2022  jpb  Creation from foundational works shown.
//

#include "llvm/Pass.h"
#include "llvm/ADT/Statistic.h"
#include "llvm/IR/Function.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/IR/LegacyPassManager.h"
#include "llvm/Transforms/IPO/PassManagerBuilder.h"

using namespace llvm;

// Change the DEBUG_TYPE define to the friendly name of your pass
#define DEBUG_TYPE "skeletonpass"

// Sample statistics. Replace with ones that represent your pass
STATISTIC(BBCount, "Total number of basic blocks");
STATISTIC(InstCount, "Total number of instructions");

// Beginning of anonymous namespace. Keeping it anonymous prevents duplicate
// namespaces from occurring, especially when merging code into the LLVM
// pass directory (which we will not be doing.)
namespace {
  struct SkeletonPass : public FunctionPass {
    static char ID;
    SkeletonPass() : FunctionPass(ID) {}

    // The main (and most important) function. This is the entry point for
    // your the work your pass will do. The sample here prints the function
    // name, then the function, then the function broken into basic blocks
    // and finally into instructions. All output is to stderr.
    virtual bool runOnFunction(Function &F) {
      // use local variables to total for each function found. The 
      // Statistics will total all functions.
      int bbct = 0, instct = 0;

      errs() << "++++++++++++++++++++\n";
      errs() << "In a function called " << F.getName() << ":\n";

      errs() << "Function body:\n";
      F.print(llvm::errs());
      errs() << "--------------------\n";

      // Basic blocks in functions
      for (auto &B : F) {
	++BBCount; ++bbct;
        errs() << "Basic block " << bbct << ":\n";
        B.print(llvm::errs());

      errs() << "--------------------\n";

	// Instructions in basic blocks
        errs() << "Instructions: \n";
        for (auto &I : B) {
	  ++InstCount; ++instct;
	  errs() << instct << ". ";
          I.print(llvm::errs(), true);
          errs() << "\n";
        }
      }
      errs() << "Grand total is " << BBCount << " basic blocks, and " << InstCount << " instructions.\n";

      return false;  // returning false means the overall CFG has not changed
    }
  };
}

// You can change the friendly and long names in RegisterPass to your own pass
// name. 
char SkeletonPass::ID = 0;
static RegisterPass<SkeletonPass> X("skeletonpass", "Skeleton Pass",
			false,  /* looks at CFG, true changed CFG */
			false); /* analysis pass, true means analysis needs to run again */

// Automatically enable the pass.
// http://adriansampson.net/blog/clangpass.html
static void registerSkeletonPass(const PassManagerBuilder &,
                         legacy::PassManagerBase &PM) {
  PM.add(new SkeletonPass());
}
static RegisterStandardPasses
  RegisterMyPass(PassManagerBuilder::EP_EarlyAsPossible,
                 registerSkeletonPass);
