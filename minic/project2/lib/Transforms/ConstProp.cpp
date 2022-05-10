#include <map>
#include <iostream>

#include "llvm/IR/Function.h"
#include "llvm/Support/raw_ostream.h"

#include "llvm/IR/LegacyPassManager.h"
#include "llvm/Transforms/IPO/PassManagerBuilder.h"

#define PASS_NAME "constprop"

using namespace llvm;

namespace
{
    struct ConstProp : public FunctionPass
    {
        static char ID;
        ConstProp() : FunctionPass(ID) {}

        void runOnInstruction(std::map<std::string, int> *ConstLookup, Instruction *I)
        {
            for (auto op = I->op_begin(); op != I->op_end(); ++op)
            {
                std::cout << "O: " << op << "\n";
            }
        }

        void runOnBlock(BasicBlock &B)
        {
            std::map<std::string, int> Constants;
            for (auto &I : B)
                runOnInstruction(&Constants, &I);
        };

        bool runOnFunction(Function &F) override
        {
            errs() << "Hello: ";
            errs().write_escaped(F.getName()) << '\n';

            for (auto &B : F)
                runOnBlock(B);

            return false;
        }
    };
}

char ConstProp::ID = 0;
static RegisterPass<ConstProp> X(PASS_NAME, "Constant Propagation Pass",
                                 false /* Only looks at CFG */,
                                 false /* Analysis Pass */);

static void registerConstantPropPass(const PassManagerBuilder &,
                                     legacy::PassManagerBase &PM)
{
    PM.add(new ConstProp());
}
static RegisterStandardPasses
    RegisterMyPass(PassManagerBuilder::EP_EarlyAsPossible,
                   registerConstantPropPass);
