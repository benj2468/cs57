//
// LLVM Function Pass Template
//
// Parts taken from skeleton Copyright (c) 2015 Adrian Sampson at
// https://github.com/sampsyo/llvm-pass-skeleton/blob/master/skeleton/Skeleton.cpp
// License file included in directory.
//
// 01 May 2022  jpb   Creation from foundational works shown.
//
// Other parts taken from here https://github.com/llvm-mirror/llvm/blob/master/lib/Transforms/Scalar/ConstantProp.cpp
//
// 11 May 2022  bjc   Project 2
//

#include "llvm/Pass.h"
#include "llvm/ADT/Statistic.h"
#include "llvm/IR/Function.h"
#include "llvm/Analysis/ConstantFolding.h"
#include "llvm/Analysis/TargetLibraryInfo.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/IR/LegacyPassManager.h"
#include "llvm/Transforms/IPO/PassManagerBuilder.h"

using namespace llvm;

// Change the DEBUG_TYPE define to the friendly name of your pass
#define DEBUG_TYPE "constprop"

// Beginning of anonymous namespace. Keeping it anonymous prevents duplicate
// namespaces from occurring, especially when merging code into the LLVM
// pass directory (which we will not be doing.)
namespace
{
  struct ConstPropPass : public FunctionPass
  {
    static char ID;
    ConstPropPass() : FunctionPass(ID) {}

    void handleInstruction(Instruction *I, const DataLayout &DL, TargetLibraryInfo *TL)
    {
      if (Constant *C = ConstantFoldInstruction(I, DL, TL))
      {
        errs() << "Replacing Instruction: (" << I << ") With Constant: (" << C << ")\n";
        I->replaceAllUsesWith(C);
        for (auto &U : I->uses())
        {
          handleInstruction(cast<Instruction>(I), DL, TL);
        }
      }
    };

    void getAnalysisUsage(AnalysisUsage &AU) const override
    {
      AU.setPreservesCFG();
      AU.addRequired<TargetLibraryInfoWrapperPass>();
    }

    // The main (and most important) function. This is the entry point for
    // your the work your pass will do. The sample here prints the function
    // name, then the function, then the function broken into basic blocks
    // and finally into instructions. All output is to stderr.
    virtual bool runOnFunction(Function &F) override
    {
      const llvm::DataLayout &DL = F.getParent()->getDataLayout();
      TargetLibraryInfo *TLI =
          &getAnalysis<TargetLibraryInfoWrapperPass>().getTLI(F);

      for (auto &B : F)
      {
        for (Instruction &I : B)
        {
          handleInstruction(&I, DL, TLI);
        }
      }
      return false; // returning false means the overall CFG has not changed
    }
  };
}

// You can change the friendly and long names in RegisterPass to your own pass
// name.
char ConstPropPass::ID = 0;
static RegisterPass<ConstPropPass> X("constproppass", "Constant Propagation Pass",
                                     false,  /* looks at CFG, true changed CFG */
                                     false); /* analysis pass, true means analysis needs to run again */

// Automatically enable the pass.
// http://adriansampson.net/blog/clangpass.html
static void registerConstPropPass(const PassManagerBuilder &,
                                  legacy::PassManagerBase &PM)
{
  PM.add(new ConstPropPass());
}
static RegisterStandardPasses
    RegisterMyPass(PassManagerBuilder::EP_EarlyAsPossible,
                   registerConstPropPass);
