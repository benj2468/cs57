//
// LLVM Function Constant Prop/Folding Pass
//
// Parts taken from skeleton Copyright (c) 2015 Adrian Sampson at
// https://github.com/sampsyo/llvm-pass-skeleton/blob/master/skeleton/Skeleton.cpp
// License file included in directory.
//
// 01 May 2022  jpb   Creation from foundational works shown.
//
//
// 11 May 2022  bjc   Project 2
//
#include "llvm/ADT/Statistic.h"
#include "llvm/Pass.h"
#include "llvm/IR/InstIterator.h"
#include "llvm/IR/NoFolder.h"
#include "llvm/IR/Type.h"
#include "llvm/IR/Function.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/IR/LegacyPassManager.h"
#include "llvm/IR/InstrTypes.h"
#include "llvm/Transforms/IPO/PassManagerBuilder.h"
#include "llvm/IR/IRBuilder.h"
#include "llvm/Transforms/Utils/BasicBlockUtils.h"
#include "llvm/Analysis/TargetLibraryInfo.h"

using namespace llvm;

// Change the DEBUG_TYPE define to the friendly name of your pass
#define DEBUG_TYPE "constprop"

// Beginning of anonymous namespace. Keeping it anonymous prevents duplicate
// namespaces from occurring, especially when merging code into the LLVM
// pass directory (which we will not be doing.)
namespace
{
  struct ConstPass : public FunctionPass
  {
    static char ID;
    ConstPass() : FunctionPass(ID) {}

    int getInt(Value *val)
    {
      if (llvm::ConstantInt *CI = dyn_cast<llvm::ConstantInt>(val))
      {
        return CI->getSExtValue();
      }
      return 0;
    }

    Constant *MyConstantFolder(Instruction *I)
    {
      errs() << "Trying to fold: " << I << "\n";
      if (!all_of(I->operands(), [](Use &U)
                  { return isa<Constant>(U); }))
        return nullptr;

      Constant *Op1;
      if (I->getNumOperands() > 0)
        Op1 = dyn_cast<Constant>(I->getOperand(0));
      Constant *Op2;
      if (I->getNumOperands() > 1)
        Op2 = dyn_cast<Constant>(I->getOperand(1));

      int opResult = 0;
      bool knownCase = false;

      if (const auto *CI = dyn_cast<CmpInst>(I))
      {
        knownCase = true;
        // It is a compare instruction - fold that
        CmpInst::Predicate Pred = CI->getPredicate();
        switch (Pred)
        {
        case CmpInst::Predicate::ICMP_EQ:
          opResult = getInt(Op1) == getInt(Op2);
        case CmpInst::Predicate::ICMP_NE:
          opResult = getInt(Op1) != getInt(Op2);
        case CmpInst::Predicate::ICMP_SGE:
          opResult = getInt(Op1) >= getInt(Op2);
        case CmpInst::Predicate::ICMP_SGT:
          opResult = getInt(Op1) > getInt(Op2);
        case CmpInst::Predicate::ICMP_SLE:
          opResult = getInt(Op1) <= getInt(Op2);
        case CmpInst::Predicate::ICMP_SLT:
          opResult = getInt(Op1) < getInt(Op2);
        default:
          knownCase = false;
        }
      }
      else if (const auto *LI = dyn_cast<LoadInst>(I))
      {

        // It is a load instruction - fold that??
      }
      else if (const auto *IVI = dyn_cast<InsertValueInst>(I))
      {
        // It is an insert value instruction - fold that??
      }
      else if (const auto *EVI = dyn_cast<ExtractValueInst>(I))
      {
        // It is an extract value instruction - fold that??
      }
      else
      {
        knownCase = true;
        // Handle the opeartions cases
        unsigned op_code = I->getOpcode();
        return ConstantExpr::get(op_code, Op1, Op2);

        switch (op_code)
        {
        case Instruction::Add:
          opResult = getInt(Op1) + getInt(Op2);
        case Instruction::Sub:
          opResult = getInt(Op1) - getInt(Op2);
        case Instruction::Mul:
          opResult = getInt(Op1) * getInt(Op2);
        case Instruction::FDiv:
          opResult = getInt(Op1) / getInt(Op2);
        case Instruction::UnaryOps::FNeg:
          opResult = -getInt(Op1);
        }
      }
      if (!knownCase)
        return nullptr;

      return ConstantInt::get(I->getType(), APInt(I->getType()->getIntegerBitWidth(), opResult));
    }

    Instruction *handleInstruction(Instruction *I)
    {
      if (Constant *C = MyConstantFolder(I))
      {
        errs() << "Replacing Instruction: (" << I << ") With Constant: (" << getInt(C) << ")\n";

        I->replaceAllUsesWith(C);

        return I;
      }
      return nullptr;
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

      std::vector<Instruction *> ToDelete;
      for (inst_iterator I = inst_begin(F), E = inst_end(F); I != E; ++I)
      {
        if (Instruction *R = handleInstruction(&*I))
        {
          ToDelete.push_back(R);
        }
      };
      for (auto I : ToDelete)
      {
        if (I->isSafeToRemove())
          I->removeFromParent();
      }
      return false; // returning false means the overall CFG has not changed
    };
  };
};

// You can change the friendly and long names in RegisterPass to your own pass
// name.
char ConstPass::ID = 0;
static RegisterPass<ConstPass> X("constpass", "Constant Propagation/Folding Pass",
                                 false,  /* looks at CFG, true changed CFG */
                                 false); /* analysis pass, true means analysis needs to run again */

// Automatically enable the pass.
// http://adriansampson.net/blog/clangpass.html
static void registerConstPass(const PassManagerBuilder &,
                              legacy::PassManagerBase &PM)
{
  PM.add(new ConstPass());
};
static RegisterStandardPasses
    RegisterMyPass(PassManagerBuilder::EP_EarlyAsPossible,
                   registerConstPass);
