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
#define DEBUG_TYPE "constprop"

// Sample statistics. Replace with ones that represent your pass
STATISTIC(BBCount, "Total number of basic blocks");
STATISTIC(InstCount, "Total number of instructions");

// Beginning of anonymous namespace. Keeping it anonymous prevents duplicate
// namespaces from occurring, especially when merging code into the LLVM
// pass directory (which we will not be doing.)
namespace {
  struct ConstPropPass : public FunctionPass {
    static char ID;
    ConstPropPass() : FunctionPass(ID) {}

    void handleInstruction(Instruction &I) {
	if (I.isBinaryOp())
	{
		errs() << "Operand 1: " << *I.getOperand(0)->getType() << "\n";
		errs() << "Operand 2: " << I.getOperand(0)->getValueID() << "\n";
		errs() << "Opearnd 2: " << I.getOperand(1)->getValueID() << "\n";
		
	}	    
    };

    void handleBlock(BasicBlock &B) {
	for (auto &I: B) {
	    errs() << "I: " << I <<"\n";
	    handleInstruction(I);
	}
    };
    
    // The main (and most important) function. This is the entry point for
    // your the work your pass will do. The sample here prints the function
    // name, then the function, then the function broken into basic blocks
    // and finally into instructions. All output is to stderr.
    virtual bool runOnFunction(Function &F) {
      for (auto &B : F) {
	  errs() << "Another Block\n";
          handleBlock(B);
      }
      return false;  // returning false means the overall CFG has not changed
    }
  };
}

// You can change the friendly and long names in RegisterPass to your own pass
// name. 
char ConstPropPass::ID = 0;
static RegisterPass<ConstPropPass> X("constproppass", "Skeleton Pass",
			false,  /* looks at CFG, true changed CFG */
			false); /* analysis pass, true means analysis needs to run again */

// Automatically enable the pass.
// http://adriansampson.net/blog/clangpass.html
static void registerConstPropPass(const PassManagerBuilder &,
                         legacy::PassManagerBase &PM) {
  PM.add(new ConstPropPass());
}
static RegisterStandardPasses
  RegisterMyPass(PassManagerBuilder::EP_EarlyAsPossible,
                 registerConstPropPass);
