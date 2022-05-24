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
#define DEBUG_TYPE "constpass"

// Beginning of anonymous namespace. Keeping it anonymous prevents duplicate
// namespaces from occurring, especially when merging code into the LLVM
// pass directory (which we will not be doing.)
namespace
{
  int getInt(Value *val)
  {
    if (llvm::ConstantInt *CI = dyn_cast<llvm::ConstantInt>(val))
    {
      return CI->getSExtValue();
    }
    return 0;
  }

  // Helper struct to manage a constant instruction
  struct ConstantInstruction
  {
    Instruction *I;
    Constant *Op1;
    Constant *Op2;

    bool knownCase = false;
    int opResult = 0;

    ConstantInstruction(Instruction *Inst)
    {
      I = Inst;
      if (I->getNumOperands() > 0)
        Op1 = dyn_cast<Constant>(I->getOperand(0));
      if (I->getNumOperands() > 1)
        Op2 = dyn_cast<Constant>(I->getOperand(1));
    }

    void handleCmpInst()
    {
      CmpInst *CI = dyn_cast<CmpInst>(I);

      CmpInst::Predicate Pred = CI->getPredicate();
      switch (Pred)
      {
      case CmpInst::Predicate::ICMP_EQ:
        opResult = getInt(Op1) == getInt(Op2);
        break;
      case CmpInst::Predicate::ICMP_NE:
        opResult = getInt(Op1) != getInt(Op2);
        break;
      case CmpInst::Predicate::ICMP_SGE:
        opResult = getInt(Op1) >= getInt(Op2);
        break;
      case CmpInst::Predicate::ICMP_SGT:
        opResult = getInt(Op1) > getInt(Op2);
        break;
      case CmpInst::Predicate::ICMP_SLE:
        opResult = getInt(Op1) <= getInt(Op2);
        break;
      case CmpInst::Predicate::ICMP_SLT:
        opResult = getInt(Op1) < getInt(Op2);
        break;
      default:
        knownCase = false;
        break;
      }
    }

    void handlePhiNode()
    {
      PHINode *PHI = dyn_cast<PHINode>(I);
      if (Value *Val = PHI->hasConstantValue())
      {
        knownCase = true;
        opResult = getInt(Val);
      }
    }

    void handleBinaryOp()
    {
      knownCase = true;
      unsigned op_code = I->getOpcode();

      switch (op_code)
      {
      case Instruction::Add:
        opResult = getInt(Op1) + getInt(Op2);
        break;
      case Instruction::Sub:
        opResult = getInt(Op1) - getInt(Op2);
        break;
      case Instruction::Mul:
        opResult = getInt(Op1) * getInt(Op2);
        break;
      case Instruction::FDiv:
        opResult = getInt(Op1) / getInt(Op2);
        break;
      case Instruction::UnaryOps::FNeg:
        opResult = -getInt(Op1);
        break;
      default:
        // If it's not a known case revert the known case
        knownCase = false;
        break;
      }
    }

    // Build our final constant result
    Constant *buildFromResult()
    {
      // If we don't know the case, return nullptr
      if (!knownCase)
        return nullptr;

      // Generate the ConstantInt result
      return ConstantInt::get(I->getType(), APInt(I->getType()->getIntegerBitWidth(), opResult));
    }
  };

  struct ConstFuncPass
  {

    /// Custom Constant Folder for any instruction
    ///
    /// Returns a Constant if it can be folded, and nullptr otherwise
    static Constant *MyConstantFolder(Instruction *I)
    {
      if (!all_of(I->operands(), [](Use &U)
                  { return isa<Constant>(U); }))
        return nullptr;

      ConstantInstruction ConstInst(I);

      // If we have a Comparison Instruction
      if (isa<CmpInst>(I))
      {
        ConstInst.handleCmpInst();
      }
      else if (isa<PHINode>(I))
      {
        ConstInst.handlePhiNode();
      }
      else
      {
        ConstInst.handleBinaryOp();
      }

      // If we don't know the case, return nullptr
      return ConstInst.buildFromResult();
    }

    /// Handle a generic instruction
    ///
    /// return true if we can fold it
    /// return false if we cannot
    static bool handleInstruction(Instruction *I)
    {
      if (Constant *C = ConstFuncPass::MyConstantFolder(I))
      {
        I->replaceAllUsesWith(C);

        return true;
      }
      return false;
    };

    // The main (and most important) function. This is the entry point for
    // your the work your pass will do. The sample here prints the function
    // name, then the function, then the function broken into basic blocks
    // and finally into instructions. All output is to stderr.
    static Constant *runOnFunction(std::map<Function *, Constant *> ConstantFunctions, Function &F)
    {
      std::vector<Instruction *> ToDelete;
      // Iterate over all the instruction
      std::vector<Instruction *> WorkList;
      Constant *Return;
      int returnStmtCount = 0;

      for (inst_iterator I = inst_begin(F), E = inst_end(F); I != E; ++I)
        WorkList.push_back(&*I);

      for (Instruction *I : WorkList)
      {
        // Call instructions need to be checked special becuase we know if functions are constant
        if (CallInst *Call = dyn_cast<CallInst>(I))
        {
          auto Const = ConstantFunctions.find(dyn_cast<Function>(Call->getOperand(0)));

          if (Const != ConstantFunctions.end())
          {
            I->replaceAllUsesWith(Const->second);
          }
        }
        // If it's an instruction that we folded, add the instruction to a list of instructions to delete
        else if (ConstFuncPass::handleInstruction(I))
        {
          if (I->isSafeToRemove())
          {
            ToDelete.push_back(I);
          }
        }
        // Return instructions also need to be special becuase they might indicate a function is a constnat function
        else if (isa<ReturnInst>(I))
        {
          Value *V = I->getOperand(0);
          if (isa<Constant>(V))
          {
            returnStmtCount++;
            Return = dyn_cast<Constant>(V);
          }
        }
      };
      // Delete all the instructions that we flagged
      for (auto I : ToDelete)
      {
        if (I->isSafeToRemove())
        {
          I->removeFromParent();
        }
      }
      // If there is a single return stmt, and it is constant, then we have a constant function
      if (returnStmtCount == 1)
        return Return;

      return nullptr;
    };
  };

  struct ConstModPass : public ModulePass
  {
    static char ID;
    ConstModPass() : ModulePass(ID) {}

    void getAnalysisUsage(AnalysisUsage &AU) const override
    {
      AU.setPreservesCFG();
      AU.addRequired<TargetLibraryInfoWrapperPass>();
    }

    virtual bool runOnModule(Module &M) override
    {
      std::map<Function *, Constant *> ConstantFunctions;
      for (Function &F : M)
      {
        if (Constant *C = ConstFuncPass::runOnFunction(ConstantFunctions, F))
        {
          ConstantFunctions.insert(std::pair<Function *, Constant *>(&F, C));
        }
      }

      return false;
    };
  };
};

// You can change the friendly and long names in RegisterPass to your own pass
// name.
char ConstModPass::ID = 0;
static RegisterPass<ConstModPass> X("constpass", "Constant Propagation/Folding Pass",
                                    false,  /* looks at CFG, true changed CFG */
                                    false); /* analysis pass, true means analysis needs to run again */

// Automatically enable the pass.
// http://adriansampson.net/blog/clangpass.html
static void registerConstPass(const PassManagerBuilder &,
                              legacy::PassManagerBase &PM)
{
  PM.add(new ConstModPass());
};
static RegisterStandardPasses
    RegisterMyPass(PassManagerBuilder::EP_EarlyAsPossible,
                   registerConstPass);
