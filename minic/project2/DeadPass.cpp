//
// LLVM Function Dead Code Elimination Pass
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
#define DEBUG_TYPE "deadpass"

// Beginning of anonymous namespace. Keeping it anonymous prevents duplicate
// namespaces from occurring, especially when merging code into the LLVM
// pass directory (which we will not be doing.)
namespace
{
    struct DeadPass : public FunctionPass
    {
        static char ID;
        DeadPass() : FunctionPass(ID) {}

        void getAnalysisUsage(AnalysisUsage &AU) const override
        {
            AU.setPreservesCFG();
            AU.addRequired<TargetLibraryInfoWrapperPass>();
        }

        bool getBool(Value *val)
        {
            if (llvm::ConstantInt *CI = dyn_cast<llvm::ConstantInt>(val))
            {
                return CI->getSExtValue();
            }
            return 0;
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

            std::vector<BasicBlock *> Blocks;

            for (BasicBlock &B : F)
            {
                Blocks.push_back(&B);
            }
            int blockNum = 0;
            for (BasicBlock *B : Blocks)
            {
                // Loop over all the basic blocks
                // Remove a basic block if it has no instrutions
                std::vector<Instruction *> Instrs;
                for (auto &I : *B)
                    Instrs.push_back(&I);

                bool canRemove = true;

                for (Instruction *I : Instrs)
                {
                    if (BranchInst *Branch = dyn_cast<BranchInst>(I))
                    {
                        if (Branch->isConditional())
                        {
                            if (Constant *Cond = dyn_cast<Constant>(Branch->getCondition()))
                            {
                                BranchInst *Updated = BranchInst::Create(Branch->getSuccessor(getBool(Cond)));

                                ReplaceInstWithInst(Branch, Updated);
                            }
                        }
                    }
                    else
                        canRemove = false;
                }

                if (B->hasNPredecessors(0) && blockNum > 0)
                {
                    BasicBlock *Suc = B->getSingleSuccessor();
                    for (auto &P : Suc->phis())
                    {
                        P.removeIncomingValue(B);
                    }

                    B->eraseFromParent();
                }

                blockNum++;
            }
            return false; // returning false means the overall CFG has not changed
        };
    };
};

// You can change the friendly and long names in RegisterPass to your own pass
// name.
char DeadPass::ID = 0;
static RegisterPass<DeadPass> X("deadpass", "Dead Code Removal Pass",
                                false,  /* looks at CFG, true changed CFG */
                                false); /* analysis pass, true means analysis needs to run again */

// Automatically enable the pass.
// http://adriansampson.net/blog/clangpass.html
static void registerDeadPass(const PassManagerBuilder &,
                             legacy::PassManagerBase &PM)
{
    PM.add(new DeadPass());
};
static RegisterStandardPasses
    RegisterMyPass(PassManagerBuilder::EP_EarlyAsPossible,
                   registerDeadPass);
